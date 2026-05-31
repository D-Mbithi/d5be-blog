from django import forms

from .models import Category, Comment, Recipe


class PostForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            "title",
            "description",
            "instructions",
            "category",
            "prep_time",
            "cook_time",
            "servings",
            "difficulty",
            "status",
            "featured_image",
            "tags",
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
