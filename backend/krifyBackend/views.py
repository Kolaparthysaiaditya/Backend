import random
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Projects, empollyDeatiles
from .serializers import ProjectSerializer,EmployLoginSerializer, InternLoginSerializer, EmployProfileSerializer

OTP_Data = {} 


@api_view(["POST"])
def profile_card(request):
    Eid = request.data.get("Eid")
    try:
        profile = empollyDeatiles.objects.get(Eid=Eid)
        serializer = EmployProfileSerializer(profile)
        print(serializer.data)
        return Response(serializer.data)
    except empollyDeatiles.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)


@api_view(['GET'])
def project_list(request):
    projects = Projects.objects.all().order_by("-rate")
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def top_projects(request):
    projects = Projects.objects.all().order_by("rate")[:3]
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def employ_login(request):
    print("hrllo")
    serializer = EmployLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        return Response({
            "message": "Login successful",
            "Eemail":user.Eemail,
            "Ename": user.Ename,
            "Eid": user.Eid,
            "roll": user.roll,
        })
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def intern_login(request):
    OFFICE_LAT = 16.969417
    OFFICE_LON = 82.223776

    def Distance(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        return R * 2 * atan2(sqrt(a), sqrt(1-a))
    

    serializer = InternLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)

    user = serializer.validated_data

    try :
        lat = float(request.data.get("lat"))
        lon = float(request.data.get("lon"))
    except (TypeError, ValueError):
        return Response({"message": "Invalid or missing location data"})
    
    dist = Distance(OFFICE_LAT, OFFICE_LON, lat, lon)
    print(f"Intern distance: {dist:.2f} km") 

    if dist > 0.5 :
        return Response({"message": "Unauthorized location. Please login In office."})

    return Response({
        "message": "Login successful",
        "email":user.email,
        "name": user.name,
        "Iid": user.Iid,
    })

@api_view(['POST'])
def Forget_password(request):
    email = request.data.get("email")

    try:
        user = empollyDeatiles.objects.get(Eemail = email)
    except empollyDeatiles.DoesNotExist :
        return Response({"error": "Email not Found"}, status=404)
    
    otp_code = "".join(random.choices("1234567890", k=4))
    expire_at = datetime.now() + timedelta(minutes=1)
    OTP_Data[email] = {'otp': otp_code, 'expire_at':expire_at}

    send_mail(
        "Krify Login info",
        f"Your OTP is {otp_code} it is only 1 minite valid",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )

    return Response({'message': 'OTP Send to email'}, status=200)

@api_view(['POST'])
def verify_OTP(request):
    email = request.data.get("email")
    otp_code = request.data.get("otp")
    
    record = OTP_Data[email]

    if datetime.now() > record["expire_at"]:
        OTP_Data.pop(email, None)
        return Response({"message":"OTP Expired"})
    if record['otp'] != otp_code :
        return Response({"message":"OTP incorrect"})
    
    return Response({"message":"OTP Verifyed"})

@api_view(['POST'])
def Reset_Password(request):
    email = request.data.get('email')
    password = request.data.get('password')
    confirem = request.data.get('confirem')

    if password != confirem :
        return Response({"message":"Passwords are not match"})
    
    try :
        user = empollyDeatiles.objects.get(Eemail = email)
        user.password = password
        user.save()

        return Response({"message":"Password reset successful"})
    
    except empollyDeatiles.DoesNotExist :
        return Response({"message":"User not found"})
