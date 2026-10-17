import time

from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from .stages import FINAL_STAGE, FREEDOM_ENTRANCE, GAME_MINUTES, STAGES

# Session keys. "progress" is the highest stage the team may open:
# 0 = not started, 1..FINAL_STAGE = on that stage, FINAL_STAGE + 1 = escaped.
PROGRESS = "progress"
STARTED_AT = "started_at"
FINISHED_AT = "finished_at"
# The page number whose entrance animation is still to be played.
ENTRANCE = "entrance"


def _progress(request):
    return request.session.get(PROGRESS, 0)


def _take_entrance(request, number):
    """True only on the first view of a page the team has just unlocked."""
    return request.session.pop(ENTRANCE, None) == number


def _unlock(request, number):
    request.session[PROGRESS] = number
    request.session[ENTRANCE] = number


def _resume_url(progress):
    if progress < 1:
        return reverse("intro")
    if progress > FINAL_STAGE:
        return reverse("freedom")
    return reverse("stage", args=[progress])


def _timer_context(request):
    started_at = request.session.get(STARTED_AT)
    if started_at is None:
        return {}
    return {"deadline": started_at + GAME_MINUTES * 60}


def intro(request):
    return render(
        request,
        "game/intro.html",
        {
            "progress": _progress(request),
            "resume_url": _resume_url(_progress(request)),
            "game_minutes": GAME_MINUTES,
        },
    )


@require_POST
def start(request):
    if _progress(request) == 0:
        _unlock(request, 1)
        request.session[STARTED_AT] = int(time.time())
    return redirect(_resume_url(_progress(request)))


@require_http_methods(["GET", "POST"])
def stage(request, number):
    current = STAGES.get(number)
    if current is None:
        raise Http404
    progress = _progress(request)
    if number > progress:
        return redirect(_resume_url(progress))

    solved = number < progress
    error = None
    if request.method == "POST":
        if solved:
            return redirect(_resume_url(progress))
        if current.accepts(request.POST.get("code", "")):
            _unlock(request, number + 1)
            if number == FINAL_STAGE:
                request.session[FINISHED_AT] = int(time.time())
            return redirect(_resume_url(number + 1))
        error = "The lock doesn't budge. Check the Scriptures and try again."

    return render(
        request,
        "game/stage.html",
        {
            "stage": current,
            "solved": solved,
            "error": error,
            "reached": [STAGES[n] for n in STAGES if n <= progress],
            "next_url": _resume_url(number + 1) if solved else None,
            "entrance": current.entrance if _take_entrance(request, number) else None,
            **_timer_context(request),
        },
    )


def freedom(request):
    if _progress(request) <= FINAL_STAGE:
        return redirect(_resume_url(_progress(request)))
    elapsed = request.session.get(FINISHED_AT, 0) - request.session.get(STARTED_AT, 0)
    minutes, seconds = divmod(max(elapsed, 0), 60)
    return render(
        request,
        "game/freedom.html",
        {
            "elapsed": f"{minutes}:{seconds:02d}",
            "reached": [STAGES[n] for n in STAGES],
            "entrance": FREEDOM_ENTRANCE if _take_entrance(request, FINAL_STAGE + 1) else None,
        },
    )


@require_http_methods(["GET", "POST"])
def reset(request):
    """For the Gamemaster: wipe this device's progress between groups."""
    if request.method == "POST":
        request.session.flush()
        return redirect("intro")
    return render(request, "game/reset.html")
