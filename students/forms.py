from django import forms
from .models import Course, Enrollment


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "course_image",
            "description",
            "video_link",
            "duration",
        ]


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course"]
