from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # 1. Суммарный рейтинг каждой статьи автора умножается на 3
        post_rating = Post.objects.filter(author=self).aggregate(Sum('rating'))['rating__sum'] or 0
        post_rating *= 3

        # 2. Суммарный рейтинг всех комментариев автора
        comment_rating = Comment.objects.filter(user=self.user).aggregate(Sum('rating'))['rating__sum'] or 0

        # 3. Суммарный рейтинг всех комментариев к статьям автора
        post_comments_rating = Comment.objects.filter(post__author=self).aggregate(Sum('rating'))['rating__sum'] or 0

        # Итоговый рейтинг
        self.rating = post_rating + comment_rating + post_comments_rating
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, name='subscribed_categories', blank=True)

class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=POST_TYPES, default=ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField(default=0)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Send email to all subscribers
        subscribers = self.category.subscribers.all()
        for subscriber in subscribers:
            # Prepare email content
            html_content = render_to_string(
                'new_post_email.html',  # Create this template
                {
                    'user': subscriber,
                    'title': self.title,
                    'preview': self.content[:50],  # First 50 characters
                    'category': self.category,
                }
            )

            # Email setup
            msg = EmailMultiAlternatives(
                subject=self.title,
                body=self.content[:50],
                from_email='dmitrij.croitoru@yandex.com',
                to=[subscriber.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.content[:124] + '...' if len(self.content) > 124 else self.content

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # Текст комментария
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время создания
    rating = models.IntegerField(default=0)  # Рейтинг комментария

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

