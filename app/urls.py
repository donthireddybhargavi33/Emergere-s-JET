from django.urls import path
import os
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import warnings
warnings.filterwarnings('ignore')

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.user_list, name='user_list'),
    path('users/<pk>/', views.user_detail, name='user_detail'),
    path('user/<pk>/update/', views.user_update, name='user_update'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('get-sub-departments/<int:department_id>/', views.get_sub_departments, name='get_sub_departments'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/<pk>/', views.dashboard, name='dashboard'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('Game-leaderboard/', views.update_user_score, name='leaderboard1'),
    path('help/', views.help, name='help'),
    path('bingo.html/', views.bingo, name='bingo'),
    path('floating-button/', views.floating_button_view, name='floating_button_view'),
    path('email-form/', views.send_email, name='email_form'),
    path('email/sent/<str:receiver_email>/', views.email_sent, name='email_sent'),
    path('inbox/',views.inbox, name='inbox'),
    path('sent_items/',views.outbox, name='sent_items'),
    path('reply-emails/', views.reply_emails, name='replies'),
    path('drafts/',views.drafts, name='drafts'),
    path('deleted_items/',views.deleted_items, name='deleted_items'),
    path('email-detail/<int:pk>/', views.email_detail, name='email_detail'),
    path('email_delete/<int:pk>/', views.email_delete, name='email_delete'),
    path('email-reply/<int:pk>/', views.reply_email, name='reply_email'),
    path('generate_ai/', views.generate_ai_response, name='generate_ai'),
    path('generate_email_response/', views.email_response, name='generate_email_response'),
    path('email_response/<str:subject>/<str:message>/', views.email_response, name='email_response'),
    path('templates/', views.templates_view, name='templates'),
    path('get-child-template-types/<int:parent_template_type_id>/', views.get_child_template_types, name='get_child_templates'),
    path('get-templates/<int:child_template_type_id>/', views.get_templates, name='get_templates'),
    path('email_form/<str:template_type>/', views.send_email, name='email_form'),
    path('schedule_email/', views.schedule_email, name='schedule_email'),
    path('scheduled_emails/', views.view_scheduled_emails, name='scheduled_emails'),
    path('send_scheduled_email/<pk>/', views.send_scheduled_email, name='send_scheduled_email'),
    path('send_reminder_email/<pk>/', views.send_reminder_email, name='send_remainder_email'),
    path('towers-of-hanoi/',views.towers_of_hanoi,name='towersofhanoi'),
    path('snake/',views.snake,name='snake'),
    path('hangman/',views.hangman,name='hangman'),
    path('sudoku/',views.sudoku,name='sudoku'),
    path('Match-Cards/',views.memory,name='memory'),
    path('Quiz-Time/',views.quiz,name='quiz'),
    path('Word-Guess/',views.guess,name='guess'),
    path('chess/',views.chess,name='chess'),
    path('mathsprint',views.mathsprint,name='mathsprint'),
    









    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)