from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from rest_framework.throttling import UserRateThrottle
from .models import FriendRequest, User, UserActivity
from .serialization import FriendRequestSerializer, ModeSerial, AcceptSerial, PendingFriendRequestSerializer, UserActivitySerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.db.models import Q
from rest_framework.decorators import action
from django.conf import settings
from lib.pagination import CustomPageNumberPagination
from .permissions import IsAdmin, IsWrite, IsRead

# Custom Throttle class for limiting friend requests
class FriendRequestThrottle(UserRateThrottle):
    rate = '3/minute'

class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (JWTAuthentication,)
    pagination_class = CustomPageNumberPagination

    def get_throttles(self):
        if self.action == 'create':
            return [FriendRequestThrottle()]
        return super().get_throttles()
    
    def get_permissions(self):
        """
        Custom method to return the appropriate permissions based on the user's group.
        """
        # Check if the user belongs to the 'admin' group
        if self.request.user.groups.filter(name='admin').exists():
            return [IsAdmin()]  # Full access for admin group

        # Check if the user belongs to the 'write' group
        elif self.request.user.groups.filter(name='write').exists():
            return [IsWrite()]  # Allow write and read operations for write group

        # Check if the user belongs to the 'read' group
        elif self.request.user.groups.filter(name='read').exists():
            return [IsRead()]  # Read-only access for read group

        return super().get_permissions()  # Default permission if no group matches

    @swagger_auto_schema(tags=['Friend Request'])
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        sender = request.user
        receiver = User.objects.get(id=request.data['receiver'])

        # Check if already blocked
        if FriendRequest.objects.filter(sender=sender, receiver=receiver, mode='Block').exists():
            return Response({"error": "You cannot send a friend request to a blocked user."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if request is on cooldown
        existing_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).first()
        if existing_request and existing_request.is_on_cooldown():
            return Response({"error": "You are on cooldown. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
        friend_request = super().create(request, *args, **kwargs)
        UserActivity.objects.create(user=sender, target_user=receiver, action='FRIEND_REQUEST_SENT', friend_request=FriendRequest.objects.get(id=friend_request.data['id']))
        # Proceed to create friend request
        return friend_request

    @swagger_auto_schema(tags=['Friend Request'], request_body=AcceptSerial)
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        status_update = request.data.get('status')

        # Handle friend request acceptance
        if status_update == 'Accept':
            instance.status = 'Accept'
            UserActivity.objects.create(user=request.user, target_user=instance.receiver, action='FRIEND_REQUEST_ACCEPTED', friend_request=instance)
        elif status_update == 'Reject':
            instance.status = 'Reject'
            UserActivity.objects.create(user=request.user, target_user=instance.receiver, action='FRIEND_REQUEST_REJECTED', friend_request=instance)
            instance.set_cooldown(24)  # Set 24-hour cooldown
        instance.save()

        return Response({"status": instance.status}, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Friend Request'], request_body=ModeSerial)
    @transaction.atomic
    def block_user(self, request, *args, **kwargs):
        sender = request.user
        receiver = User.objects.get(id=request.data['receiver'])

        # Block user
        FriendRequest.objects.update_or_create(sender=sender, receiver=receiver, defaults={'mode': 'Block'})
        UserActivity.objects.create(user=sender, target_user=receiver, action='FRIEND_REQUEST_BLOCKED')
        return Response({"status": "User blocked"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Friend Request'], request_body=ModeSerial)
    @transaction.atomic
    def unblock_user(self, request, *args, **kwargs):
        sender = request.user
        receiver = User.objects.get(id=request.data['receiver'])

        # Unblock user
        friend_request = FriendRequest.objects.filter(sender=sender, receiver=receiver).first()
        if friend_request:
            friend_request.mode = 'Unblock'
            friend_request.save()
            UserActivity.objects.create(user=sender, target_user=receiver, action='FRIEND_REQUEST_UNBLOCKED')
        return Response({"status": "User unblocked"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='friends-list')
    @swagger_auto_schema(tags=['Friend Request'])
    def friends_list(self, request):
        user = request.user
        cache_key = f"friends_list_{user.id}"
        cached_friends = cache.get(cache_key)

        if cached_friends:
            return Response(cached_friends, status=status.HTTP_200_OK)

        # Fetch friends where the request was accepted
        friends_qs = FriendRequest.objects.filter(
            Q(sender=user, status='Accept') | Q(receiver=user, status='Accept')
        ).select_related('sender', 'receiver')

        # Extract friends (sender or receiver)
        friends = []
        for friend_request in friends_qs:
            if friend_request.sender == user:
                friends.append(friend_request.receiver)
            else:
                friends.append(friend_request.sender)

        # Serialize and cache the data
        friends_data = [{'id': friend.id, 'username': friend.username} for friend in friends]
        cache.set(cache_key, friends_data, timeout=settings.FRIENDS_LIST_CACHE_TIMEOUT)

        return Response(friends_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='pending-requests')
    @swagger_auto_schema(tags=['Friend Request'])
    def pending_requests(self, request):
        user = request.user

        # Filter for received friend requests with status "Send"
        pending_requests_qs = FriendRequest.objects.filter(receiver=user, status='Send').order_by('-created_at')

        # Paginate the results
        page = self.paginate_queryset(pending_requests_qs)
        if page is not None:
            serializer = PendingFriendRequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PendingFriendRequestSerializer(pending_requests_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='activities')
    @swagger_auto_schema(tags=['Friend Request'])
    def user_activities(self, request):
        user = request.user
        activities_qs = UserActivity.objects.filter(user=user).order_by('-created_at')

        # Use the viewset's pagination class and methods
        page = self.paginate_queryset(activities_qs)
        if page is not None:
            serializer = UserActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # In case pagination is disabled
        serializer = UserActivitySerializer(activities_qs, many=True)
        return Response(serializer.data)