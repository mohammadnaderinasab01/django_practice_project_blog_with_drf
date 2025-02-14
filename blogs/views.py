from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import BlogSerializer, BlogCreateUpdateSerializer, \
    BlogVoteRequestSerializer, CommentSerializer, \
    CommentCreateSerializer, BlogDetailSerializer
from .models import Blog, Comment, BlogVote
from users.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Count, Q
from rest_framework import generics
from utils.permissions import HasAuthorAccessBlog, HasAuthorAccessComment
import time
from rest_framework.exceptions import NotFound


class BlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()
    http_method_names = ['get', 'post', 'delete', 'put']

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, HasAuthorAccessBlog]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'PATCH':
            return BlogCreateUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == 'list':
            query = self.request.query_params.get('q', '')
            return Blog.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return super().get_queryset()

    @extend_schema(
        parameters=[
            OpenApiParameter(name='q', type=str, description='search query', required=False),
        ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class BlogVoteView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            blog_vote = BlogVote.objects.get(blog__id=pk, user__id=request.user.id)
            blog_vote.delete()
            return Response(f'Your Vote for blog with id: {pk} has been successfully deleted')
        except BlogVote.DoesNotExist:
            return Response(f"No vote found with blog id: {pk} for the user", status=status.HTTP_404_NOT_FOUND)

    @extend_schema(request=BlogVoteRequestSerializer)
    def post(self, request, pk, *args, **kwargs):

        start_time = time.time()

        serializer = BlogVoteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response("Invalid request data.", status=status.HTTP_400_BAD_REQUEST)

        try:
            blog = Blog.objects.get(id=pk)
            user = request.user
            vote_type = serializer.validated_data['vote_type']

            # Check if the user has already voted
            vote, created = BlogVote.objects.get_or_create(
                blog=blog,
                user=user,
                defaults={'vote_type': vote_type},
            )

            if created:
                message = f"{vote_type.capitalize()} vote successful."
            else:
                # If the vote type hasn't changed, do nothing
                if vote.vote_type == vote_type:
                    end_time = time.time()
                    print(f"Query executed in {end_time - start_time:.4f} seconds")
                    return Response("You've already voted on this blog.", status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Update the vote type
                    vote.vote_type = vote_type
                    vote.save()
                    message = f"Vote updated to {vote_type}."

            end_time = time.time()
            print(f"Query executed in {end_time - start_time:.4f} seconds")
            return Response(message, status=status.HTTP_200_OK)

        except Blog.DoesNotExist:
            return Response(f"No blog found with id: {pk}", status=status.HTTP_404_NOT_FOUND)


class MostPopularBlogsView(generics.ListAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        start_time = time.time()
        queryset = Blog.objects.annotate(
            total_votes=Count('votes', filter=Q(votes__vote_type='up')) -
            Count('votes', filter=Q(votes__vote_type='down'))
        ).order_by('-total_votes')
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return super().get_serializer_class()

    @property
    def allowed_methods(self):
        return [method for method in super().allowed_methods if method not in ['PUT', 'PATCH']]


class BlogDetailView(generics.RetrieveAPIView):
    serializer_class = BlogDetailSerializer
    queryset = Blog.objects.prefetch_related('comments', 'comments__author')

    @extend_schema(
        parameters=[
            OpenApiParameter(name='comments_page', type=int, description='Page number for pagination', required=False),
        ],
        responses=BlogDetailSerializer
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BlogCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        try:
            queryset = Blog.objects.get(id=self.kwargs.get('pk')).comments.all()
            return queryset
        except Blog.DoesNotExist:
            raise NotFound(f"No blog found with id: {self.kwargs.get('pk')}")
