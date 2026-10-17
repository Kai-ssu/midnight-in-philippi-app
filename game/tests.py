from django.test import SimpleTestCase
from django.urls import reverse

from .stages import normalize


class NormalizeTests(SimpleTestCase):
    def test_ignores_case_spaces_and_dashes(self):
        self.assertEqual(normalize(" j-p m-h "), "JPMH")
        self.assertEqual(normalize("2-8-4"), "284")


class GameFlowTests(SimpleTestCase):
    def start(self):
        return self.client.post(reverse("start"))

    def submit(self, stage, code):
        return self.client.post(reverse("stage", args=[stage]), {"code": code})

    def test_intro_renders(self):
        response = self.client.get(reverse("intro"))
        self.assertContains(response, "Begin")

    def test_stages_locked_before_start(self):
        response = self.client.get(reverse("stage", args=[1]))
        self.assertRedirects(response, reverse("intro"))

    def test_start_opens_stage_one(self):
        response = self.start()
        self.assertRedirects(response, reverse("stage", args=[1]))
        self.assertContains(self.client.get(reverse("stage", args=[1])), "The Accusation")

    def test_wrong_code_stays_on_stage(self):
        self.start()
        response = self.submit(1, "123")
        self.assertContains(response, "Check the Scriptures and try again")
        self.assertRedirects(self.client.get(reverse("stage", args=[2])), reverse("stage", args=[1]))

    def test_cannot_skip_ahead(self):
        self.start()
        response = self.submit(3, "16425")
        self.assertRedirects(response, reverse("stage", args=[1]))

    def test_full_playthrough(self):
        self.start()
        self.assertRedirects(self.submit(1, "2-8-4"), reverse("stage", args=[2]))
        self.assertRedirects(self.submit(2, "j p m h"), reverse("stage", args=[3]))
        self.assertRedirects(self.submit(3, "1-6-4-2-5"), reverse("stage", args=[4]))
        self.assertRedirects(self.submit(4, "7302"), reverse("freedom"))
        self.assertContains(self.client.get(reverse("freedom")), "You escaped in")

    def test_word_lock_alternative(self):
        self.start()
        self.submit(1, "284")
        self.assertRedirects(self.submit(2, "SONG"), reverse("stage", args=[3]))

    def test_solved_stage_can_be_revisited(self):
        self.start()
        self.submit(1, "284")
        self.assertContains(self.client.get(reverse("stage", args=[1])), "Unlocked")

    def test_freedom_locked_until_finished(self):
        self.start()
        self.assertRedirects(self.client.get(reverse("freedom")), reverse("stage", args=[1]))

    def test_answers_not_in_page(self):
        self.start()
        self.assertNotContains(self.client.get(reverse("stage", args=[1])), "284")

    def test_entrance_plays_once_after_unlock(self):
        self.start()
        self.assertContains(self.client.get(reverse("stage", args=[1])), "entrance--dark")
        self.assertNotContains(self.client.get(reverse("stage", args=[1])), 'class="entrance')
        self.submit(1, "284")
        self.assertContains(self.client.get(reverse("stage", args=[2])), "entrance--songs")
        self.assertNotContains(self.client.get(reverse("stage", args=[1])), 'class="entrance')
        self.assertNotContains(self.client.get(reverse("stage", args=[2])), 'class="entrance')

    def test_entrance_on_freedom(self):
        self.start()
        for stage, code in [(1, "284"), (2, "JPMH"), (3, "16425"), (4, "7302")]:
            self.submit(stage, code)
        response = self.client.get(reverse("freedom"))
        self.assertContains(response, "entrance--doors")
        self.assertContains(response, f'action="{reverse("reset")}"')
        self.assertNotContains(self.client.get(reverse("freedom")), 'class="entrance')

    def test_reset_clears_progress(self):
        self.start()
        self.submit(1, "284")
        self.client.post(reverse("reset"))
        self.assertRedirects(self.client.get(reverse("stage", args=[1])), reverse("intro"))

    def test_unknown_stage_404(self):
        self.start()
        self.assertEqual(self.client.get(reverse("stage", args=[9])).status_code, 404)
