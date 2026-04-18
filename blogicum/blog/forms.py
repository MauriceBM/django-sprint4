from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from blog.models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикаций."""

    class Meta:
        model = Post
        fields = [
            'title', 'text', 'pub_date',
            'location', 'category', 'image'
        ]
        widgets = {
            'text': forms.Textarea(attrs={'rows': 10}),
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            ),
        }

    def __init__(self, *args, **kwargs):
        data = kwargs.get('data')
        if args:
            data = args[0]
        if isinstance(data, dict) and data.get('pub_date') is None:
            data['pub_date'] = ''
        super().__init__(*args, **kwargs)

    def clean_pub_date(self):
        """Возвращает дату, сохраняя старую при редактировании."""
        data = self.cleaned_data.get('pub_date')
        if not data:
            if self.instance.pk:
                return self.instance.pub_date or timezone.now()
            return timezone.now()
        return data


class CommentForm(forms.ModelForm):
    """Форма для добавления и редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }


class ProfileEditForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя."""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
