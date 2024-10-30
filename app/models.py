from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager,PermissionsMixin
from django.utils import timezone
from django.conf import settings
from PIL import Image
import os
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomUserManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(username=username)
    
class CustomUserManager(UserManager):
    pass

class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=50, blank=False, unique=True)
    About = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    first_name = models.CharField(max_length=25, blank=False)
    last_name = models.CharField(max_length=25, blank=False)
    email = models.EmailField(unique=True)
    emp_id = models.CharField(max_length=10, blank=True)
    designation = models.CharField(max_length=25, blank=True)
    Date_of_birth = models.DateField(null=True, blank=True)
    contact_no = models.CharField(max_length=10, blank=True)
    expertise = models.CharField(max_length=250, blank=True)
    certifications = models.CharField(max_length=250, blank=True)
    Date_of_joining = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=255, blank=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class Department(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures')
    last_login_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    About = models.CharField(max_length=120,null=True,blank=True)

    def resize_profile_picture(self):
        img = Image.open(self.picture.path)
        img.thumbnail((105, 135))
        resized_image_path = os.path.join(os.path.dirname(self.profile_picture.path), 'resized_', os.path.basename(self.profile_picture.path))
        img.save(resized_image_path)

    def __str__(self):
        if self.department:
            return f"{self.user.username} - {self.department.name}"
        else:
            return f"{self.user.username} - No department assigned"


class Course(models.Model):
    POINTS_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    link = models.URLField(unique=True, blank=False)
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),  # Minimum value is 0
            MaxValueValidator(100)    # Maximum value is 5
        ]
    )
    points = models.CharField(max_length=1, choices=POINTS_CHOICES, default='0')

    def __str__(self):
        return self.name

class Certification(models.Model):
    POINTS_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    link = models.URLField(max_length=255)
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),  
            MaxValueValidator(100)    
        ]
    )
    points = models.CharField(max_length=1, choices=POINTS_CHOICES, default='0')

    def __str__(self):
        return self.name



class UserEnrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, null=True, blank=True)
    course_enrolled_at = models.DateTimeField(null=True, blank=True)
    course_completed_at = models.DateTimeField(null=True, blank=True)
    course_progress = models.IntegerField(default=0)

    certification = models.ForeignKey('Certification', on_delete=models.CASCADE, null=True, blank=True)
    certification_enrolled_at = models.DateTimeField(null=True, blank=True)
    certification_completed_at = models.DateTimeField(null=True, blank=True)
    certification_progress = models.IntegerField(default=0)
    
    
    def __str__(self):
        return f"{self.user.username} - {self.course.name if self.course else self.certification.name}"
    
class UserCertification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.certification.name}"
    
class Email_Message(models.Model):
    From = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_emails')
    TO = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_emails')    
    cc_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='cc_emails')
    bcc_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bcc_emails')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    replied_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Email from {self.From} to {self.TO}"

    def get_replies(self):
        return Email_Message.objects.filter(replied_to=self)
    
    def save_to_inbox(self, user):
        """
        Saves a copy of the email to the inbox of the specified user.

        Args:
            user (User): The user whose inbox the email should be saved to.
        """
        # Create a new Email_Message instance for the inbox copy
        inbox_email = Email_Message(
            From=self.From,
            TO=user,
            CC=self.cc_users,
            BCC=self.bcc_users,
            subject=self.subject,
            message=self.message,
            sent=True  # Mark as sent since it's a copy
        )

        # Save the inbox copy to the database
        inbox_email.save()

        # Create a reply relationship for the inbox copy
        inbox_email.replies.add(self)
    
    @property
    def is_reply(self):
        return self.replied_to is not None

    @property
    def original_email(self):
        if self.is_reply:
            return self.replied_to
        return None

    @property
    def reply_emails(self):
        if self.is_reply:
            return Email_Message.objects.filter(replied_to=self.replied_to)
        return Email_Message.objects.filter(replied_to=self)


class ParentTemplateType(models.Model):
    name = models.CharField(max_length=255)

class ChildTemplateType(models.Model):
    parent_template_type = models.ForeignKey(ParentTemplateType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='Select Template type')

class Template(models.Model):
    child_template_type = models.ForeignKey(ChildTemplateType, on_delete=models.CASCADE, null=True)  # Allow null initially
    name = models.CharField(max_length=255)
    content = models.TextField(max_length=10000, null=True)

    
class ScheduledEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_emails_sent')
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='scheduled_emails_received')
    cc_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='scheduled_emails_cc', blank=True)
    bcc_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='scheduled_emails_bcc', blank=True)
    scheduled_time = models.DateTimeField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Email from {self.sender} to {self.receivers.all()} scheduled for {self.scheduled_time}"
class ReminderEmail(models.Model):
    scheduled_email = models.ForeignKey(ScheduledEmail, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    sent = models.BooleanField(default=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminder_emails_sent')
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='reminder_emails_received')
