import logging

from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import Content, User
from editor.forms import PartialContentForm

logger = logging.getLogger("EDITOR")

@login_required
def index(request):
    user_content = Content.objects.filter(user_id__exact=request.user.id)
    return render(
        request, "editor/form.html", {"user_content": user_content}
    )

@login_required
def content(request):
    """
    GET with section=x to request information for that section
    POST with form contents to validate and create new content
    """
    section_choices = [x for x, _ in Content.Section.choices]
    if (
        request.method == 'POST'
        and 'section' in request.POST
        and request.POST['section'] in section_choices
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



