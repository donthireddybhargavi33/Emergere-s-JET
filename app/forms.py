from django import forms
from .models import User, Department, Profile, Course, Certification, Email_Message,ScheduledEmail,ReminderEmail
from django.core.exceptions import ValidationError

class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',  'contact_no', 'About', 'Date_of_birth', 'profile_picture')
        widgets = {
            'Date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = "Username*"
        
class ProfessionalDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('emp_id', 'designation', 'expertise', 'email', 'Date_of_joining')
        widgets = {
            'Date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['email'].label = "Email*"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_picture', 'department', 'About')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['confirm_password'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ('email','username','first_name','last_name','Date_of_birth','Date_of_joining','emp_id','About','profile_picture','designation','contact_no','expertise','certifications','department')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long')
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match')
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    

    

class UserUpdationForm(forms.ModelForm):
    """
    Form to handle user profile updates.

    Attributes:
        department (ModelChoiceField): A field to select the user's department.
    """
    department = forms.ModelChoiceField(queryset=Department.objects.filter(parent=None))

    def _init_(self, *args, **kwargs):
        """
        Initializes the form.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super()._init_(*args, **kwargs)
        self.fields['department'].widget.attrs['onchange'] = 'getSubDepartments(this)'

    class Meta:
        """
        Meta class for the form.

        Attributes:
            model (User): The model associated with the form.
            fields (tuple): A tuple of fields to include in the form.
            widgets (dict): A dictionary of widgets to use for specific fields.
        """
        model = User
        fields = ('first_name', 'last_name', 'department', 'email', 'emp_id', 'designation', 'Date_of_birth', 'contact_no', 'expertise', 'certifications', 'Date_of_joining', 'profile_picture','About')
        widgets = {
            'Date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'Date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name', 'parent')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profile_picture',)

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if not profile_picture.name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise ValidationError('Only image files are allowed.')
        return profile_picture

class UserCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'description', 'link','points')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        course = super().save(commit=False)
        course.user = self.user
        course.progress = 0  # initialize progress field
        if commit:
            course.save()
        return course

class UserCertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ('name', 'description', 'link','points')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        certification = super().save(commit=False)
        certification.user = self.user
        certification.progress = 0  # initialize progress field
        if commit:
            certification.save()
        return certification
    
    

  
class EmailForm(forms.ModelForm):
    class Meta:
        model = Email_Message
        fields = ('From','TO', 'cc_users', 'bcc_users','subject', 'message')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['From'] = forms.ModelChoiceField(queryset=User.objects.filter(id=self.user.id), required=True)
            self.fields['TO'] = forms.ModelChoiceField(queryset=User.objects.exclude(id=self.user.id), required=True)
            self.fields['cc_users'] = forms.ModelMultipleChoiceField(queryset=User.objects.exclude(id=self.user.id), required=False)
            self.fields['bcc_users'] = forms.ModelMultipleChoiceField(queryset=User.objects.exclude(id=self.user.id), required=False)

    def clean_message(self):
        message = self.cleaned_data['message']
        if message:
            # Remove any unnecessary characters from the message
            message = message.replace('\n', ' ').replace('\r', ' ')
            self.cleaned_data['message'] = message
        return message

    def clean(self):
        cleaned_data = super().clean()
        From = cleaned_data.get('From')
        TO = cleaned_data.get('TO')
        cc_users = cleaned_data.get('cc_users')
        bcc_users = cleaned_data.get('bcc_users')
        subject = cleaned_data.get('subject')
        message = cleaned_data.get('message')


        # Check if the subject and message are not empty
        if not subject or not message:
            raise forms.ValidationError('Subject and message are required')

        # Check if the TO is not the same as the From
        if TO == From:
            raise forms.ValidationError('Receiver cannot be the same as the sender')

        # Check if the cc_users and bcc_users are not the same as the receiver or sender
        if cc_users and TO in cc_users:
            raise forms.ValidationError('CC users cannot include the receiver')
        if bcc_users and TO in bcc_users:
            raise forms.ValidationError('BCC users cannot include the receiver')
        if cc_users and From in cc_users:
            raise forms.ValidationError('CC users cannot include the sender')
        if bcc_users and From in bcc_users:
            raise forms.ValidationError('BCC users cannot include the sender')

        return cleaned_data


class ReplyEmailForm(forms.ModelForm):
    class Meta:
        model = Email_Message
        fields = ('message',)

    def _init_(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.email = kwargs.pop('email', None)
        super()._init_(*args, **kwargs)
        if self.user and self.email:
            self.fields['message'] = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10}))
            self.initial['message'] = f"Re: {self.email.subject}"



class ScheduledEmailForm(forms.ModelForm):
    class Meta:
        model = ScheduledEmail
        fields = ('subject', 'message', 'receivers', 'cc_users', 'bcc_users', 'scheduled_time')

    def _init_(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super()._init_(*args, **kwargs)
        if self.user:
            self.fields['receivers'] = forms.ModelMultipleChoiceField(queryset=User.objects.exclude(id=self.user.id), required=True)
            self.fields['cc_users'] = forms.ModelMultipleChoiceField(queryset=User.objects.exclude(id=self.user.id), required=False)
            self.fields['bcc_users'] = forms.ModelMultipleChoiceField(queryset=User.objects.exclude(id=self.user.id), required=False)

class ReminderEmailForm(forms.ModelForm):
    class Meta:
        model = ReminderEmail
        fields = ('reminder_time', 'sender', 'receivers')