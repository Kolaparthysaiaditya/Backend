import random
import pytz
from datetime import datetime
from django.utils import timezone
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from .models import Projects, empollyDeatiles, projectTeams, ProjectsInfo, Interns, EmployeeAttendance, InternAttendance
from .serializers import ProjectSerializer,EmployLoginSerializer, InternLoginSerializer, EmployProfileSerializer, ProjectTeamsSerializer, ProjectInfoSerializer, InternsSerializer, EmployeeAttendanceSerializer, InternAttendanceSerializer


OTP_Data = {} 
internid = 0
IST = pytz.timezone('Asia/Kolkata')

@api_view(["POST"])
def profile_card(request):
    Eid = request.data.get("Eid")
    try:
        profile = empollyDeatiles.objects.get(Eid=Eid)
        serializer = EmployProfileSerializer(profile)
        return Response(serializer.data)
    except empollyDeatiles.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)


@api_view(['POST'])
def current_project(request):
    Eid = request.data.get('Eid')

    if not Eid:
        return Response({'error': 'Eid is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = empollyDeatiles.objects.get(Eid=Eid)
        project = employee.currentProject

        if not project:
            return Response({'message': 'No current project assigned.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectSerializer(project, context={'request': request})  # 👈 important
        return Response(serializer.data, status=status.HTTP_200_OK)

    except empollyDeatiles.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(["POST"])
def previous_projects_by_ids(request):
    Eid = request.data.get("Eid")
    project_ids = request.data.get("project_ids", [])

    if Eid:
        try:
            user = empollyDeatiles.objects.get(Eid=Eid)
        except empollyDeatiles.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        projects_qs = user.previousProjects.all()
        if not projects_qs.exists():
            projects_qs = Projects.objects.filter(project_team__Ename=user)

    elif project_ids:
        projects_qs = Projects.objects.filter(id__in=project_ids)
    else:
        return Response({"error": "Eid or project_ids required"}, status=400)

    data = []
    for p in projects_qs:
        pi = p.project_info.first()  # get first ProjectsInfo
        data.append({
            "id": p.id,
            "title": p.title,
            "para": p.para,
            "rate": p.rate,
            "links": p.links,
            "image": f"http://127.0.0.1:8000/{p.image}" if p.image else None,
            "project_info": [{
                "id": pi.id,
                "status": pi.status,
                "start_date": pi.start_date,
                "deadline": pi.deadline
            }] if pi else []
        })

    return Response(data)


@api_view(["GET"])
def projectInfo(request):
    projects = ProjectsInfo.objects.all()
    serializer = ProjectInfoSerializer(projects, many=True)
    return Response(serializer.data)

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



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_project(request):
   
    # Project fields
    title = request.data.get("title")
    links = request.data.get("links")
    para = request.data.get("para")
    rate = request.data.get("rate")
    image = request.FILES.get("image")

    # ProjectInfo fields
    category = request.data.get("category")
    start_date = request.data.get("start_date") or date.today()
    deadline = request.data.get("deadline") or date.today()
    status = request.data.get("status") or "Pending"

    if not all([title, links, para, rate, image, category]):
        return Response({"error": "All fields (title, links, para, rate, image, category) are required."}, status=400)

    try:
        # Create Project
        project = Projects.objects.create(
            title=title,
            links=links,
            para=para,
            rate=rate,
            image=image
        )

        # Create ProjectInfo
        ProjectsInfo.objects.create(
            project=project,
            category=category,
            start_date=start_date,
            deadline=deadline,
            status=status
        )

        serializer = ProjectSerializer(project)
        return Response({"message": "Project added successfully", "project": serializer.data}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['PUT'])
def update_status_deadline(request, pk):
    """
    Update only status and deadline.
    """
    try:
        project_info = ProjectsInfo.objects.get(pk=pk)
    except ProjectsInfo.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    status_val = request.data.get("status")
    deadline_val = request.data.get("deadline")

    if status_val:
        project_info.status = status_val
    if deadline_val:
        project_info.deadline = deadline_val
    project_info.save()

    return Response({"message": "Status and deadline updated successfully"})

@api_view(["GET"])
def get_interns(request):
    intern = Interns.objects.all()
    serializer = InternsSerializer(intern, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_intern(request, iid):
    try:
        intern = Interns.objects.get(Iid=iid)
        intern.delete()
        return Response({'message': 'Intern deleted successfully'})
    except Interns.DoesNotExist:
        return Response({'error': 'Intern not found'}, status=404)

@api_view(['POST'])
def add_intern(request):
    from datetime import datetime
    from .models import Interns

    name = request.data.get("name")
    email = request.data.get("email")
    phone = request.data.get("phone")
    password = request.data.get("password")
    course = request.data.get("course")
    propic = request.FILES.get("propic")

    if not all([name, email, phone, password, course]):
        return Response({"error": "All fields are required."}, status=400)

    if propic is None:
        return Response({"error": "Profile picture is required."}, status=400)

    # Year part
    year_suffix = datetime.now().strftime("%y")  # last 2 digits of year, e.g., '25'

    # Find last intern to get last incremental number
    last_intern = Interns.objects.filter(Iid__startswith=f"it{year_suffix}") \
                                 .order_by("-Iid").first()
    if last_intern:
        last_number = int(last_intern.Iid[-3:])  # get last 3 digits
        new_number = last_number + 1
    else:
        new_number = 1

    # Pad to 3 digits
    number_part = str(new_number).zfill(3)

    Iid = f"IT{year_suffix}{number_part}"

    try:
        intern = Interns.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            course=course,
            propic=propic,
            Iid=Iid
        )
        serializer = InternsSerializer(intern)
        return Response(serializer.data, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_employees(request):
    employees = empollyDeatiles.objects.exclude(roll = "CEO")
    serializer = EmployProfileSerializer(employees, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def get_all_employees_attendance(request):
   
    employees = empollyDeatiles.objects.all()
    data = []

    total_days = EmployeeAttendance.objects.values_list('date', flat=True).distinct().count()

    for emp in employees:
        attendance_records = emp.attendance_records.all().order_by('-date')

        serialized_records = [
            {
                "date": record.date,
                "status": record.status,
                "check_in": record.check_in,
                "check_out": record.check_out,
            }
            for record in attendance_records
        ]

        present_days = emp.attendance_records.filter(status="Present").count()

        percentage = 0
        if total_days > 0:
            percentage = round((present_days / total_days) * 100, 2)

        data.append({
            "Eid": emp.Eid,
            "Ename": emp.Ename,
            "roll": emp.roll,
            "attendance_percentage": percentage,
            "records": serialized_records
        })

    return Response(data)

@api_view(['GET'])
def get_all_intern_attadence(request):
    interns = Interns.objects.all()
    data =[]

    total_days = InternAttendance.objects.values_list('date', flat=True).distinct().count()

    for intern in interns:
        intern_attendance = intern.intern_attendance.all().order_by('-date')

        serialized_records = [
            {
                "date": record.date,
                "status": record.status,
                "check_in": record.check_in,
                "check_out": record.check_out,
            }
            for record in intern_attendance
        ]

        present_days = intern.intern_attendance.filter(status="Present").count()

        percentage = 0
        if total_days > 0:
            percentage = round((present_days / total_days) * 100, 2)

        data.append({
            "Iid": intern.Iid,
            "name":intern.name,
            "attendance_percentage": percentage,
            "records": serialized_records
        })
    return Response(data)



@api_view(['POST'])
def mark_attendance(request):
    Eid = request.data.get("Eid")
    status = request.data.get("status", "Present")
    check_in = request.data.get("check_in")

    if not Eid:
        return Response({"error": "Eid is required"}, status=400)

    try:
        employee = empollyDeatiles.objects.get(Eid=Eid)
    except empollyDeatiles.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    date_today = timezone.now().date()  # ✅ only date, not datetime

    if EmployeeAttendance.objects.filter(employee=employee, date=date_today).exists():
        return Response({"error": "Attendance already marked for today"}, status=400)

    try:
        check_in_time = datetime.strptime(check_in, "%H:%M:%S").time()
    except Exception as e:
        return Response({"error": "Invalid check-in time format"}, status=400)

    attendance = EmployeeAttendance.objects.create(
        employee=employee,
        status=status,
        check_in=check_in_time,
        date=date_today  # explicitly set date as date object
    )

    serializer = EmployeeAttendanceSerializer(attendance)
    return Response({"message": "Attendance marked", "data": serializer.data}, status=201)

@api_view(['POST'])
def mark_checkout(request):
    Eid = request.data.get("Eid")
    check_out = request.data.get("check_out")

    if not Eid:
        return Response({"error": "Eid is required"}, status=400)

    try:
        employee = empollyDeatiles.objects.get(Eid=Eid)
    except empollyDeatiles.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    today = timezone.now().date()

    try:
        attendance = EmployeeAttendance.objects.get(employee=employee, date=today)
    except EmployeeAttendance.DoesNotExist:
        return Response({"error": "No check-in record found for today"}, status=400)

    if attendance.check_out:
        return Response({"error": "Already logged out"}, status=400)

    attendance.check_out = datetime.strptime(check_out, "%H:%M:%S").time()
    attendance.save()

    serializer = EmployeeAttendanceSerializer(attendance)
    return Response({"message": "Checked out successfully", "data": serializer.data})


@api_view(['POST'])
def get_employee_attendance(request):
    Eid = request.data.get("Eid")
    if not Eid:
        return Response({"error": "Eid required"}, status=400)

    try:
        employee = empollyDeatiles.objects.get(Eid=Eid)
    except empollyDeatiles.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    records = EmployeeAttendance.objects.filter(employee=employee).order_by('-date')
    serializer = EmployeeAttendanceSerializer(records, many=True)
    return Response({
        "employee": {
            "Ename": employee.Ename,
            "Eid": employee.Eid,
            "roll": employee.roll,
            "phone": employee.phone,
            "experience": employee.experience,
            "propic": employee.propic.url if employee.propic else None,
        },
        "attendance": serializer.data
    })

@api_view(['POST'])
def get_intern_attendance(request):
    Iid = request.data.get("Iid")
    if not Iid :
        return Response({"error": "Iid Required"}, status=400)
    
    try:
        intern = Interns.objects.get(Iid=Iid)
    except Interns.DoesNotExist:
        return Response({"error":"Intern not found"}, status=404)
    
    record = InternAttendance.objects.filter(inter=intern).order_by('-date')
    serializer = InternAttendanceSerializer(record, many=True)
    return Response({
        "intern": {
            "name":intern.name,
            "Iid":intern.Iid,
            "phone":intern.phone,
            "propic":intern.propic.url if intern.propic else None,
        },
        "attendance": serializer.data
    })
 