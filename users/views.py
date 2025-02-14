from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import UserSerializer, UserLoginSerializer, UserSignupSerializerRequest, UserUpdateInfoSerializerRequest, UserLoginSerializerRequest, UserUpdatePasswordSerializer
from drf_spectacular.utils import extend_schema
from .models import User
from django.utils.timezone import now


class LoginView(APIView):
    serializer_class = UserLoginSerializerRequest
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        request=UserLoginSerializerRequest
    )
    def post(self, request):
        username = request.data.get('phone_number', None)
        password = request.data.get('password', None)

        authenticated_user = authenticate(username=username, password=password)

        if authenticated_user:
            authenticated_user.last_login = now()
            authenticated_user.save(update_fields=['last_login'])
            serializer = UserLoginSerializer(authenticated_user)
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_200_OK,
                    'message': 'شما با موفقیت وارد شدید'
                }],
                'result': serializer.data,
                'resultStatus': 0
            }, status=status.HTTP_200_OK)
        return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_401_UNAUTHORIZED,
                    'message': 'شماره تلفن یا رمز عبورتان را بدرستی وارد نکردید'
                }],
                'result': None,
                'resultStatus': 1
        }, status=status.HTTP_401_UNAUTHORIZED)


class SignUpView(APIView):
    serializer_class = UserSignupSerializerRequest

    @extend_schema(
        request=UserSignupSerializerRequest
    )
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'validationMessage': [{
                        'statusCode': status.HTTP_201_CREATED,
                        'message': 'ثبت نام شما با موفقیت انجام شد'
                    }],
                    'result': serializer.data,
                    'resultStatus': 0
                }, status=status.HTTP_201_CREATED)
            elif serializer.errors is not None and serializer.errors.get('phone_number') is not None and serializer.errors.get('phone_number')[0] is not None and str(serializer.errors.get('phone_number')[0]) == 'user with this phone number already exists.':
                return Response({
                    'validationMessage': [{
                        'statusCode': status.HTTP_400_BAD_REQUEST,
                        'message': 'کاربری با این مشخصات از قبل وجود دارد'
                    }],
                    'result': None,
                    'resultStatus': 1
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': "Bad Request"
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'validationMessage': [{
                    'statusCode': status.HTTP_400_BAD_REQUEST,
                    'message': str(e)
                }],
                'result': None,
                'resultStatus': 1
            }, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdatePasswordSerializer

    @extend_schema(request=UserUpdatePasswordSerializer)
    def post(self, request):
        serializer = UserUpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(id=request.user.id)
        user.set_password(serializer.validated_data.get('password'))
        user.save()
        return Response("Password successfully changed", status=status.HTTP_200_OK)


class UpdateUserInfo(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateInfoSerializerRequest

    @extend_schema(request=UserUpdateInfoSerializerRequest)
    def put(self, request, *args, **kwargs):
        serializer = UserUpdateInfoSerializerRequest(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
