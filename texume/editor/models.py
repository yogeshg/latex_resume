import logging
import datetime as dt
import textwrap
import os

from django.db import models
from django.contrib.auth.models import User as AuthUser
# Create your models here.

MIN_DATE = dt.date(year=2000, month=1, day=1)
ALLOWED_FILE_FORMATS = ["latex", "markdown"]

logger = logging.getLogger(__name__)

class User(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)


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


    def render(self, file_format):
        if file_format not in ALLOWED_FILE_FORMATS:
            raise ValueError(f"{file_format} can be one of {ALLOWED_FILE_FORMATS}")

        if self.formatting == Content.Formatting.ORG_LOC_TITLE_DATE_POINTS:
            _list = self.body.split("\n\n")
            rendered_output = []
            for item in _list:
                org, loc, title, date, description = item.split("\n", 4)
                if file_format == "markdown":
                    rendered_description = "\n".join(
                        ("* " + d) for d in description.split("\n")
                    )
                    rendered_output.append(textwrap.dedent(f"""
                        *{org}* {loc}
                        _{title}_ [{date}]
                    """) + "\n" + rendered_description)
            return "\n\n".join(rendered_output) + "\n\n"
        elif self.formatting == Content.Formatting.DATE_POINTS:
            _list = self.body.split("\n\n")
            rendered_output = []
            for item in _list:
                date, description = item.split("\n", 1)
                rendered_description = "; ".join(description.split("\n"))
                if file_format == "markdown":
                    rendered_output.append(f"* [{date}] {rendered_description}")
            return "\n".join(rendered_output) + "\n"
        else:
            if file_format == "markdown":
                return self.body + "\n"
            else:
                return "\n"

        self.formatting
    


class TexFormats:

    @staticmethod
    def load_template(filename):
        full_filename = os.path.join("editor/templates/editor/", filename)
        with open(full_filename, "r") as f:
            return f.read()

    @staticmethod
    def format_header(**kwargs):
        template = TexFormats.load_template("header.template.tex")
        replace_words = {
            "NAME": Content.Section.NAME,
            "PHONE": Content.Section.PHONE,
            "POSTMAIL": Content.Section.POSTMAIL,
            "EMAIL": Content.Section.EMAIL,
            "LINK": Content.Section.LINK,
        }
        for word, section in replace_words.items():
            template = template.replace(word, kwargs.get(section, word))

        return template

class Resume:

    SECTION_CHOICES = [s for s, _ in Content.Section.choices]
    HEADER_SECTIONS = ["Name", "Link", "Phone", "Email", "Postmail"]

    def __init__(self, user: AuthUser):
        self.user = user
        self._all_latest_content = None

    def refresh(self):
        self._all_latest_content = None

    @property
    def all_latest_content(self):
        if self._all_latest_content is None:
            self._fetch_latest_content()
        return self._all_latest_content

    @property
    def last_updated(self):
        last_updated = MIN_DATE
        for _, content in self.all_latest_content.items():
            if content.created is not None and content.created > last_updated:
                last_updated = content.created
        return last_updated

    def render(self, file_format):
        if file_format not in ALLOWED_FILE_FORMATS:
            raise ValueError(f"{file_format} can be one of {ALLOWED_FILE_FORMATS}")

        header_info = {
            section: self.all_latest_content.get(section).body
            for section in self.HEADER_SECTIONS
        }

        if file_format == "latex":
            rendered_resume = TexFormats.format_header(**header_info)
        else:
            print(header_info)
            rendered_resume = textwrap.dedent("""
                *{Name}*
                {Phone}
                {Email}
                {Postmail}
                {Link}
                """).format(**header_info)


        for section, content in self.all_latest_content.items():
            if section not in self.HEADER_SECTIONS:
                content.body, content.formatting
                rendered_resume += f"{section}\n" + content.render(file_format)

        return rendered_resume
    

    def _fetch_latest_content(self):
        self._all_latest_content = {
            s: latest_content(self.user, s) for s in self.SECTION_CHOICES
        }

def latest_content(user: AuthUser, section: str) -> Content:
    user = User.objects.get(user=user)
    content = (
        Content.objects
            .filter(user=user)
            .filter(section__exact=section)
        )
    logger.info("latest section found for user ({}, {}, {}, {})".format(
        content.exists(), user, type(user), section
        ))
    if content.exists():
        return content.latest('created')
    else:
        return Content(user=user, section=section)


from model_mommy import mommy
from django.test import TestCase


class ContentTestCase(TestCase):

    def setUp(self):
        self._content_a = Content(
            formatting = Content.Formatting.ORG_LOC_TITLE_DATE_POINTS,
            body=textwrap.dedent("""
                some organisation
                amazing place
                domain ninja
                2019-01-23
                did amazing things
                organized cool stuff

                some organisation
                same place
                leader
                2018-10-23
                cool things here as well
                """).strip()
            )
        self._content_b = Content(
            formatting = Content.Formatting.DATE_POINTS,
            body=textwrap.dedent("""
                2019-01-23
                did amazing things
                organized cool stuff

                2018-10-23
                cool things here as well
                """).strip()
            )
        self._content_c = Content(
            formatting = Content.Formatting.TEXT,
            body=textwrap.dedent("""
                * 2019-01-23: did amazing things; organized cool stuff
                * 2018-10-23: cool things here as well
                """).strip()
            )

    def test_formatting(self):
        for file_format in ALLOWED_FILE_FORMATS:
            print(self._content_a.render(file_format))
            print(self._content_b.render(file_format))
            print(self._content_c.render(file_format))


class ResumeTestCase(TestCase):

    def setUp(self):
        self._new_content = mommy.make(Content)
        self._new_user = mommy.make(User)

    def test_creation(self):
        rr = Resume(user=self._new_user.user)

    def test_all_content(self):
        rr = Resume(user=self._new_user.user)
        for section, content in rr.all_latest_content.items():
            self.assertEquals(content.body, "")
        rr = Resume(user=self._new_content.user.user)
        self.assertIn(self._new_content, rr.all_latest_content.values())

    def test_last_updated(self):
        rr = Resume(user=self._new_user.user)
        self.assertEquals(MIN_DATE, rr.last_updated)
        rr = Resume(user=self._new_content.user.user)
        self.assertEquals(self._new_content.created, rr.last_updated)

    def test_render(self):
        rr = Resume(user=self._new_content.user.user)
        for file_format in ALLOWED_FILE_FORMATS:
            print(rr.render(file_format))
