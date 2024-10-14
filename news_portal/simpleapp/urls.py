from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    BaseRegisterView,
    NewsListView,
    NewsDetailView,
    NewsCreateView,
    ArticleCreateView,
    NewsUpdateView,
    ArticleUpdateView,
    NewsDeleteView,
    ArticleDeleteView,
    SearchView,
    IndexView,
    upgrade_me,
    CategoryDetailView,
    AccountConfirmView,
)

urlpatterns = [
    path('news/', NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('news/create/', NewsCreateView.as_view(), name='news_create'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('news/<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),
    path('news/search/', SearchView.as_view(), name='news_search'),
    path('', IndexView.as_view(), name='index'),
    path('upgrade/', upgrade_me, name='upgrade_to_premium'),
    path('category/<int:category_id>/', CategoryDetailView.as_view(), name='category_detail'),
    path('account/confirm/', AccountConfirmView.as_view(), name='account_confirm_email'),
    path('accounts/login/',
         LoginView.as_view(template_name='login.html'),
         name='login'),
    path('accounts/logout/',
         LogoutView.as_view(template_name='logout.html'),
         name='logout'),
    path('accounts/signup/',
         BaseRegisterView.as_view(template_name='signup.html'),
         name='signup'),
]


