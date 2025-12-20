from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.admin_base, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/edit/<int:pk>/', views.student_edit, name='student_edit'),
    path('students/delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/add/', views.enrollment_add, name='enrollment_add'),
    path('enrollments/edit/<int:pk>/', views.enrollment_edit, name='enrollment_edit'),
    path('enrollments/delete/<int:pk>/', views.enrollment_delete, name='enrollment_delete'),
    path('admin/courses/', views.admin_course_list, name='admin_course_list'),
    path('admin/courses/add/', views.admin_course_add, name='admin_course_add'),
    path('admin/courses/edit/<int:pk>/', views.admin_course_edit, name='admin_course_edit'),
    path('admin/courses/delete/<int:pk>/', views.admin_course_delete, name='admin_course_delete'),
]
