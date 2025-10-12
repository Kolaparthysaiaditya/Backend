import random
import string
from rest_framework import serializers
from .models import Projects, empollyDeatiles, Interns, projectTeams

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = "__all__"

class EmployProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = empollyDeatiles
        fields = "__all__"

class ProjectTeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = projectTeams
        fields = "__all__"


class EmployLoginSerializer(serializers.Serializer):
    Eemail = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("Eemail")
        password = data.get("password")

        try:
            user = empollyDeatiles.objects.get(Eemail=email)
        except empollyDeatiles.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if user.password != password:   # ⚠️ In production use hashing!
            raise serializers.ValidationError("Invalid email or password")

        return user
    

class InternLoginSerializer(serializers.Serializer):
    Iid = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        Iid = data.get("Iid")
        password = data.get("password")

        try :
            user = Interns.objects.get(Iid = Iid)
        except Interns.DoesNotExist:
            raise serializers.ValidationError("invalid user")
        
        if user.password != password:
            raise serializers.ValidationError("Incorrect password")
        
        return user

