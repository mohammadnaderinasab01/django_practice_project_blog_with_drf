from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("jwt/create/", TokenObtainPairView.as_view(), name="jwt_create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh_token"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt_verify_token"),
    path("update-password/", views.UpdatePasswordView.as_view(), name="update_password"),
    path("update-user-info/", views.UpdateUserInfo.as_view(), name="update_user_info"),
]
