from django import forms

from .models import Category, Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "body",
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "name",
        ]

class EmailPostForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4}),
        }
