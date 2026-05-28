from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .selectors import get_home_context


@login_required
def home(request):
    context = get_home_context()
    context['page_title'] = 'Dashboard'
    return render(request, 'dashboard/home.html', context)
