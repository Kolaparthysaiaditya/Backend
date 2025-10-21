import random
import string
from rest_framework import serializers
from .models import Projects, empollyDeatiles, Interns, projectTeams, ProjectsInfo, EmployeeAttendance, InternAttendance


class ProjectInfoNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectsInfo
        fields = ['id', 'category', 'start_date', 'deadline', 'status']

class ProjectSerializer(serializers.ModelSerializer):
    project_info = ProjectInfoNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Projects
        fields = ['id', 'title', 'links', 'para', 'rate', 'image', 'project_info']


class EmployProfileSerializer(serializers.ModelSerializer):
    currentProject = serializers.CharField(source='currentProject.title', default="No project assigned")
    class Meta:
        model = empollyDeatiles
        fields = [
            "Ename",
            "Eemail",
            "phone",
            "experience",
            "roll",
            "propic",
            "currentProject",
            "previousProjects",
        ]

class ProjectTeamsSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.title")
    status = serializers.CharField(source="proStatus")

    class Meta:
        model = projectTeams
        fields = ["project_name", "status"]
 

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

class ProjectInfoSerializer(serializers.ModelSerializer):
    project = serializers.SerializerMethodField()
    class Meta:
        model = ProjectsInfo
        fields = "__all__"
        
    def get_project(self, obj):
        return {
            "id": obj.project.id,
            "title": obj.project.title,
            "links": obj.project.links,
            "para": obj.project.para,
            "rate": obj.project.rate,
            "image": obj.project.image.url if obj.project.image else None
        }

class InternsSerializer(serializers.ModelSerializer):
    class Meta :
        model = Interns
        fields = "__all__"


class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    Ename = serializers.CharField(source='employee.Ename', read_only=True)
    Eid = serializers.CharField(source='employee.Eid', read_only=True)
    date = serializers.DateField(read_only=True)

    class Meta:
        model = EmployeeAttendance
        fields = "__all__"

class InternAttendanceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="intern.name", read_only=True)
    Iid = serializers.CharField(source="intern.Iid", read_only=True)

    class Meta:
        model = InternAttendance
        fields = "__all__"

