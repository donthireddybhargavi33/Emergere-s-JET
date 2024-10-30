from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .forms import PersonalDetailsForm,ProfessionalDetailsForm, DepartmentForm,UserCourseForm, UserCertificationForm,UserUpdationForm,UserRegistrationForm,EmailForm,ReplyEmailForm,ScheduledEmailForm,ReminderEmailForm
from .models import User, Department,Course, Certification, UserEnrollment,Profile,UserCertification,Email_Message,Template,ScheduledEmail,ReminderEmail,ParentTemplateType, ChildTemplateType
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from django.db.models.signals import post_save
from django.db.models import Count
from app.models import User  
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from datetime import timedelta
from django.core.mail import get_connection,EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.http import HttpResponseForbidden
import logging
from django.templatetags.static import static
from .api import generate_email_response_function
from .email_sender import finalize_and_send_email


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        # Instantiate forms with POST data and possible file uploads
        user_registration_form = UserRegistrationForm(request.POST)
        personal_details_form = PersonalDetailsForm(request.POST, request.FILES)  # Include request.FILES
        professional_details_form = ProfessionalDetailsForm(request.POST)

        # Check if all forms are valid
        if user_registration_form.is_valid() and personal_details_form.is_valid() and professional_details_form.is_valid():
            # Create a new user
            user = user_registration_form.save()

            # Save the profile picture
            profile = Profile(user=user)  # Create a new Profile instance for the user
            profile.profile_picture = personal_details_form.cleaned_data['profile_picture']
            profile.save()  # Save the profile

            # Update the personal details
            personal_details_form.instance = user  # Assign the user instance to the form
            personal_details_form.save()  # Save personal details

            # Update the professional details
            professional_details_form.instance = user  # Assign the user instance to the form
            professional_details_form.save()  # Save professional details
            
            # Login the user
            login(request, user)

            # Redirect to the user's dashboard
            return redirect('dashboard')  # Redirecting to the dashboard using the URL name
            
        else:
            # If there are errors, render the form with errors
            return render(request, 'register.html', {
                'user_registration_form': user_registration_form,
                'personal_details_form': personal_details_form,
                'professional_details_form': professional_details_form,
            })
    else:
        # If not a POST request, instantiate empty forms
        user_registration_form = UserRegistrationForm()
        personal_details_form = PersonalDetailsForm()
        professional_details_form = ProfessionalDetailsForm()
        return render(request, 'register.html', {
            'user_registration_form': user_registration_form,
            'personal_details_form': personal_details_form,
            'professional_details_form': professional_details_form,
        })

def login_view(request):
    if request.method == 'POST':
        # Check if the username and password fields are present in the request
        if 'username' in request.POST and 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Pass the user object to the login function
                login(request, user)
                # Redirect to a success page
                return redirect('dashboard')
            else:
                # Return an error message
                return render(request, 'error.html', {'error_message': 'Invalid username or password'})
        else:
            # Return an error message if the username or password fields are missing
            return render(request, 'error.html', {'error_message': 'Please enter both username and password'})
    else:
        # Handle GET requests differently
        return render(request, 'login.html')  # Render the login template


def get_sub_departments(request, department_id):
    sub_departments = Department.objects.filter(parent_id=department_id)
    data = [{'id': sub_department.id, 'name': sub_department.name} for sub_department in sub_departments]
    return JsonResponse(data, safe=False)

def create_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'create_department.html', {'form': form})

def department_list(request):
    departments = Department.objects.all()
    return render(request, 'department_list.html', {'departments': departments})
@login_required
def user_list(request):
    User = get_user_model()  # Get the custom user model
    users = User.objects.filter(is_active=True)
    return render(request, 'user_list.html', {'users': users})
@login_required
def user_detail(request, pk):
    User = get_user_model()  # Get the custom user model
    user = User.objects.get(pk=pk)
    return render(request, 'user_detail.html', {'user': user})

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    About = user.About
    form = UserUpdationForm(instance=user)

    if request.method == 'POST':
        form = UserUpdationForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')

    return render(request, 'dashboard.html', {
        'form': form,
        'ongoing_courses': Course.objects.filter(userenrollment__user=user, userenrollment__completed_at__isnull=True),
        'completed_courses': Course.objects.filter(userenrollment__user=user, userenrollment__completed_at__isnull=False),
        'ongoing_certifications': Certification.objects.filter(usercertification__in=UserCertification.objects.filter(user=user, completed_at__isnull=True)),
        'completed_certifications': Certification.objects.filter(usercertification__in=UserCertification.objects.filter(user=user, completed_at__isnull=False)),
    })


@login_required
def course_view(request):
    user = request.user
    courses = Course.objects.filter(user=user)
    course_form = UserCourseForm(user=user)

    if request.method == 'POST':
        course_form = UserCourseForm(request.POST, user=user)
        if course_form.is_valid():
            course = course_form.save()
            # update progress field
            course.progress = 0
            course.save()
            messages.success(request, 'Course added successfully!')
            return redirect('course_view')

    return render(request, 'course.html', {
        'courses': courses,
        'course_form': course_form,
    })

@login_required
def certification_view(request):
    user = request.user
    certifications = Certification.objects.filter(user=user)
    certification_form = UserCertificationForm(user=user)

    if request.method == 'POST':
        certification_form = UserCertificationForm(request.POST, user=user)
        if certification_form.is_valid():
            certification = certification_form.save()
            # update progress field
            certification.progress = 0
            certification.save()
            messages.success(request, 'Certification added successfully!')
            return redirect('certification_view')

    return render(request, 'certification.html', {
        'certifications': certifications,
        'certification_form': certification_form,
    })

@login_required
def user_update(request, pk):
    User = get_user_model() 
    user = get_object_or_404(User, pk=pk)

    # Ensure that the user can only update their own profile
    if request.user != user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        # Create forms with the incoming POST data
        personal_details_form = PersonalDetailsForm(request.POST, request.FILES, instance=user)
        professional_details_form = ProfessionalDetailsForm(request.POST, instance=user)

        if personal_details_form.is_valid() and professional_details_form.is_valid():
            # Update user's profile with cleaned data from forms
            user = personal_details_form.save(commit=False)  # Get the user instance

            # Update personal details
            user.username = personal_details_form.cleaned_data.get('username')
            user.first_name = personal_details_form.cleaned_data.get('first_name')
            user.last_name = personal_details_form.cleaned_data.get('last_name')
            user.Date_of_birth = personal_details_form.cleaned_data.get('Date_of_birth')
            user.save()  # Save changes to user

            # Get the profile instance related to this user
            profile = Profile.objects.get(user=user)  # Assuming one-to-one relationship
            profile.profile_picture = personal_details_form.cleaned_data.get('profile_picture', profile.profile_picture)  # Keep existing if not updated
            profile.save()  

            # Update professional details
            user.emp_id = professional_details_form.cleaned_data.get('emp_id')
            user.designation = professional_details_form.cleaned_data.get('designation')
            user.expertise = professional_details_form.cleaned_data.get('expertise')
            user.Date_of_joining = professional_details_form.cleaned_data.get('Date_of_joining')
            
            # Save any other professional details if necessary
            professional_details_form.instance = user  # Assign the user instance to the form
            professional_details_form.save()  # Save professional details

            # Redirect to the user's profile page
            return redirect('dashboard')  # Redirect to the dashboard

    else:
        # If not a POST request, render forms with the current user's data
        personal_details_form = PersonalDetailsForm(instance=user)
        professional_details_form = ProfessionalDetailsForm(instance=user)

    # Provide the forms to the template
    return render(request, 'user_update.html', {
        'personal_details_form': personal_details_form,
        'professional_details_form': professional_details_form,
    })



@login_required
def user_delete(request, pk):
    user = get_user_model().objects.get(pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('register')
    return render(request, 'user_delete.html', {'user': user})

def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request, pk=None):
    if pk is None:
        pk = request.user.pk
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        department = Department.objects.get(id=1)
        profile = Profile(user=user, department=department)
        profile.save()
    print("Profile retrieved:", profile)

    # Retrieve the user's enrolled courses
    enrolled_courses = UserEnrollment.objects.filter(user=user, course__isnull=False)

    # Retrieve the user's certifications
    user_certifications = UserEnrollment.objects.filter(user=user, certification__isnull=False)

    # Initialize progress bars for courses and certifications
    course_progress_bars = []
    certification_progress_bars = []

    # Calculate progress for each course
    for course in enrolled_courses:
        progress = course.course_progress
        if progress is None:
            progress = 0
        course_progress_bars.append({
            'course': course.course,
            'progress': progress,
            'completed': course.course_completed_at is not None
        })

    # Calculate progress for each certification
    for certification in user_certifications:
        progress = certification.certification_progress
        if progress is None:
            progress = 0
        certification_progress_bars.append({
            'certification': certification.certification,
            'progress': progress,
            'completed': certification.certification_completed_at is not None
        })

    dashboard_data = {
        'user': user,
        'profile': profile,
        'enrolled_courses': enrolled_courses,
        'user_certifications': user_certifications,
        'course_progress_bars': course_progress_bars,
        'certification_progress_bars': certification_progress_bars
    }

    return render(request, 'dashboard.html', dashboard_data)


@receiver(post_save, sender=UserEnrollment)
def update_user_enrollment(sender, instance, created, **kwargs):
    if not created and instance.course_completed_at is None and instance.certification_completed_at is None:
        if instance.course_progress == 100:
            instance.course_completed_at = timezone.now()
            instance.save()
        elif instance.certification_progress == 100:
            instance.certification_completed_at = timezone.now()
            instance.save()

@login_required
def update_course_progress(request, course_id):
    course = Course.objects.get(id=course_id)
    user_enrollment = UserEnrollment.objects.get(user=request.user, course=course)
    if request.method == 'POST':
        form = UserCourseForm(request.user, request.POST, instance=user_enrollment)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserCourseForm(request.user, instance=user_enrollment)
    return render(request, 'course_update.html', {'form': form})

@login_required
def update_certification_progress(request, certification_id):
    certification = Certification.objects.get(id=certification_id)
    user_enrollment = UserEnrollment.objects.get(user=request.user, certification=certification)
    if request.method == 'POST':
        form = UserCertificationForm(request.user, request.POST, instance=user_enrollment)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserCertificationForm(request.user, instance=user_enrollment)
    return render(request, 'certificate_update.html', {'form': form})

def help(request):
    return render(request,'help.html')

@login_required
def leaderboard(request):
    User = get_user_model()
    users = User.objects.prefetch_related('userenrollment_set').annotate(
        num_certifications=Count('userenrollment__certification'),
        num_courses=Count('userenrollment__course')
    ).order_by('-num_certifications', '-num_courses')  # Initial order

    leaderboard = []
    for user in users:
        user_enrollments = user.userenrollment_set.all()  # Retrieve all enrollments
        
        # Create an entry for the user
        user_entry = {
            'username': user.username,
            'name': user.first_name + ' ' + user.last_name,
            'num_certifications': user.num_certifications,
            'num_courses': user.num_courses,
            'certifications': [],
            'courses': []
        }

        # Collect certifications
        for user_enrollment in user_enrollments:
            if user_enrollment.certification:
                user_entry['certifications'].append({
                    'name': user_enrollment.certification.name,
                    'date_completed': user_enrollment.certification_completed_at
                })

            if user_enrollment.course:
                user_entry['courses'].append({
                    'name': user_enrollment.course.name,
                    'date_completed': user_enrollment.course_completed_at
                })

        # Add the user's data to the leaderboard
        leaderboard.append(user_entry)

    # Sort the leaderboard based on the defined criteria
    leaderboard.sort(key=lambda x: (
        -x['num_certifications'],
        min(cert['date_completed'] for cert in x['certifications']) if x['certifications'] else float('inf'),
        -x['num_courses'],
        min(course['date_completed'] for course in x['courses']) if x['courses'] else float('inf')
    ))

    # Assign ranks
    for i, user_entry in enumerate(leaderboard):
        user_entry['rank'] = i + 1

    # Render the leaderboard with detailed information
    return render(request, 'leaderboard.html', {'leaderboard': leaderboard})


@login_required
def update_user_score(request):
    user_profile = request.user.profile  # Get the user's profile
    current_time = timezone.now()

    # Set last_login_time if it's not set
    if user_profile.last_login_time is None:
        user_profile.last_login_time = current_time
        user_profile.save()  # Save the profile to update the field

    # Check if score refresh is needed (every 7 days)
    if current_time >= user_profile.last_login_time + timedelta(days=7):
        user_profile.score = 0  # Reset score to 0 after 7 days
        user_profile.last_login_time = current_time  # Update last_login_time
        user_profile.save()  # Save changes
        return  # Exit early to avoid score calculation

    active_time = (current_time - user_profile.last_login_time).total_seconds() / 60  # Active time in minutes

    # Calculate score based on active time
    if active_time <= 5:
        score_increase = min(active_time, 5)  # Cap the score increase at 5
        user_profile.score += score_increase
    else:
        user_profile.score -= (active_time - 5)
        user_profile.score = max(user_profile.score, 0)

    # Ensure the score is within the range of 100 to 1000
    if user_profile.score < 100:
        user_profile.score = 100  # Minimum score
    elif user_profile.score > 1000:
        user_profile.score = 1000  # Maximum score

    # Update last login time
    user_profile.last_login_time = current_time
    user_profile.save()  # Save changes to the database

    # Fetch all profiles and order them by score in descending order
    profiles = Profile.objects.all().order_by('-score')

    leaderboard = []
    for index, profile in enumerate(profiles):
        leaderboard.append({
            'rank': index + 1,  # Rank starts at 1
            'username': profile.user.username,
            'score': profile.score,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else static('home/default-img.jpg'),  # Use static function
        })

    # Render the leaderboard template with the user profile score and the leaderboard data
    return render(request, 'leaderboard1.html', {'score': user_profile.score, 'leaderboard': leaderboard})



@login_required
def floating_button_view(request):
    return redirect('bingo')

@login_required
def bingo(request):
    games = [
        {'name': 'Tower Of Hanoi', 'image': 'game_hub/tower_of_hanoi.jpg', 'description': 'Play as towerofhanoi and use your brain!', 'url': 'towerofhanoi.html'},
        {'name': 'Snake', 'image': 'snake.jpg', 'description': 'Classic snake game, eat and grow!', 'url': 'snake.html'},
        {'name': 'Hangman', 'image': 'hangman1.jpeg', 'description': 'Guess the word correctly!', 'url': 'Hangman.html'},
        {'name': 'Sudoku', 'image': 'sudoku-hero.png', 'description': 'Challenge your mind!', 'url': 'sudoko.html'},
        {'name': 'Tic Tac Toe', 'image': 'TicTacToe (2).jpg', 'description': 'Classic game for two players!', 'url': 'Tic Tac Toe.html'},
        {'name': 'Math Cards', 'image': 'matchcards.jpg', 'description': 'Test your math skills!', 'url': 'matchcard.html'},
        {'name': 'Quiz Time', 'image': 'quiztime (1).jpg', 'description': 'How many questions can you answer?', 'url': 'Quiz.html'},
        {'name': 'Rock Paper Scissors', 'image': 'rockpaperscissors.jpg', 'description': 'Challenge an AI!', 'url': 'Rockpaperscissors.html'},
        {'name': 'Guess the Word', 'image': 'guess-the-word.jpg', 'description': 'Can you guess the right word?', 'url': 'numberguess.html'},
    ]
    update_user_score(request)

    return render(request, 'bingo.html', {'games': games})
def towers_of_hanoi(request):
    update_user_score(request)
    return render(request,'towersofhanoi.html')
def snake(request):
    update_user_score(request)
    return render(request,'snake.html')
def hangman(request):
    update_user_score(request)
    return render(request,'hangman.html')
def sudoku(request):
    update_user_score(request)
    return render(request,'sudoku.html')
def memory(request):
    update_user_score(request)
    return render(request,'memory.html')
def quiz(request):
    update_user_score(request)
    return render(request,'quiz.html')
def guess(request):
    update_user_score(request)
    return render(request,'guess.html')
def chess(request):
    update_user_score(request)
    return render(request,'chess.html')
def mathsprint(request):
    update_user_score(request)
    return render(request,'mathsprint.html')


logging.basicConfig(level=logging.ERROR)

@login_required
def send_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST, user=request.user)

        if form.is_valid():
            email = form.save(commit=False)
            email.From = request.user  # Set the sender
            email.sent = False  # Initial state; won't mark as sent until finalized
            email.message = form.cleaned_data['message']  # Get email message from cleaned data

            # Save the email to get the ID before assigning CC/BCC
            email.save()

            # Save CC and BCC fields
            cc_users = form.cleaned_data.get('cc_users', [])
            bcc_users = form.cleaned_data.get('bcc_users', [])
            email.cc_users.set(cc_users)  # Save CC users
            email.bcc_users.set(bcc_users)  # Save BCC users

            # Check if the user wants to finalize and send the email
            if email.message:  # Ensure there is a message to send
                return finalize_and_send_email(request, email, form)  # Call to send function

            # Render the email form with the content ready for customization
            return render(request, 'email_form.html', {
                'form': form,
                'message': email.message,  # Pass the message for the user to edit
                'is_template': bool(request.POST.get('template_type')),
                'is_generated': bool(request.POST.get('use_generated_text'))
            })

        else:
            return render(request, 'email_form.html', {'form': form, 'error': 'Please correct the errors.'})

    else:
        # Handle GET requests
        message = request.GET.get('message')
        template_content = request.GET.get('template_content')
        if message:
            form = EmailForm(initial={'message': message})
        elif template_content:
            form = EmailForm(initial={'message': template_content})
        else:
            form = EmailForm(user=request.user)
        
        return render(request, 'email_form.html', {'form': form})



def get_email_message(request):
    """
    Generates the email message content based on user selection.
    Returns the customized content for the email message.
    """
    # Check for template selection
    if request.POST.get('template_type'):
        try:
            template = Template.objects.get(template_type=request.POST.get('template_type'))
            return template.content  # Use the selected template's content
        except Template.DoesNotExist:
            logger.error('Template not found.')
            messages.error(request, 'Template not found.')
            return ''

    # Check for AI generated text
    elif request.POST.get('use_generated_text'):
        generated_text = request.session.get('generated_text', '')
        if generated_text:
            return generated_text
        else:
            messages.error(request, 'No generated text available.')
            return ''

    # Fallback if GET parameters are present
    elif request.GET.get('message'):
        message_content = request.GET.get('message', '')
        # Check for customization options
        if request.GET.get('customize_message'):
            customization = request.GET.get('customize_message')
            message_content = customize_message_content(message_content, customization)
        return message_content

    elif request.GET.get('template_content'):
        template_content = request.GET.get('template_content', '')
        # Check for customization options
        if request.GET.get('customize_content'):
            customization = request.GET.get('customize_content')
            template_content = customize_message_content(template_content, customization)
        return template_content

    return ''

def customize_message_content(original_content, customization):
    """
    Customizes the original content based on the provided customization input.
    Returns the customized content.
    """
    return original_content.replace("{customization_placeholder}", customization)

@login_required
def inbox(request):
    emails = Email_Message.objects.filter(TO=request.user).prefetch_related('replies')
    return render(request, 'inbox.html', {'emails': emails})

@login_required
def sent_items(request):
    emails = Email_Message.objects.filter(From=request.user).prefetch_related('replies')
    return render(request, 'sent_items.html', {'emails': emails})


@login_required
def outbox(request):
    emails = request.user.sent_emails.filter(deleted=False)
    return render(request, 'sent_items.html', {'emails': emails})


@login_required  # Ensure you import your model
def drafts(request):
    User = get_user_model()
    if request.method == 'POST':
        form_data = request.POST

        # Check if this is an edit or a new draft
        draft_id = form_data.get('draft_id')  # Add field for draft ID to identify edits
        
        if draft_id:  # Editing an existing draft
            email = get_object_or_404(Email_Message, id=draft_id, From=request.user, sent=False)
            # Update the existing draft
            email.TO = get_object_or_404(User, id=form_data['to_user_id'])  # Ensure a valid recipient
            email.subject = form_data['subject']
            email.message = form_data['message']
            email.sent = False  # Ensure the draft status remains false
            email.save()
            return JsonResponse({'success': True, 'message': 'Draft updated successfully!'})

        else:  # Creating a new draft
            to_user_id = form_data.get('to_user_id')
            to_user = get_object_or_404(User, id=to_user_id)

            email = Email_Message(
                From=request.user,
                TO=to_user,
                subject=form_data['subject'],
                message=form_data['message'],
                sent=False  # Default sent status to False for a new draft
            )
            email.save()
            return JsonResponse({'success': True})

    return render(request, 'drafts.html')
    
def save_draft(request):
    return render(request,'drafts.html')

@login_required
def deleted_items(request):
    emails = Email_Message.objects.filter(Q(TO=request.user) | Q(From=request.user), deleted=True)
    return render(request, 'deleted_items.html', {'emails': emails})

@login_required
def email_sent(request, TO_email):
    return render(request, 'email_sent.html', {'TO_email': TO_email})

@login_required
def email_detail(request, pk):
    email = Email_Message.objects.get(id=pk)
    if email.TO == request.user:
        return render(request, 'email_detail.html', {'email': email})
    elif email.From == request.user:
        return render(request, 'email_detail.html', {'email': email})
    else:
        return redirect('inbox')

@login_required
def email_delete(request, pk, next_url=None):
    # Fetch the email object by primary key
    email = get_object_or_404(Email_Message, id=pk)

    # Check if the email belongs to the current user
    if email.From == request.user or email.TO == request.user:  # Allow deletion if the user is the sender or receiver
        if request.method == 'POST':
            email.delete()  # Delete the email
            messages.success(request, 'Email deleted successfully.')
            if next_url:
                return redirect(next_url)  # Redirect to the specified URL
            else:
                return redirect('inbox')  # Default to Inbox if no URL is specified
    else:
        messages.error(request, 'You do not have permission to delete this email.')
        return redirect('inbox')  # Redirect to Inbox if the user does not have permission

    # Render the delete confirmation page if not a POST request
    return render(request, 'email_delete.html', {'email': email}) 

@login_required
def reply_email(request, pk):
    email = Email_Message.objects.get(id=pk)
    if request.method == 'POST':
        form = ReplyEmailForm(request.POST)
        if form.is_valid():
            reply_message = form.cleaned_data['message']
            reply_email_message = Email_Message(
                subject=f'Re: {email.subject}',
                message=reply_message,
                From=request.user,
                TO=email.From,
                replied_to=email
            )
            try:
                reply_email_message.sent = True
                reply_email_message.save()
                # Send the reply email using the custom email backend
                connection = get_connection(backend='app.custom_email_backend.CustomEmailBackend')
                email_message = EmailMessage(
                    subject=reply_email_message.subject,
                    body=reply_email_message.message,
                    from_email=reply_email_message.From.email,
                    to=[reply_email_message.TO.email]
                )
                email_message.connection = connection
                connection.send_messages([email_message], request=request)
                return redirect('sent_items')
            except ImproperlyConfigured as e:
                print(f"Error sending reply email: {e}")
                return render(request, 'reply_email.html', {'form': form, 'error': 'Error sending reply email', 'email': email})
            except Exception as e:
                print(f"Error sending reply email: {e}")
                return render(request, 'reply_email.html', {'form': form, 'error': 'Error sending reply email', 'email': email})
        else:
            return render(request, 'reply_email.html', {'form': form, 'email': email})    
    else:
        form = ReplyEmailForm()
        return render(request, 'reply_email.html', {'form': form, 'email': email})

@login_required
def reply_emails(request):
    reply_emails = Email_Message.objects.filter(TO=request.user, replied_to__isnull=False)
    return render(request, 'replies.html', {'reply_emails': reply_emails})
    
logger = logging.getLogger(__name__)
@login_required
def generate_ai_response(request):
    if request.method == 'GET':
        return render(request, 'generate_ai.html', {'generated_text': '', 'subject': ''})

    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        regenerate = bool(request .POST.get('regenerate'))
        generated_text = generate_email_response_function(prompt, regenerate)
        subject = "Generated Email"
        request.session['generated_text'] = generated_text
        return render(request, 'generate_ai.html', {'generated_text': generated_text, 'subject': subject, 'prompt': prompt})
        
    return HttpResponse('Invalid request')

@login_required
def email_response(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        prompt = f'Subject: {subject}\nMessage: {message}'
        generated_text = generate_email_response_function(prompt)
        if request.POST.get('use_generated_text'):
            message = generated_text
        form = EmailForm(request.POST, user=request.user, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email sent successfully!')
            return redirect('sent_items')  # Redirect to the email list view
    else:
        message = request.GET.get('message', '')
        form = EmailForm(initial={'message': message}, user=request.user, request=request)
    return render(request, 'email_form.html', {'form': form, 'generated_text': '', 'subject': '', 'message': message})


def templates_view(request):
    # Fetch all parent template types and their associated child types and templates
    parent_template_types = ParentTemplateType.objects.prefetch_related(
        'childtemplatetype_set__template_set'
    ).all()

    template_data = []
    for parent_type in parent_template_types:
        child_data = []
        for child_type in parent_type.childtemplatetype_set.all():
            templates = child_type.template_set.all()  # Use reverse relation to fetch templates
            child_data.append({
                'id': child_type.id,
                'name': child_type.name,
                'templates': [{'id': template.id, 'name': template.name, 'content': template.content} for template in templates]  # Include content here if you wish
            })
        template_data.append({
            'parent_type': parent_type,
            'child_types': child_data
        })

    return render(request, 'templates.html', {'template_data': template_data})

def get_child_template_types(request, parent_template_type_id):
    # Fetch child template types based on parent template type ID and return JSON
    child_template_types = ChildTemplateType.objects.filter(parent_template_type_id=parent_template_type_id).values('id', 'name')
    return JsonResponse(list(child_template_types), safe=False)

def get_templates(request, child_template_type_id):
    # Fetch templates based on child template type ID and return JSON
    templates = Template.objects.filter(child_template_type_id=child_template_type_id).values('id', 'name', 'content') 
    return JsonResponse(list(templates), safe=False)

@login_required
def schedule_email(request):
    if request.method == 'POST':
        form = ScheduledEmailForm(request.POST)
        if form.is_valid():
            scheduled_email = form.save(commit=False)
            scheduled_email.From = request.user
            scheduled_email.save()
            receivers = form.cleaned_data['receivers']
            scheduled_email.receivers.set(receivers)
            return redirect('scheduled_emails')
    else:
        form = ScheduledEmailForm()
    return render(request, 'schedule_email.html', {'form': form})

@login_required
def scheduled_emails(request):
    scheduled_emails = ScheduledEmail.objects.filter(From=request.user)
    return render(request, 'scheduled_emails.html', {'scheduled_emails': scheduled_emails})

@login_required
def schedule_email_view(request):
    users = User.objects.all()  # retrieve the list of users
    context = {'users': users}
    return render(request, 'schedule_email.html', context)

def send_scheduled_email(request, pk):
    scheduled_email = ScheduledEmail.objects.get(id=pk)
    if scheduled_email.sent:
        return redirect('scheduled_emails')
    email_message = EmailMessage(
        subject=scheduled_email.subject,
        body=scheduled_email.message,
        from_email=request.user.email,  # Set From email to current user's email
        to=[receiver.email for receiver in scheduled_email.receivers.all()],
        cc=[cc_user.email for cc_user in scheduled_email.cc_users.all()],
        bcc=[bcc_user.email for bcc_user in scheduled_email.bcc_users.all()]
    )
    try:
        connection = get_connection(backend='accounts.custom_email_backend.CustomEmailBackend')
        email_message.connection = connection
        connection.send_messages([email_message], request=request)
        scheduled_email.sent = True
        scheduled_email.save()
        return redirect('scheduled_emails')
    except ImproperlyConfigured as e:
        # Handle email sending failure due to improperly configured backend
        print(f"Error sending email: {e}")
        form = ScheduledEmailForm(user=request.user)
        return render(request, 'schedule_email.html', {'form': form, 'error': 'Error sending email'})
    except Exception as e:
        # Handle other email sending failures
        print(f"Error sending email: {e}")
        form = ScheduledEmailForm(user=request.user)
        return render(request, 'schedule_email.html', {'form': form, 'error': 'Error sending email'})

@login_required
def send_reminder_email(request, pk):
    scheduled_email = ScheduledEmail.objects.get(id=pk)
    try:
        reminder_email = ReminderEmail.objects.get(scheduled_email=scheduled_email)
    except ReminderEmail.DoesNotExist:
        reminder_email = ReminderEmail(scheduled_email=scheduled_email)
        reminder_email.save()

    if request.method == 'POST':
        form = ReminderEmailForm(request.POST, instance=reminder_email)
        if form.is_valid():
            form.save()
            email_message = EmailMessage(
                subject=f'Reminder: {scheduled_email.subject}',
                body=f'Reminder: {scheduled_email.message}',
                from_email=scheduled_email.From.email,
                to=[receiver.email for receiver in scheduled_email.receivers.all()]
            )
            try:
                connection = EmailBackend(
                    host='your_host',
                    port='your_port',
                    username='your_username',
                    password='your_password',
                    use_tls=True
                )
                email_message.connection = connection
                connection.send_messages([email_message], request=request)
                reminder_email.sent = True
                reminder_email.save()
                return redirect('scheduled_emails')
            except Exception as e:
                # Handle email sending failure
                print(f"Error sending reminder email: {e}")
                return render(request, 'reminder_email.html', {'form': form, 'error': 'Error sending reminder email'})
    else:
        form = ReminderEmailForm(instance=reminder_email)

    return render(request, 'reminder_email.html', {'form': form})

login_required
def view_scheduled_emails(request):
    """
    View to display the scheduled emails for the current user.
    """
    # Get the scheduled emails for the current user
    scheduled_emails = ScheduledEmail.objects.filter(user=request.user)

    # Render the scheduled_emails.html template with the scheduled emails
    return render(request, 'scheduled_emails.html', {'scheduled_emails': scheduled_emails})


