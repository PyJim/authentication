from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer
from django.db import transaction
import uuid
from django.contrib.auth import authenticate

class RegisterView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    user.set_password(data['password'])
                    user.save()

                    org_name = f"{user.firstName}'s Organisation"
                    org = Organisation.objects.create(
                        org_id=str(uuid.uuid4()),
                        name=org_name,
                        description=''
                    )
                    org.users.add(user)
                    org.save()

                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'status': 'success',
                        'message': 'Registration successful',
                        'data': {
                            'accessToken': str(refresh.access_token),
                            'user': UserSerializer(user).data
                        }
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'status': 'Bad request',
                    'message': 'Registration unsuccessful',
                    'statusCode': 400,
                    'errors': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'Unprocessable entity',
            'message': 'Registration unsuccessful',
            'statusCode': 422,
            'errors': serializer.errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        user = authenticate(email=data['email'], password=data['password'])
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'accessToken': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Bad request',
            'message': 'Authentication failed',
            'statusCode': 401
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user == user or request.user in user.organisations.all():
            return Response({
                'status': 'success',
                'message': 'User record',
                'data': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Forbidden',
            'message': 'You do not have access to this user\'s record',
            'statusCode': 403
        }, status=status.HTTP_403_FORBIDDEN)

class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organisations.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Organisations retrieved',
            'data': {'organisations': serializer.data}
        }, status=status.HTTP_200_OK)

class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        org = self.get_object()
        if request.user in org.users.all():
            return Response({
                'status': 'success',
                'message': 'Organisation record',
                'data': OrganisationSerializer(org).data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Forbidden',
            'message': 'You do not have access to this organisation\'s record',
            'statusCode': 403
        }, status=status.HTTP_403_FORBIDDEN)

class CreateOrganisationView(generics.CreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            with transaction.atomic():
                org = Organisation.objects.create(
                    org_id=str(uuid.uuid4()),
                    name=data['name'],
                    description=data.get('description', '')
                )
                org.users.add(request.user)
                org.save()
                return Response({
                    'status': 'success',
                    'message': 'Organisation created successfully',
                    'data': OrganisationSerializer(org).data
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'Bad request',
                'message': 'Client error',
                'statusCode': 400,
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class AddUserToOrganisationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, org_id, *args, **kwargs):
        data = request.data
        try:
            org = Organisation.objects.get(org_id=org_id)
            if request.user in org.users.all():
                user = User.objects.get(user_id=data['userId'])
                org.users.add(user)
                org.save()
                return Response({
                    'status': 'success',
                    'message': 'User added to organisation successfully',
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'Forbidden',
                'message': 'You do not have access to this organisation',
                'statusCode': 403
            }, status=status.HTTP_403_FORBIDDEN)
        except Organisation.DoesNotExist:
            return Response({
                'status': 'Not found',
                'message': 'Organisation not found',
                'statusCode': 404
            }, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({
                'status': 'Not found',
                'message': 'User not found',
                'statusCode': 404
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'Bad request',
                'message': 'Client error',
                'statusCode': 400,
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
