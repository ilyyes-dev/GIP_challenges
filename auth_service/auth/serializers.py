from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150, trim_whitespace=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        username = validated_data.pop("username")
        return User.objects.create_user(username=username, password=password)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, write_only=True, trim_whitespace=True)
    password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account is not active.")

        attrs["user"] = user
        return attrs
