from django_filters import FilterSet, DateFilter
from django import forms
from .models import Post

class PostFilter(FilterSet):
    created_at = DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Дата позже',
        widget=forms.DateInput(attrs={'type': 'date'})  # Set the type to "date"
    )

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],  # Search by title
            'author__user__username': ['icontains'],  # Search by author's username
            'created_at': ['gte'],  # Filter by creation date
        }
