"""pyjudge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'login/',
        auth_views.LoginView.as_view(),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("", ListContestView.as_view()),
    path("panel/", admin_panel_view),
    path("profile/", profile_view),

    path("contest/create/", CreateContestView.as_view()),
    path("contest/<int:pk>/edit/", UpdateContestView.as_view()),
    path("contest/<int:pk>/delete/", DeleteContestView.as_view()),
    path("contest/<int:contest>/", ListTaskView.as_view()),

    path("task/create/", CreateTaskView.as_view()),
    path("task/<int:pk>/edit/", UpdateTaskView.as_view()),
    path("task/<int:pk>/delete/", DeleteTaskView.as_view()),
    path("task/<int:pk>/", DetailTaskView.as_view()),
    path("task/<int:pk>/submit/", SubmitSolutionView.as_view()),

    path("test/create/", CreateTestView.as_view()),
    path("test/<int:pk>/delete/", DeleteTestView.as_view()),
    path("test/<int:pk>/edit/", UpdateTestView.as_view()),

    path("solution/<int:pk>/", DetailSolutionView.as_view()),



]
