from rest_framework import serializers
from .models import User, Organisation

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'password', 'phone']

    def validate(self, data):
        if 'password' not in data or not data['password']:
            raise serializers.ValidationError({"password": "This field is required."})
        if 'firstName' not in data or not data['firstName']:
            raise serializers.ValidationError({"firstName": "This field is required."})
        if 'lastName' not in data or not data['lastName']:
            raise serializers.ValidationError({"lastName": "This field is required."})
        if 'email' not in data or not data['email']:
            raise serializers.ValidationError({"email": "This field is required."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        return user


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']
