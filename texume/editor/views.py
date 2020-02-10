from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Content


@login_required
def index(request):
    user_content = Content.objects.filter(user_id__exact=request.user.id)
    return render(
        request, "editor/form.html", {"user_content": user_content}
    )
