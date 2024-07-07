from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganisationsView, OrganisationDetailView, AddUserToOrganisationView

urlpatterns = [
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('api/users/<str:id>', UserDetailView.as_view(), name='user_detail'),
    path('api/organisations', OrganisationsView.as_view(), name='organisations'),
    path('api/organisations/<str:orgId>', OrganisationDetailView.as_view(), name='organisation_detail'),
    path('api/organisations/<str:orgId>/users', AddUserToOrganisationView.as_view(), name='add_user_to_organisation'),
]
