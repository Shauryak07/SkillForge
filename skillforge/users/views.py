from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import SignupForm

class UserLoginView(LoginView):
    template_name="users/login.html"

# using default signup view just added a email field as modification
class SignupView(CreateView):
    form_class = SignupForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self,form):
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend") # auto login after the signup
        print("login success")
        return super().form_valid(form)


