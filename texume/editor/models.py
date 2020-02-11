import logging
import datetime as dt
import textwrap
import os
import re
from typing import List

from django.db import models
from django.contrib.auth.models import User as AuthUser
# Create your models here.

MIN_DATE = dt.date(year=2000, month=1, day=1)
ALLOWED_FILE_FORMATS = ["markdown", "latex"]

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
        PROFESSIONAL_EXPERIANCE = "Professional Experience" # TODO: typo
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
            _list = _two_line_split(self.body)
            section_kwargs = {
                'ORG': [], 'LOC': [], 'TITLE': [], 'DATE': [], 'ITEMS': []
            }
            for item in _list:
                org, loc, title, date, description = item.split("\n", 4)
                section_kwargs['ORG'].append(org)
                section_kwargs['LOC'].append(loc)
                section_kwargs['TITLE'].append(title)
                section_kwargs['DATE'].append(date)
                section_kwargs['ITEMS'].append(description.split("\n"))

            if file_format == "latex":
                rendered_output = TexFormats.render_section(
                    self.section, self.formatting, **section_kwargs
                )
                return rendered_output
            else: # file_format == "markdown":
                rendered_output = [self.section]

                for i in range(len(_list)):
                    org = section_kwargs['ORG'][i]
                    loc = section_kwargs['LOC'][i]
                    title = section_kwargs['TITLE'][i]
                    date = section_kwargs['DATE'][i]
                    body = [("* " + item) for item in section_kwargs['ITEMS'][i]]
                    body = "\n".join(body)
                    rendered_output.append(textwrap.dedent(f"""
                        *{org}* {loc}
                        _{title}_ [{date}]
                    """) + "\n" + body)

                return "\n\n".join(rendered_output) + "\n\n"

        elif self.formatting == Content.Formatting.DATE_POINTS:
            _list = _two_line_split(self.body)

            if file_format == "latex":
                date_points = [item.split("\n", 1) for item in _list]
                rendered_output = TexFormats.render_section(
                    self.section,
                    self.formatting,
                    DATE_POINTS=date_points
                )
                return rendered_output
            else:  # file_format == "markdown":
                rendered_output = [self.section]
                for item in _list:
                    date, description = item.split("\n", 1)
                    rendered_description = "; ".join(description.split("\n"))
                    rendered_output.append(f"* [{date}] {rendered_description}")
                return "\n".join(rendered_output) + "\n"
        else:
            if file_format == "latex":
                rendered_output = TexFormats.render_section(
                    self.section, self.formatting, BODY=self.body
                )
                return rendered_output
            else:
                return f"{self.section}\n{self.body}\n"

        self.formatting
    


class TexFormats:

    SECTION_COMMANDS = {
        Content.Section.EDUCATION : "education",
        Content.Section.PROFESSIONAL_EXPERIANCE : "professionalExperience",
        Content.Section.PROJECT_WORK : "projectWork",
        Content.Section.PUBLICATIONS : "publications",
        Content.Section.COURSES : "courses",
        Content.Section.TECHNICAL_SKILLS : "technicalSkills",
        Content.Section.EXTRA_CURRICULAR : "extraCurricular",
    }

    def render_section(section: str, formatting: str, **kwargs):
        tex_template = textwrap.dedent(r"""
        \renewcommand{\SECTION}{
            BODY
        }
        """).strip() + "\n\n"
        section = TexFormats.SECTION_COMMANDS[section]
        if formatting == Content.Formatting.ORG_LOC_TITLE_DATE_POINTS:
            subsections_keys = list(kwargs.keys())
            num_subsections = len(kwargs[subsections_keys[0]])
            body = []
            for i in range(num_subsections):
                subsection_kwargs = {k: kwargs[k][i] for k in subsections_keys}
                body.append(TexFormats.format_oltdp(**subsection_kwargs))
            body = "\n".join(body)
            return tex_template.replace('SECTION', section).replace('BODY', body)
        elif formatting == Content.Formatting.DATE_POINTS:
            body = TexFormats.format_datepoints(**kwargs)
            return tex_template.replace('SECTION', section).replace('BODY', body)
        else:
            body = TexFormats.format_body(**kwargs)
            return tex_template.replace('SECTION', section).replace('BODY', body)

    @staticmethod
    def format_oltdp(ORG: str, LOC: str, TITLE: str, DATE: str, ITEMS: List[str]):
        tex_template = r"""
        \OrgLocTitleDate{ORG}{LOC}{TITLE}{DATE}\begin{list2}
            \item {ITEM}
        \end{list2}
        """
        start, sep, end = textwrap.dedent(tex_template).strip().split("\n")
        rendered_output = [start]
        for point in ITEMS:
            rendered_output.append(sep.replace('ITEM', point))
        rendered_output.append(end)
        rendered_output = "\n".join(rendered_output)
        rendered_output = rendered_output.replace('ORG', ORG)
        rendered_output = rendered_output.replace('LOC', LOC)
        rendered_output = rendered_output.replace('TITLE', TITLE)
        rendered_output = rendered_output.replace('DATE', DATE)
        return rendered_output

    @staticmethod
    def format_datepoints(DATE_POINTS: List[List[str]]):
        tex_template = r"""
            \begin{itemize}[leftmargin=0pt,label={}]
                \item \DatePoint{POINT}{DATE}
            \end{itemize}
        """
        start, sep, end = textwrap.dedent(tex_template).strip().split("\n")
        rendered_output = [start]
        for date, point in DATE_POINTS:
            rendered_output.append(sep.replace('DATE', date).replace('POINT', point))
        rendered_output.append(end)
        rendered_output = "\n".join(rendered_output)
        return rendered_output

    @staticmethod
    def format_body(BODY: str):
        return r"{BODY}".replace('BODY', BODY)

    @staticmethod
    def format_header(**kwargs):
        tex_template = r"""
            \newcommand{\phone}{PHONE}
            \newcommand{\postmail}{POSTMAIL}
            \newcommand{\email}{EMAIL}
            \newcommand{\homepage}{\href{LINK}{LINK}}
            \name{\href{LINK}{\Large{NAME}}}
            \address{\phone\\\postmail}
            \address{\hfill\email\\\hfill\homepage}
        """
        tex_template = textwrap.dedent(tex_template).strip() + "\n\n"
        replace_words = {
            "NAME": Content.Section.NAME,
            "PHONE": Content.Section.PHONE,
            "POSTMAIL": Content.Section.POSTMAIL,
            "EMAIL": Content.Section.EMAIL,
            "LINK": Content.Section.LINK,
        }
        for word, section in replace_words.items():
            tex_template = tex_template.replace(word, kwargs.get(section, word))

        return tex_template

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
                rendered_resume += content.render(file_format)

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
            section = Content.Section.PROFESSIONAL_EXPERIANCE,
            formatting = Content.Formatting.ORG_LOC_TITLE_DATE_POINTS,
            body=textwrap.dedent("""
                some organisation
                amazing place
                domain ninja
                2019-01-23
                did amazing things
                organized cool stuff

                another organisation
                same place
                leader
                2018-10-23
                cool things here as well
                """).strip()
            )
        self._content_b = Content(
            section = Content.Section.PROJECT_WORK,
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
            section = Content.Section.COURSES,
            formatting = Content.Formatting.TEXT,
            body=textwrap.dedent("""
                first course, second course, another course,
                yet another course
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

def _two_line_split(text, maxsplit=-1):
    return text.replace("\r\n", "\n").split("\n\n", maxsplit=maxsplit)

def _single_line_split(text, maxsplit=-1):
    return text.replace("\r\n", "\n").split("\n", maxsplit=maxsplit)
