from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import empollyDeatiles, Projects, Interns, projectTeams, ProjectsInfo, EmployeeAttendance, InternAttendance

@admin.register(empollyDeatiles)
class EmpollyDeatilesAdmin(ImportExportModelAdmin):
    pass

@admin.register(Projects)
class ProjectsAdmin(ImportExportModelAdmin):
    pass

@admin.register(Interns)
class InternsAdmin(ImportExportModelAdmin):
    pass

admin.site.register(projectTeams)
admin.site.register(ProjectsInfo)

@admin.register(InternAttendance)
class InternAttendanceAdmin(admin.ModelAdmin):
    list_display = ("intern", 'date', 'status', 'check_in', 'check_out',)
    search_fields = ('intern__name', 'intern__Iid', 'status')
    list_filter = ('status', 'date')

@admin.register(EmployeeAttendance)
class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in', 'check_out',)
    search_fields = ('employee__Ename', 'employee__Eid', 'status')
    list_filter = ('status', 'date')