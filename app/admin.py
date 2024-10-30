from django.contrib import admin
from .models import User, Department, Profile, Course, Certification, UserEnrollment,Template,ScheduledEmail,ParentTemplateType, ChildTemplateType
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ('username', 'first_name', 'last_name', 'email', 'emp_id', 'designation', 'Date_of_joining')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'emp_id')

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')

class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')

class UserEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'certification', 'course_enrolled_at', 'course_completed_at', 'certification_enrolled_at', 'certification_completed_at')
    search_fields = ('user__username', 'course__name', 'certification__name')

class TemplateTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'content')
    list_filter = ('template_type',)

class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('file',)


admin.site.register(ParentTemplateType)
admin.site.register(ChildTemplateType)
admin.site.register(Template)
admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Profile)
admin.site.register(Course, CourseAdmin)
admin.site.register(Certification, CertificationAdmin)
admin.site.register(UserEnrollment, UserEnrollmentAdmin)
admin.site.register(ScheduledEmail)
