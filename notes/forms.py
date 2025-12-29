from django import forms

from .models import Category, Note


class NoteForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.order_by("name"),
        required=False,
        widget=forms.MultipleHiddenInput(),
        label="카테고리",
    )

    class Meta:
        model = Note
        fields = ["title", "content", "categories"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "제목",
                    "autocomplete": "off",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 12,
                    "style": "display:none;",
                }
            ),
        }
