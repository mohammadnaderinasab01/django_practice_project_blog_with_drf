from rest_framework import serializers
from .models import Blog, Comment
from users.models import User
from rest_framework.pagination import PageNumberPagination
from users.serializers import UserSerializer
from django.conf import settings


class AuthorSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BlogSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = '__all__'

    def get_total_votes(self, obj):
        try:
            return obj.total_votes
        except:
            try:
                return obj.votes.filter(vote_type='up').count() - obj.votes.filter(vote_type='down').count()
            except:
                return None


class BlogCreateUpdateSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        blog = Blog.objects.create(**validated_data)
        return blog


class BlogVoteRequestSerializer(serializers.Serializer):
    vote_type = serializers.ChoiceField(choices=['up', 'down'])


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    related_object = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        exclude = ('object_id', 'content_type')

    def get_related_object(self, obj):
        try:
            return obj.content_object.__class__.__name__
        except:
            return None


class CommentCreateSerializer(serializers.ModelSerializer):
    related_id = serializers.IntegerField(write_only=True)
    source_type = serializers.ChoiceField(write_only=True, choices=['blog', 'comment'])

    class Meta:
        model = Comment
        fields = ['description', 'related_id', 'source_type']

    def validate(self, data):
        """
        Validate that related_id belongs to either a Blog or a Comment.
        """
        related_id = data.get('related_id')
        source_type = data.get('source_type')

        if not related_id:
            raise serializers.ValidationError("related_id is required.")

        # if source_type != "blog" and source_type != "comment":
        #     raise serializers.ValidationError(f"use blog or comment for it")

        if source_type == "blog" and not Blog.objects.filter(id=related_id).exists():
            raise serializers.ValidationError(f"No Blog found with id {related_id}.")

        elif source_type == "comment" and not Comment.objects.filter(id=related_id).exists():
            raise serializers.ValidationError(f"No Comment found with id {related_id}.")

        # Determine the model class and add content_object to the validated data
        if source_type == 'blog':
            data['content_object'] = Blog.objects.get(id=related_id)
        elif source_type == 'comment':
            data['content_object'] = Comment.objects.get(id=related_id)

        data.pop('related_id', None)
        data.pop('source_type', None)

        return data

    def create(self, validated_data):
        """
        Create a Comment instance using content_object.
        """
        print('validated: ', validated_data)
        user = self.context['request'].user
        validated_data['author'] = user
        # content_object = validated_data.pop('content_object')
        # validated_data['content_type'] = ContentType.objects.get_for_model(content_object)
        # validated_data['object_id'] = content_object.id
        return super().create(validated_data)


class BlogDetailSerializer(BlogSerializer):
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        request = self.context.get('request')

        paginator = PageNumberPagination()
        paginator.page_query_param = 'comments_page'
        comments_queryset = obj.comments.all()

        page = paginator.paginate_queryset(comments_queryset, request, view=self.context.get('view'))

        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data).data

        serializer = CommentSerializer(comments_queryset, many=True)
        return serializer.data
