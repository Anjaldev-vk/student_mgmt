from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from students.forms import CourseForm
from .models import User
from .forms import RegisterForm, StudentForm, EnrollmentForm
from django.shortcuts import get_object_or_404
from students.models import Enrollment, Course
from django.db.models import Q
from django.core.paginator import Paginator
from student_mgmt.settings import EMAIL_HOST_USER
from django.core.mail import send_mail


# This is my home view
def home_view(request):
    return render(request, "home.html")


# This is my login logic
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect("admin_base")
            else:
                return redirect("student_base")

        messages.error(request, "Invalid username or password")

    context = {'hide_navbar': True} 
    return render(request, "login.html", context)



# This view Logout the user and redirects to the login page
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully",extra_tags='logout_msg')
    return redirect("login")


# This view help me to Handles user registration and saves a new account
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_staff = False
            user.save()

            send_mail(
                subject="Welcome to Student Management System",
                message=f"Dear {user.username},\n\nWelcome to our Student Management System. Your account has been created successfully.",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            messages.success(request, "Account created successfully")
            return redirect("login")
    else:
        form = RegisterForm()
    

    return render(request, "register.html", {"form": form, "hide_navbar": True})


# Displays admin dashboard stats for staff users
@login_required
def admin_base(request):
    if not request.user.is_staff:
        return redirect("login")
    

    total_students = User.objects.filter(is_staff=False).count()
    total_staff = User.objects.filter(is_staff=True).count()
    recent_students = User.objects.filter(is_staff=False).order_by('-date_of_join')[:5]
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    context = {
        'total_students': total_students,
        'total_staff': total_staff,
        'recent_students': recent_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
    }
    
    return render(request, "admin/dashboard/dashboard.html", context)


# This view Shows the student dashboard for non-staff users
@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect("login")
        
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    context = {
        'enrollments': enrollments,
        'enrolled_count': enrollments.count(),
        'active_count': enrollments.exclude(status='Completed').count(),
        'completed_count': enrollments.filter(status='Completed').count(),
    }
    return render(request, "student_dashboard/student_dashboard.html", context)




@login_required
def student_list(request):
    if not request.user.is_staff:
        return redirect("login")
        
    students = User.objects.filter(is_staff=False).order_by('-date_of_join')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        students = students.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        
    # Pagination
    paginator = Paginator(students, 7) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "admin/students/list.html", {"students": page_obj, "query": query})


# Handles adding a new student through the admin panel
@login_required
def student_add(request):
    if not request.user.is_staff:
        return redirect("login")
    
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.save()
            messages.success(request, "Student added successfully")
            return redirect("student_list")
    else:
        form = StudentForm()
    
    return render(request, "admin/students/form.html", {"form": form, "title": "Add Student"})

# Allows staff to edit an existing student's details
@login_required
def student_edit(request, pk):
    if not request.user.is_staff:
        return redirect("login")
        
    student = get_object_or_404(User, pk=pk, is_staff=False)
    
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully")
            return redirect("student_list")
    else:
        form = StudentForm(instance=student)
    
    return render(request, "admin/students/form.html", {"form": form, "title": "Edit Student"})

# Deletes a student account after staff confirmation
@login_required
def student_delete(request, pk):
    if not request.user.is_staff:
        return redirect("login")
        
    student = get_object_or_404(User, pk=pk, is_staff=False)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully")
        
    return redirect("student_list")


# Shows a list of all enrollments for staff users
@login_required
def enrollment_list(request):
    if not request.user.is_staff:
        return redirect("login")
        
    enrollments = Enrollment.objects.all().order_by('-enrolled_at')
    
    # Search functionality
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    if query:
        enrollments = enrollments.filter(
            Q(student__username__icontains=query) |
            Q(student__email__icontains=query) |
            Q(course__title__icontains=query)
        )
    
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)
        
    # Pagination
    paginator = Paginator(enrollments, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "admin/enrollments/list.html", {
        "enrollments": page_obj, 
        "query": query,
        "status_filter": status_filter,
        "status_choices": Enrollment.STATUS_CHOICES
    })

# Allows staff to enroll a student in a course
@login_required
def enrollment_add(request):
    if not request.user.is_staff:
        return redirect("login")
    
    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student enrolled successfully")
            return redirect("enrollment_list")
    else:
        form = EnrollmentForm()
    
    return render(request, "admin/enrollments/form.html", {"form": form, "title": "Enroll Student"})

# Allows staff to cancel a student's enrollment in a course
@login_required
def enrollment_delete(request, pk):
    if not request.user.is_staff:
        return redirect("login")
        
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == "POST":
        enrollment.delete()
        messages.success(request, "Enrollment cancelled successfully")
        
    return redirect("enrollment_list")


@login_required
def enrollment_edit(request, pk):
    if not request.user.is_staff:
        return redirect("login")
        
    enrollment = get_object_or_404(Enrollment, pk=pk)
    
    if request.method == "POST":
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, "Enrollment updated successfully")
            return redirect("enrollment_list")
    else:
        form = EnrollmentForm(instance=enrollment)
        
    return render(request, "admin/enrollments/form.html", {"form": form, "title": "Edit Enrollment"})



# Lists all courses for admin users
@login_required
def admin_course_list(request):
    if not request.user.is_staff:
        return redirect("login")

    courses = Course.objects.all().order_by('-created_at')

    # Search functionality
    query = request.GET.get('q')
    if query:
        courses = courses.filter(title__icontains=query)

    # Pagination
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/courses/list.html", {
        "courses": page_obj,
        "query": query
    })


# Allows staff to add a new course through the admin panel
@login_required
def admin_course_add(request):
    if not request.user.is_staff:
        return redirect("login")

    form = CourseForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_course_list")

    return render(request, "admin/courses/add.html", {
        "form": form
    })


# Allows staff to edit an existing course's details
@login_required
def admin_course_edit(request, pk):
    if not request.user.is_staff:
        return redirect("login")

    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("admin_course_list")

    return render(request, "admin/courses/edit.html", {
        "form": form,
        "course": course
    })


# Allows staff to delete a course from the system
@login_required
def admin_course_delete(request, pk):
    if not request.user.is_staff:
        return redirect("login")

    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return redirect("admin_course_list")
