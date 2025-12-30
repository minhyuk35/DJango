from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import Post
from notes.models import Note

from learning.models import Quiz, QuizQuestion
from learning.quizgen import generate_quiz


class Command(BaseCommand):
    help = "Create quizzes for existing posts/notes that don't have one yet."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate quizzes even if already exists (will delete existing questions).",
        )

    def handle(self, *args, **options):
        force: bool = bool(options["force"])

        post_ct = ContentType.objects.get_for_model(Post)
        note_ct = ContentType.objects.get_for_model(Note)

        created_quizzes = 0
        updated_quizzes = 0
        deleted_questions = 0
        created_questions = 0

        def ensure_for(obj, ct: ContentType):
            nonlocal created_quizzes, updated_quizzes, deleted_questions, created_questions

            quiz, created = Quiz.objects.get_or_create(
                content_type=ct,
                object_id=obj.pk,
                defaults={"title": obj.title},
            )
            if created:
                created_quizzes += 1
            else:
                if quiz.title != obj.title:
                    quiz.title = obj.title
                    quiz.save(update_fields=["title"])
                    updated_quizzes += 1

            has_questions = quiz.questions.exists()
            if not created and not force and has_questions:
                return

            if force and not created:
                deleted_questions += quiz.questions.count()
                QuizQuestion.objects.filter(quiz=quiz).delete()

            categories = []
            if hasattr(obj, "categories"):
                categories = list(obj.categories.values_list("name", flat=True))

            generated = generate_quiz(obj.title, getattr(obj, "content", ""), categories)
            for q in generated:
                QuizQuestion.objects.create(
                    quiz=quiz,
                    prompt=q.prompt,
                    choices=q.choices,
                    answer_index=q.answer_index,
                )
                created_questions += 1

        for p in Post.objects.all().prefetch_related("categories"):
            ensure_for(p, post_ct)

        for n in Note.objects.all().prefetch_related("categories"):
            ensure_for(n, note_ct)

        self.stdout.write(
            self.style.SUCCESS(
                "Done. "
                f"quizzes_created={created_quizzes} "
                f"quizzes_updated={updated_quizzes} "
                f"questions_deleted={deleted_questions} "
                f"questions_created={created_questions}"
            )
        )
