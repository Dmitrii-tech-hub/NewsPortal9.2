from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import BaseRegisterForm
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Category
from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.shortcuts import get_current_site


class NewsListView(ListView):
    model = Post
    template_name = 'news_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.filter(type='NW')  # Filter for news posts
    paginate_by = 10  # Number of posts per page

# News Detail View
class NewsDetailView(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'post'

# News Create View
class NewsCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news_create.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'NW'  # Set post type to News
        post.save()
        return super().form_valid(form)

# News Update View
class NewsUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'NW'  # Ensure the type remains News
        post.save()
        return super().form_valid(form)

# News Delete View
class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'news_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(type='NW')  # Only delete News posts

# Article Create View
class ArticleCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'article_create.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AR'  # Set post type to Article
        post.save()
        return super().form_valid(form)

# Article Update View
class ArticleUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'article_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AR'  # Ensure the type remains Article
        post.save()
        return super().form_valid(form)

# Article Delete View
class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'article_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(type='AR')  # Only delete Article posts

# Search View
class SearchView(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get('title')
        author_name = self.request.GET.get('author')
        after_date = self.request.GET.get('date_after')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author_name:
            queryset = queryset.filter(author__user__username__icontains=author_name)
        if after_date:
            queryset = queryset.filter(created_at__date__gt=after_date)

        return queryset

class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
    return redirect('/')


class MyView(PermissionRequiredMixin, View):
    permission_required = ('simpleapp.add_post', 'simpleapp.change_post')

class CategoryDetailView(View):
    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        return render(request, 'category_detail.html', {'category': category})

    def post(self, request, *args, **kwargs):
        category_id = kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)

        if request.user.is_authenticated:
            # Add the user to category subscribers
            category.subscribers.add(request.user)

            # Prepare and send subscription email
            html_content = render_to_string(
                'subscription_email.html',  # Your email template
                {
                    'user': request.user,
                    'category': category,
                }
            )

            msg = EmailMultiAlternatives(
                subject=f'Подписка на категорию {category.name}',
                body=f'Вы подписались на категорию {category.name}.',
                from_email='peterbadson@yandex.ru',  # Update with your email
                to=[request.user.email],  # Send to the current user
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            # Show a success message
            messages.success(request, f'Вы успешно подписались на категорию {category.name}')

        return redirect('category_detail', category_id=category_id)

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        user = instance
        current_site = get_current_site(None)
        activate_url = f"http://{current_site.domain}{reverse('account_confirm_email')}"
        html_content = render_to_string(
            'welcome_email.html',
            {
                'user': user,
                'activate_url': activate_url
            }
        )
        subject = 'Добро пожаловать на наш сайт, активируйте ваш аккаунт!'
        msg = EmailMultiAlternatives(
            subject=subject,
            body=f'Привет, {user.username}! Пожалуйста, активируйте ваш аккаунт.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class AccountConfirmView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')

        # Проверяем, существует ли такой пользователь
        user = get_object_or_404(User, pk=user_id)

        # Активируем пользователя
        user.is_active = True
        user.save()

        # Отправляем сообщение об успешной активации
        messages.success(request, f'Аккаунт {user.username} успешно активирован!')

        # Перенаправляем на страницу логина или главную страницу
        return redirect('login')
