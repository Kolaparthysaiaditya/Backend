from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Projects(models.Model):
    image = models.ImageField(upload_to="photos/")
    links = models.CharField(max_length=555)
    title = models.CharField(max_length=255)
    para = models.CharField(max_length=555)
    rate = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.title}, {self.rate}"
    
class ProjectsInfo(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Cancelled', 'Cancelled'),
    ]

    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="project_info")
    category = models.CharField(max_length=255)
    start_date = models.DateField()
    deadline = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.project.title} - {self.status}"

class empollyDeatiles(models.Model):
    ROLE_CHOICES = [
        ('CEO', 'CEO'),
        ('HR', 'HR'),
        ('Manager', 'Manager'),
        ('Developer', 'Developer'),
        ('Tester', 'Tester'),
        ('UXI Developer', 'UXI Developer'),
    ]
    propic = models.ImageField(upload_to="photos/")
    Ename = models.CharField(max_length=225)
    Eemail = models.EmailField()
    password = models.CharField(max_length=255)
    phone = models.IntegerField(unique=True)
    Eid = models.CharField(unique=True, max_length=255)
    roll = models.CharField(max_length=255, choices=ROLE_CHOICES)
    experience = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(45)])
    currentProject = models.ForeignKey(Projects, on_delete=models.SET_NULL, blank=True, null=True , related_name="assend_employee")
    previousProjects = models.ManyToManyField(Projects, blank=True, related_name="previous_employees")

    def __str__(self):
        return f"{self.Ename} {self.roll}"
    

class Interns(models.Model):
    COURSE_CHOICES = [
        ('WEB Frontend', 'Web Frontend'),
        ('Python Fullstack', 'Python Fullstack'),
        ('Flutter', 'Fultter'),
        ('AI & ML', 'AI & ML'),
        ('UIX', 'UIX'),
    ]
    propic = models.ImageField(upload_to="photos/")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=555)
    phone = models.IntegerField(unique=True)
    Iid = models.CharField(max_length=100, unique=True)
    course = models.CharField(max_length=255, choices=COURSE_CHOICES)

    def __str__(self):
        return f"{self.name}"


class projectTeams(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Cancelled', 'Cancelled'),
    ]
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="project_team")
    Ename = models.ForeignKey(empollyDeatiles, on_delete=models.CASCADE, related_name="p_member")
    proStatus = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.Ename.Ename} in {self.project.title} project"

class EmployeeAttendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('On Leave', 'On Leave'),
    ]

    employee = models.ForeignKey(empollyDeatiles, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Absent')

    def __str__(self):
        return f"{self.employee.Ename} - {self.date} ({self.status})"

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

class InternAttendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('On Leave', 'On Leave'),
    ]

    intern = models.ForeignKey(Interns, on_delete=models.CASCADE, related_name="intern_attendance")
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Absent')

    class Meta:
        unique_together = ('intern', 'date')
        ordering = ["-date"]

    def __str__(self):
        return f"{self.intern.name}"

