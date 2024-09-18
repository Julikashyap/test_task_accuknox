from .views import *
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .friend_request_action import FriendRequestViewSet

user_action_router = DefaultRouter()
user_action_router.register(r'user_action', UserOperations, basename='user_action')

assign_role_router = DefaultRouter()
assign_role_router.register(r'assign_role', AssignRoleToUSer, basename='assign_role')

friend_router = DefaultRouter()
friend_router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')

friend_request_block = FriendRequestViewSet.as_view({
    'post': 'block_user'
})

friend_request_unblock = FriendRequestViewSet.as_view({
    'post': 'unblock_user'
})

urlpatterns = [
    path('', index, name='welcome'),
    path('v1/api/register', RegisterAPI.as_view(), name='register'),
    path('v1/api/login', LoginAPI.as_view(), name='login'),
    path('v1/api/logout', LogOutAPI.as_view(), name='logout'),
    path('v1/api/profile_image', UpdateProfileImage.as_view(), name='profile_image'),
    path('v1/api/change_password', ChangePassword.as_view(), name='change_password'),
    re_path(r'^api/v1/', include(user_action_router.urls)),
    re_path(r'^api/v1/', include(assign_role_router.urls)),
    re_path(r'^api/v1/', include(friend_router.urls)),
    path('friend-requests/block/', friend_request_block, name='block-user'),
    path('friend-requests/unblock/', friend_request_unblock, name='unblock-user'),
]