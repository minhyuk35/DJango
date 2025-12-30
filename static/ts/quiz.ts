type QuizRoot = HTMLElement & { dataset: { quiz?: string } };

const getAnswerIndex = (el: HTMLElement): number | null => {
  const raw = el.getAttribute("data-answer");
  if (!raw) return null;
  const n = Number.parseInt(raw, 10);
  return Number.isFinite(n) ? n : null;
};

const grade = (root: HTMLElement) => {
  const questions = root.querySelectorAll<HTMLElement>(".quiz-q");
  questions.forEach((q) => {
    const answer = getAnswerIndex(q);
    const msg = q.querySelector<HTMLElement>(".quiz-msg");
    const checked = q.querySelector<HTMLInputElement>("input[type=radio]:checked");
    const chosen = checked ? Number.parseInt(checked.value, 10) : NaN;

    q.classList.remove("is-correct", "is-wrong", "is-missing");
    q.querySelectorAll<HTMLElement>(".quiz-choice").forEach((c) => c.classList.remove("is-correct", "is-wrong"));

    if (!checked || answer === null || !Number.isFinite(chosen)) {
      q.classList.add("is-missing");
      if (msg) msg.textContent = "선택하지 않았어요.";
      return;
    }

    const choices = q.querySelectorAll<HTMLElement>(".quiz-choice");
    const chosenWrap = choices[chosen];
    const answerWrap = choices[answer];

    if (answerWrap) answerWrap.classList.add("is-correct");
    if (chosen === answer) {
      q.classList.add("is-correct");
      if (msg) msg.textContent = "정답!";
    } else {
      q.classList.add("is-wrong");
      if (chosenWrap) chosenWrap.classList.add("is-wrong");
      if (msg) msg.textContent = "오답. 정답을 표시했어요.";
    }
  });
};

(() => {
  const roots = document.querySelectorAll<QuizRoot>("[data-quiz]");
  if (!roots.length) return;
  roots.forEach((root) => {
    const btn = root.querySelector<HTMLButtonElement>("[data-quiz-grade]");
    btn?.addEventListener("click", () => grade(root));
  });
})();

