from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        context_dict = {}
        return render(request, "fittrack/index.html", context=context_dict)


@login_required
def dashboard(request):
    context = {"username": request.user.username}
    return render(request, "fittrack/dashboard.html", context)

