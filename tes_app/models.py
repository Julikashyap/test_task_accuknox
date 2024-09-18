from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class User(AbstractUser):
    """
        Inherits from default User of Django and extends the fields.
        The following fields are part of Django User Model:
        | id
        | password
        | last_login
        | is_superuser
        | username
        | first_name
        | last_name
        | email
        | is_staff
        | is_active
        | date_joined
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    email = models.EmailField(unique=True, null=False, db_index=True, error_messages={'unique': "Email already exists"})
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=250)
    pin_code = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    image = models.ImageField(upload_to='profile', blank=True, null=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def save(self, *args, **kwargs):
        # Call the original save method to create the user
        super(User, self).save(*args, **kwargs)
        read_group, created = Group.objects.get_or_create(name='read')
        if read_group not in self.groups.all():
            self.groups.add(read_group)

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('Send', 'Send'),
        ('Accept', 'Accept'),
        ('Reject', 'Reject'),
    ]

    MODE_CHOICES = [
        ('Unblock', 'Unblock'),
        ('Block', 'Block'),
    ]

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='Send')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    mode = models.CharField(max_length=12, choices=MODE_CHOICES, default='Unblock')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cooldown_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def set_cooldown(self, hours=24):
        self.cooldown_end = timezone.now() + timedelta(hours=hours)
        self.save()

    def is_on_cooldown(self):
        return self.cooldown_end and self.cooldown_end > timezone.now()

class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('FRIEND_REQUEST_SENT', 'Friend Request Sent'),
        ('FRIEND_REQUEST_ACCEPTED', 'Friend Request Accepted'),
        ('FRIEND_REQUEST_REJECTED', 'Friend Request Rejected'),
        ('FRIEND_REQUEST_BLOCKED', 'Friend Request Blocked'),
        ('FRIEND_REQUEST_UNBLOCKED', 'Friend Request Unblocked'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    friend_request = models.ForeignKey(FriendRequest, on_delete=models.CASCADE, related_name='logged_activities', null=True, blank=True)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='targeted_activities', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)