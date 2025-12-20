from django.urls import path
from . import views

urlpatterns = [

    path('student_dashboard/',views.Student_dashboard,name='student_dashboard'),
    path('profile/',views.Student_profile,name='student_profile'),
    path('course/',views.Student_course,name='student_course'),
    path('course/enroll/<int:course_id>/', views.student_enroll_request, name='student_enroll_request'),
    path('course/watch/<int:course_id>/', views.watch_course, name='watch_course'),
    path('course/update-status/<int:course_id>/<str:status>/', views.update_course_status, name='update_course_status')
]
