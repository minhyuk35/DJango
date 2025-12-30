from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from blog.models import Post
from notes.models import Note

from .models import Quiz, QuizQuestion
from .quizgen import generate_quiz


def _ensure_quiz_for(instance):
    content_type = ContentType.objects.get_for_model(instance.__class__)
    quiz, created = Quiz.objects.get_or_create(
        content_type=content_type,
        object_id=instance.pk,
        defaults={"title": instance.title},
    )
    if not created:
        return

    categories = []
    if hasattr(instance, "categories"):
        categories = list(instance.categories.values_list("name", flat=True))

    generated = generate_quiz(instance.title, getattr(instance, "content", ""), categories)
    for q in generated:
        QuizQuestion.objects.create(
            quiz=quiz,
            prompt=q.prompt,
            choices=q.choices,
            answer_index=q.answer_index,
        )


@receiver(post_save, sender=Post)
def on_post_saved(sender, instance: Post, created: bool, **kwargs):
    if created:
        _ensure_quiz_for(instance)


@receiver(post_save, sender=Note)
def on_note_saved(sender, instance: Note, created: bool, **kwargs):
    if created:
        _ensure_quiz_for(instance)

