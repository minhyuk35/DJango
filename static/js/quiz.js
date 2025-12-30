"use strict";
const getAnswerIndex = (el) => {
    const raw = el.getAttribute("data-answer");
    if (!raw)
        return null;
    const n = Number.parseInt(raw, 10);
    return Number.isFinite(n) ? n : null;
};
const grade = (root) => {
    const questions = root.querySelectorAll(".quiz-q");
    questions.forEach((q) => {
        const answer = getAnswerIndex(q);
        const msg = q.querySelector(".quiz-msg");
        const checked = q.querySelector("input[type=radio]:checked");
        const chosen = checked ? Number.parseInt(checked.value, 10) : NaN;
        q.classList.remove("is-correct", "is-wrong", "is-missing");
        q.querySelectorAll(".quiz-choice").forEach((c) => c.classList.remove("is-correct", "is-wrong"));
        if (!checked || answer === null || !Number.isFinite(chosen)) {
            q.classList.add("is-missing");
            if (msg)
                msg.textContent = "선택하지 않았어요.";
            return;
        }
        const choices = q.querySelectorAll(".quiz-choice");
        const chosenWrap = choices[chosen];
        const answerWrap = choices[answer];
        if (answerWrap)
            answerWrap.classList.add("is-correct");
        if (chosen === answer) {
            q.classList.add("is-correct");
            if (msg)
                msg.textContent = "정답!";
        }
        else {
            q.classList.add("is-wrong");
            if (chosenWrap)
                chosenWrap.classList.add("is-wrong");
            if (msg)
                msg.textContent = "오답. 정답을 표시했어요.";
        }
    });
};
(() => {
    const roots = document.querySelectorAll("[data-quiz]");
    if (!roots.length)
        return;
    roots.forEach((root) => {
        const btn = root.querySelector("[data-quiz-grade]");
        btn === null || btn === void 0 ? void 0 : btn.addEventListener("click", () => grade(root));
    });
})();

