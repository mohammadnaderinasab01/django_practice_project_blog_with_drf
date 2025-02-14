from rest_framework.permissions import BasePermission
from blogs.models import Blog, Comment, BlogVote


class HasAuthorAccessBlog(BasePermission):
    def has_permission(self, request, view):
        blog_id = view.kwargs.get('pk')
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return True
        return request.user.id == blog.author.id


class HasAuthorAccessComment(BasePermission):
    def has_permission(self, request, view):
        comment_id = view.kwargs.get('pk')
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return True
        return request.user.id == comment.author.id
