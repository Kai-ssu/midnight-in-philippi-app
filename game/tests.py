from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from .stages import STAGES, normalize


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

    def test_old_word_lock_answer_is_rejected(self):
        self.start()
        self.submit(1, "284")
        self.assertContains(self.submit(2, "SONG"), "Check the Scriptures and try again")

    def test_full_playthrough(self):
        self.start()
        self.assertRedirects(self.submit(1, "2-8-4"), reverse("stage", args=[2]))
        self.assertRedirects(self.submit(2, "j p m h"), reverse("stage", args=[3]))
        self.assertRedirects(self.submit(3, "1-6-4-2-5"), reverse("stage", args=[4]))
        self.assertRedirects(self.submit(4, "7302"), reverse("freedom"))
        self.assertContains(self.client.get(reverse("freedom")), "You escaped in")

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

    def test_landing_offers_three_roles(self):
        response = self.client.get(reverse("landing"))
        for url in [reverse("intro"), reverse("facilitator"), reverse("about")]:
            self.assertContains(response, f'href="{url}"')

    def test_leader_and_about_pages_render(self):
        self.assertContains(self.client.get(reverse("facilitator")), "<svg")
        self.assertContains(self.client.get(reverse("about")), "Kye Laurel")

    def test_leader_page_shows_no_answers(self):
        response = self.client.get(reverse("facilitator"))
        for stage in STAGES.values():
            for answer in stage.answers:
                self.assertNotContains(response, answer)

    def test_backdrop_has_join_qr_and_debrief_link(self):
        response = self.client.get(reverse("backdrop"))
        self.assertContains(response, "<svg")
        self.assertContains(response, "testserver/play")
        self.assertContains(response, f'href="{reverse("debrief")}"')

    def test_backdrop_needs_no_game(self):
        response = self.client.get(reverse("backdrop"))
        self.assertContains(response, 'id="clock"')
        self.assertNotIn("progress", self.client.session)

    def test_debrief_shows_questions_only(self):
        response = self.client.get(reverse("debrief"))
        for title in ["Praise in the Dark", "Mercy Over Self-Preservation", "The Domino Effect of Faith"]:
            self.assertContains(response, title)
        self.assertNotContains(response, "Facilitator Focus")

    def test_stage_three_has_strips_for_each_bible(self):
        self.start()
        self.submit(1, "284")
        self.submit(2, "JPMH")
        response = self.client.get(reverse("stage", args=[3]))
        self.assertContains(response, 'data-bible="niv"')
        self.assertContains(response, 'data-bible="nkjv"')
        self.assertContains(response, "NO HARM")
        self.assertNotContains(response, "{#")  # no leaked template comments

    def test_every_stage_has_the_bible_switch(self):
        self.start()
        for stage, code in [(1, "284"), (2, "JPMH"), (3, "16425"), (4, None)]:
            response = self.client.get(reverse("stage", args=[stage]))
            self.assertContains(response, 'data-bible-pick="nkjv"')
            if code:
                self.submit(stage, code)
        self.assertContains(self.client.get(reverse("intro")), 'data-bible-pick="nkjv"')

    @override_settings(LEADER_CODE="open sesame")
    def test_answer_key_needs_the_passcode(self):
        url = reverse("answers")
        locked = self.client.get(url)
        self.assertContains(locked, 'name="passcode"')
        self.assertNotContains(locked, "2-8-4")

        wrong = self.client.post(url, {"passcode": "guess"})
        self.assertContains(wrong, "That passcode")
        self.assertNotContains(wrong, "2-8-4")

        self.client.post(url, {"passcode": "open sesame"})
        unlocked = self.client.get(url)
        for code in ["2-8-4", "J-P-M-H", "1-6-4-2-5", "7-3-0-2"]:
            self.assertContains(unlocked, code)

        self.client.post(url, {"action": "lock"})
        self.assertNotContains(self.client.get(url), "2-8-4")

    def test_new_passcode_locks_unlocked_devices(self):
        with override_settings(LEADER_CODE="old code"):
            self.client.post(reverse("answers"), {"passcode": "old code"})
            self.assertContains(self.client.get(reverse("answers")), "2-8-4")
        with override_settings(LEADER_CODE="new code"):
            self.assertNotContains(self.client.get(reverse("answers")), "2-8-4")

    @override_settings(LEADER_CODE="")
    def test_answer_key_stays_locked_without_a_passcode(self):
        response = self.client.post(reverse("answers"), {"passcode": ""})
        self.assertNotContains(response, "2-8-4")
        self.assertContains(self.client.get(reverse("answers")), "LEADER_CODE")

    def test_story_page_and_backdrop_link(self):
        self.assertContains(self.client.get(reverse("story")), 'id="caption"')
        self.assertContains(self.client.get(reverse("backdrop")), f'href="{reverse("story")}"')

    def test_unknown_stage_404(self):
        self.start()
        self.assertEqual(self.client.get(reverse("stage", args=[9])).status_code, 404)
