from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Iterable

from django.utils.html import strip_tags


_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "is",
    "are",
    "it",
    "this",
    "that",
    "for",
    "with",
    "as",
    "on",
    "at",
    "by",
    "from",
    "we",
    "you",
    "i",
    "be",
    "can",
    "will",
    "not",
    "있다",
    "없는",
    "한다",
    "하기",
    "대한",
    "그리고",
    "또는",
    "에서",
    "으로",
    "하면",
    "합니다",
    "있어요",
    "정리",
}


def _tokens(text: str) -> list[str]:
    plain = strip_tags(text or "")
    raw = re.split(r"[^0-9A-Za-z가-힣]+", plain.lower())
    toks = [t for t in raw if len(t) >= 2 and t not in _STOPWORDS]
    return toks


def _sentences(text: str) -> list[str]:
    plain = strip_tags(text or "")
    parts = re.split(r"(?:[\.!\?]\s+|\n+)", plain)
    return [p.strip() for p in parts if len(p.strip()) >= 12]


@dataclass(frozen=True)
class GeneratedQuestion:
    prompt: str
    choices: list[str]
    answer_index: int


def generate_quiz(title: str, content: str, category_names: Iterable[str]) -> list[GeneratedQuestion]:
    toks = _tokens(title + " " + content)
    if not toks:
        return []

    keyword = toks[0]
    categories = [c for c in category_names if c] or ["기타"]
    categories = list(dict.fromkeys(categories))

    questions: list[GeneratedQuestion] = []

    if len(categories) >= 2:
        options = categories[:4]
        correct = options[0]
        random.shuffle(options)
        questions.append(
            GeneratedQuestion(
                prompt=f"'{keyword}'와 가장 관련이 깊은 카테고리는?",
                choices=options,
                answer_index=options.index(correct),
            )
        )

    sents = _sentences(content)
    if sents:
        correct_sent = None
        for s in sents:
            if keyword.lower() in s.lower():
                correct_sent = s
                break
        correct_sent = correct_sent or sents[0]

        distractors = [s for s in sents if s != correct_sent]
        random.shuffle(distractors)
        options = [correct_sent] + distractors[:3]
        options = [o[:120] + ("…" if len(o) > 120 else "") for o in options]
        random.shuffle(options)
        questions.append(
            GeneratedQuestion(
                prompt=f"다음 중 '{keyword}'에 대한 설명으로 가장 알맞은 것은?",
                choices=options,
                answer_index=options.index(correct_sent[:120] + ("…" if len(correct_sent) > 120 else "")),
            )
        )

    # Keyword pick
    uniq = list(dict.fromkeys(toks))[:12]
    if len(uniq) >= 4:
        correct = uniq[0]
        options = [correct] + uniq[1:4]
        random.shuffle(options)
        questions.append(
            GeneratedQuestion(
                prompt="이 글의 핵심 키워드로 가장 적절한 것은?",
                choices=options,
                answer_index=options.index(correct),
            )
        )

    if not questions:
        correct = keyword
        pool = [correct] + categories[:3] + ["개요", "정리", "예제", "기초", "핵심"]
        options: list[str] = []
        for p in pool:
            if p and p not in options:
                options.append(p)
            if len(options) >= 4:
                break
        while len(options) < 4:
            options.append(f"선택지 {len(options) + 1}")
        random.shuffle(options)
        questions.append(
            GeneratedQuestion(
                prompt="다음 중 이 글/노트의 키워드로 가장 알맞은 것은?",
                choices=options[:4],
                answer_index=options[:4].index(correct) if correct in options[:4] else 0,
            )
        )

    return questions[:5]
