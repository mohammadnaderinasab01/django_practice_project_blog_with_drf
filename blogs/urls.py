from .views import BlogViewSet, BlogVoteView, \
    CommentViewSet, MostPopularBlogsView, \
    BlogDetailView, BlogCommentsView
from django.urls import path, include
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r"blogs", BlogViewSet)
router.register(r"comments", CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('vote/<int:pk>/', BlogVoteView.as_view()),
    path('most-popular-blogs', MostPopularBlogsView.as_view()),
    path('blog-detail/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('<int:pk>/comments/', BlogCommentsView.as_view(), name='blog_comments'),
]
