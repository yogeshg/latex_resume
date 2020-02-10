from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Content(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Section(models.TextChoices):
        NAME = "Name"
        LINK = "Link"
        PHONE = "Phone"
        EMAIL = "Email"
        POSTMAIL = "Postmail"
        EDUCATION = "Education"
        PROFESSIONAL_EXPERIANCE = "Professional Experience"
        PROJECT_WORK = "Project Work"
        PUBLICATIONS = "Publications"
        COURSES = "Courses"
        TECHNICAL_SKILLS = "Technical Skills"
        EXTRA_CURRICULAR = "Extra Curricular"
    
    section = models.CharField(max_length=128, choices=Section.choices)

    body = models.TextField()

    class Formatting(models.TextChoices):
        ORG_LOC_TITLE_DATE_POINTS = "org-loc-title-date-points"
        DATE_POINTS = "date-points"
        TEXT = "text"

    formatting = models.CharField(
        max_length=128,
        choices=Formatting.choices,
        default=Formatting.TEXT
    )

    created = models.DateField(auto_now_add=True)


