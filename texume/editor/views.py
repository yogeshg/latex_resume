import logging

from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, FileResponse, Http404

from .models import Content, User, Resume, latest_content, authuser_is_user
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
    if not authuser_is_user(request.user):
        raise Http404("user does not have a profile, contact admin")
    mode = request.GET.get('mode', 'pdf')
    if mode not in ('latex', 'markdown', 'pdf'):
        raise Http404("invalid mode")
    if request.method == 'GET':
        resume = Resume(request.user)
        output_file = resume.save_latex()
        if mode == 'pdf':
            try:
                response = FileResponse(open(output_file, 'rb'), content_type='application/pdf')
                return response
            except FileNotFoundError:
                raise Http404()
        else:
            rendered = resume.render(mode)
            return render(request, "editor/generated.html", {mode:rendered})

@login_required
def content(request):
    """
    GET with section=x to request information for that section
    POST with form contents to validate and create new content
    """
    if not request.method in ('GET', 'POST'):
        raise Http404("Invalid method: {}".format(request.method))

    if not authuser_is_user(request.user):
        raise Http404("User does not have a profile, contact admin")

    section = getattr(request, request.method).get('section', None)
    if section not in SECTION_CHOICES:
        raise Http404("valid section required")
    content = latest_content(request.user, section)

    if request.method == 'POST':
        form = PartialContentForm(request.POST, instance=content)
        if form.is_valid():
            logging.info("creating record with data: {}".format(form.save(commit=False)))
            form.save()

    form = PartialContentForm(instance=content)
    return render(request, 'editor/content-form.html', {'form': form})



