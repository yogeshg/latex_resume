import logging

from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import Content, User
from editor.forms import PartialContentForm

logger = logging.getLogger("EDITOR")


SECTION_CHOICES = [x for x, _ in Content.Section.choices]

@login_required
def index(request):
    user_sections = [
        {'url': "content/?section={}".format(s), 'section':s}
        for s in SECTION_CHOICES
    ]
    return render(
        request, "editor/form.html", {"user_sections": user_sections}
    )

@login_required
def generate(request):
    """
    GET requests the resume to be colated and generated.
    """
    if request.method == 'GET':
        all_content = {s:_fetch_latest_content(request, s) for s in SECTION_CHOICES}


def _generate_markdown(all_content):
    header_sections = [
        "Name",
        "Link",
        "Phone",
        "Email",
        "Postmail",
    ]
    header_format = """
    {Name}
    {Email} {Link}
    {Phone} {Postmail}
    """

def _generate_section(section, content, formatting):
    if formatting == "org-loc-title-date-points":
        section_header = """
        {org} {loc}
        {title} {date}
        """
        _list = content.split("\n\n")
        item_texts = []
        for item in _list:
            org, loc, title, date, points = item.split("\n", 5)
            # section_header.format(org=org, loc=loc, title=title, date=date)
            item_header = f"""
            {org} {loc}
            {title} {date}
            """
            item_texts.append(item_header + points)
        return "\n".format(item_texts)
    else:
        return content



@login_required
def content(request):
    """
    GET with section=x to request information for that section
    POST with form contents to validate and create new content
    """
    if (
        request.method == 'POST'
        and 'section' in request.POST
        and request.POST['section'] in SECTION_CHOICES
        ):
        content = _fetch_latest_content(request, request.POST['section'])
        form = PartialContentForm(request.POST, instance=content)
        if form.is_valid():
            logging.info("creating record with data: {}".format(form.save(commit=False)))
            form.save()
            return _render_content_form(request, content)
        else:
            return render(request, 'editor/content-form.html', {'form': form})

    elif (
        request.method == 'GET'
        and 'section' in request.GET
        and request.GET['section'] in section_choices
        ):
        content = _fetch_latest_content(request, request.GET['section'])
        return _render_content_form(request, content)

    else:
        raise Http404("""
            GET with section=x to request information for that section
            POST with form contents to validate and create new content
            {} {} {} {}
            """.format(
                request.method,
                request.GET.get("section", "NOTFOUND"),
                request.POST.get("section", "NOTFOUND"),
                section_choices
                ))


def _fetch_latest_content(request, section):
    user = User.objects.get(user=request.user)
    content = (
        Content.objects
            .filter(user=user)
            .filter(section__exact=section)
        )
    logging.info("latest section found for user ({}, {}, {}, {})".format(
        content.exists(), request.user, type(request.user), section
        ))
    if content.exists():
        return content.latest('created')
    else:
        return Content(user=user, section=section)


def _render_content_form(request, content):
    form = PartialContentForm(instance=content)
    return render(request, 'editor/content-form.html', {'form': form})



