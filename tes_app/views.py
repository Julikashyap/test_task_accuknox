from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import permissions
from .models import User
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from .serialization import *
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from tes_app.filter_classes import UserFilterClass
from lib.pagination import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from django.core.mail import send_mail
from test_task import settings
from django.http import HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .permissions import IsAdmin, IsWrite, IsRead
from lib.custom_permissions import IsAdminOrReadOnlyParmission
from django.contrib.auth.models import Group

def index(request):
    return HttpResponse("Welcome to the Social Networking Application App <a href='/swagger'>Doc</a>")

def password_check(passwd):
    flag = 0
    import re
    if not re.search("[A-Z]", passwd):
        flag = 1
    if not re.search("[0-9]", passwd):
        flag = 2
    if not re.search("[@$!%*#?&]", passwd):
        flag = 3
    return flag

def send_email(email, link, jwt_token):
    """
    Function to send email to employee.
    """
    
    subject = "your account need to be verified"
    message = f'Click on Link to verify your Account(only valid for 5 minutes) {link}/{jwt_token}'
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])
    print("sent............")

class RegisterAPI(GenericAPIView):
    serializer_class = RegisterSerialization

    @swagger_auto_schema(tags=['Authentication'])
    def post(self, request, *args, **kwargs):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        address = request.data.get('address')
        pin_code = request.data.get('pin_code')
        city = request.data.get('city')
        country = request.data.get('country')
        password = request.data.get('password')

        checkpoint = password_check(password)
        if checkpoint == 1:
            return Response({'response': 'Password must contain atleast one capital alphbat'}, status=status.HTTP_400_BAD_REQUEST)
        if checkpoint == 2:
            return Response({'response': 'Password must contain atleast one digit'}, status=status.HTTP_400_BAD_REQUEST)
        if checkpoint == 3:
            return Response({'response': 'Password must contains one special character like @, $,#,&'}, status=status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.filter(email=email).count()
        if user_count:
            return Response({'response': 'User already exist'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=email, email=email, name=first_name+' '+ last_name, password=password, first_name=first_name, last_name=last_name, address=address, pin_code= pin_code, city=city, country=country)
        return Response(UserSerial(user).data, status=status.HTTP_201_CREATED)

class LoginAPI(GenericAPIView):
    serializer_class = LoginSerialization

    @swagger_auto_schema(tags=['Authentication'])
    @method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': "User does not exist!"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            result = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                **UserSerial(user).data
            }
            return JsonResponse({'status': 'Success', 'message': 'You have signed in successfully!', 'data': result}, safe=False)
        else:
            return Response({"message": "Invalid Password!"}, status=status.HTTP_400_BAD_REQUEST)

    # @ratelimit(key='ip', rate='2/m', method=['POST'], block=True)
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

class LogOutAPI(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = LogOutSerializer

    @swagger_auto_schema(tags=['Authentication'])
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
            return Response({"message": "Logout Successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token or token is missing."}, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileImage(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    parser_classes = (MultiPartParser,)

    @swagger_auto_schema(tags=['Authentication'], request_body=UpdateProfileImageSerializer)
    def post(self, request, *args, **kwargs):
        serializer = UpdateProfileImageSerializer(data = request.data)
        if serializer.is_valid():
            user = request.user
            print(user)
            data = request.data
            if data.get('image'):
                user.image = data.get('image')
            else:
                user.image = None
            user.save()
            return Response(UserSerial(request.user).data)
        else:
            return Response({'message':"Invalid data!"})


class ChangePassword(GenericAPIView):
    serializer_class = ChangePasswordSerial
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    @swagger_auto_schema(tags=["Authentication"])
    def post(self, request):
        email = request.user.email
        serializer = ChangePasswordSerial(data = request.data)
        if serializer.is_valid():
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')
            checkpoint = password_check(new_password)
            if checkpoint == 1:
                return Response({'response': 'Password must contain atleast one capital alphbat'}, status=status.HTTP_400_BAD_REQUEST)
            if checkpoint == 2:
                return Response({'response': 'Password must contain atleast one digit'}, status=status.HTTP_400_BAD_REQUEST)
            if checkpoint == 3:
                return Response({'response': 'Password must contains one special character like @, $,#,&'}, status=status.HTTP_400_BAD_REQUEST)

            userdata = User.objects.get(email=email)
            if userdata.check_password(new_password):
                message = {"result": "false", "response": "new password already exists"}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            if new_password == confirm_password:
                if userdata.check_password(old_password):
                    userdata.set_password(new_password)
                    userdata.save()
                else:
                    message = {"result": "false", "response": "Current password does not match"}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                message = {"result": "false", "response": "Confirm password not match with new password"}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"result": "true", "response": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        refresh_token = request.data.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()  # Blacklist the token
        message = {"result": "true", "response": "successfull changed password"}
        return Response(message, status=status.HTTP_200_OK)


class UserOperations(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (JWTAuthentication,)
    serializer_class = UserSerial
    filter_class = UserFilterClass
    filterset_fields = ["id", 'email', 'name']
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    swagger_ui = [
        openapi.Parameter('id', openapi.IN_QUERY, description="User ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('email', openapi.IN_QUERY, description="Email", type=openapi.TYPE_STRING),
        openapi.Parameter('name', openapi.IN_QUERY, description="name", type=openapi.TYPE_STRING),
    ]

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

    @swagger_auto_schema(tags=['User Search'], manual_parameters=swagger_ui)
    def list(self, request):
        queryset = User.objects.all().order_by()
        if self.filter_class:
            queryset = self.filter_class(request.GET, queryset=queryset).qs

        serializer = UserSerial(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['User Search'], request_body=CreateUserSerial)
    def create(self, request):
        if not request.user.is_superuser:
            return Response({'message': 'Only super user perform this action!'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CreateUserSerial(data=request.data)
        if serializer.is_valid():
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            address = request.data.get('address')
            pin_code = request.data.get('pin_code')
            city = request.data.get('city')
            country = request.data.get('country')
            password = request.data.get('password')
            exist_user = User.objects.filter(email=email).count()
            if exist_user:
                return Response({"message": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

            User.objects.create_user(username=email, email=email, name=first_name+' '+ last_name, password=password, first_name=first_name, last_name=last_name, address=address, pin_code= pin_code, city=city, country=country)
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['User Search'])
    def destroy(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({'message': 'Only super user perform this action!'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(tags=['Assign Role API'])
class AssignRoleToUSer(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnlyParmission]
    authentication_classes = (JWTAuthentication,)

    @swagger_auto_schema(tags=['Assign Role API'], request_body=AssignRoleSerialization)
    def create(self, request):
        serializer = AssignRoleSerialization(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data['name']
            try:
                user = User.objects.get(email=email)
            except:
                return Response({"message": "User not Exist."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                role = Group.objects.get(name=name)
            except:
                return Response({"message": "Role not Exist."}, status=status.HTTP_400_BAD_REQUEST)
            user.groups.add(role)
            user.save()
            return Response({"message": "Role assigned to User Successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Invalid Data!"}, serializer.errors, status=status.HTTP_400_BAD_REQUEST)