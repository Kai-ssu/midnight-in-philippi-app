// Countdown timer: the deadline (unix seconds) comes from the server.
const timer = document.querySelector(".timer");
if (timer) {
  const deadline = Number(timer.dataset.deadline) * 1000;
  const tick = () => {
    const left = Math.max(0, Math.round((deadline - Date.now()) / 1000));
    const m = Math.floor(left / 60);
    const s = String(left % 60).padStart(2, "0");
    timer.textContent = left > 0 ? `${m}:${s}` : "Time's up";
    timer.classList.toggle("low", left < 5 * 60);
  };
  tick();
  setInterval(tick, 1000);
}

// Unlock scene: tap anywhere to skip; remove it once it has faded out.
const entrance = document.querySelector(".entrance");
if (entrance) {
  const finish = () => entrance.remove();
  entrance.addEventListener("click", finish);
  entrance.addEventListener("animationend", (event) => {
    if (event.animationName === "entrance-out") finish();
  });
}

// Ask before submitting forms that wipe progress.
document.querySelectorAll("form[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});

// Stage 3: tap a strip to turn it over.
document.querySelectorAll(".strip").forEach((strip) => {
  strip.addEventListener("click", () => strip.classList.toggle("flipped"));
});
