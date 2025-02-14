from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # user = User(**validated_data)
        # user.set_password(validated_data['password'])
        # user.save()
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    token = serializers.SerializerMethodField()

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        tokens = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return tokens


class UserSignupSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'password']


class UserLoginSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'password']


class UserUpdatePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255)
    confirm_password = serializers.CharField(max_length=255)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('password should not be less than 8 characters')

        if value.isdigit():
            raise serializers.ValidationError('password should not be just numeric')

        return value

    def validate_confirm_password(self, value):
        if self.initial_data.get('password') != value:
            raise serializers.ValidationError('password and confirm password are not the same')
        return value


class UserUpdateInfoSerializerRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'id', 'phone_number']
        read_only_fields = ['id', 'phone_number']
