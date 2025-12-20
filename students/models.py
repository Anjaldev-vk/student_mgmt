from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Course(models.Model):
    title = models.CharField(max_length=200)

    course_image = models.ImageField(
        upload_to="course_images/",
        blank=True,
        null=True
    )

    description = models.TextField()

    video_link = models.URLField(
        blank=True,
        null=True,
        help_text="YouTube video link"
    )


    duration = models.CharField(
        max_length=50
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Enrollment(models.Model):
    STATUS_ENROLLED = "Not Started"
    STATUS_PENDING = "Pending"
    STATUS_IN_PROGRESS = "In Progress"
    STATUS_COMPLETED = "Completed"
    STATUS_DROPPED = "Dropped"

    STATUS_CHOICES = (
        (STATUS_ENROLLED, "Not Started"),
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_DROPPED, "Dropped"),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": False},
        related_name="enrollments"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ENROLLED,
        db_index=True
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ("-enrolled_at",)

    def __str__(self):
        return f"{self.student} → {self.course} ({self.status})"
