from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, Enrollment
from accounts.forms import StudentProfileForm




@login_required
def Student_dashboard(request):
    if request.user.is_staff:
        return redirect("login")
    
    
    # Filter only In Progress and Completed courses for the dashboard list and count
    enrollments = Enrollment.objects.filter(
        student=request.user, 
        status__in=['In Progress', 'Completed']
    ).select_related('course')
    
    context = {
        'enrollments': enrollments,
        'enrolled_count': enrollments.count(),
        'active_count': enrollments.filter(status='In Progress').count(),
        'completed_count': enrollments.filter(status='Completed').count(),
    }
    return render(request,'student_dashboard/student_dashboard.html', context)



@login_required
def Student_profile(request):
    if request.user.is_staff:
        return redirect("login")
        
    edit_mode = request.GET.get('edit') == 'true' or request.method == 'POST'
    
    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("student_profile")
    else:
        form = StudentProfileForm(instance=request.user)
        
    return render(request, 'student_profile/student_profile.html', {'form': form, 'edit_mode': edit_mode})



@login_required
def Student_course(request):
    if request.user.is_staff:
        return redirect("login")
        
    courses = Course.objects.all()
    user_enrollments = Enrollment.objects.filter(student=request.user)
    enrollment_status = {e.course_id: e.status for e in user_enrollments}
    
    context = {
        'courses': courses,
        'enrollment_status': enrollment_status,
    }
    return render(request,'student_course/student_course.html', context)


@login_required
def student_enroll_request(request, course_id):
    if request.user.is_staff:
        return redirect("login")
        
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'status': 'Pending'}
    )
    
    if created:
        messages.success(request, f"Enrollment requested for {course.title}. Status: Pending.")
    else:
        messages.info(request, f"You are already enrolled/pending for {course.title}.")
        
    return redirect("student_course")



@login_required
def watch_course(request, course_id):
    if request.user.is_staff:
        return redirect("login")
    
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    
    context = {
        'course': course,
        'enrollment': enrollment,
    }
    return render(request, 'student_course/watch_course.html', context)


@login_required
def update_course_status(request, course_id, status):
    if request.user.is_staff:
        return redirect("login")
        
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    if status == 'Completed':
        enrollment.status = Enrollment.STATUS_COMPLETED
        messages.success(request, f"Congratulations! You completed {course.title}.")
    elif status == 'Dropped':
        enrollment.status = Enrollment.STATUS_DROPPED
        messages.warning(request, f"You have dropped {course.title}.")
    
    enrollment.save()
    return redirect('student_dashboard')
