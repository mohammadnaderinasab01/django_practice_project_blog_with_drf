from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from users.models import User


class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = GenericRelation('Comment')

    def __str__(self):
        return self.title


class BlogVote(models.Model):
    VOTE_TYPE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=VOTE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'user')  # Ensure a user can only vote once per blog

    def __str__(self):
        return f"{self.user} voted {self.vote_type} on {self.blog}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    replies = GenericRelation('Comment')

    def __str__(self):
        return (self.description[:50] + '...') if len(self.description) > 50 else self.description
