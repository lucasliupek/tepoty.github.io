from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from embed_video.fields import EmbedVideoField

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.BigIntegerField()
    last_updated = models.DateTimeField(default=timezone.now)

    @classmethod
    def create(cls, user):
        book = cls(user=user, balance=0, last_updated=timezone.now())
        # do something with the book
        return book


class ContentItem(models.Model):
    contentcreator = models.ForeignKey(User, on_delete=models.CASCADE)
    yt_video_code = models.TextField(max_length=400)
    item_price = models.BigIntegerField(default=0)
    
STATUS_LIST = (
    ('A', 'Approved'),
    ('P', 'Pending'),
    ('D', 'Denied'),
)

class Transactions(models.Model):
    user_from = models.ForeignKey(User, related_name='user_from', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='user_to', on_delete=models.CASCADE)
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    operation_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=1, choices=STATUS_LIST, default='P')

class CreditAquisition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    status = models.CharField(max_length=1, choices=STATUS_LIST, default='P')
    operation_date = models.DateTimeField(default=timezone.now)

class Post(models.Model):
    content = models.TextField(max_length=150)
    content_item = models.ForeignKey(ContentItem, blank=True, null=True, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content[:5]

    @property
    def number_of_comments(self):
        return Comment.objects.filter(post_connected=self).count()

class Comment(models.Model):
    content = models.TextField(max_length=150)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_connected = models.ForeignKey(Post, on_delete=models.CASCADE)
