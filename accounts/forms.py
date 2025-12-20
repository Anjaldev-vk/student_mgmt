from django import forms
from .models import User
from students.models import Enrollment, Course

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'phone',
            'date_of_birth',
            'profile_picture',
        ]

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'phone',
            'date_of_birth',
            'profile_picture',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class EnrollmentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=False),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'status']

class StudentProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'date_of_birth',
            'profile_picture',
        ]

