from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from main import bg
from main.models import *
from main import accessor
from main.permissions import *


def error(request, message, label, url):
    return render(request, "base/error.html", ctx(
        "Error",
        msg=message,
        back_text=label,
        back_url=url,
    ))


def confirmation(request, message, yes_text, yes_url, no_text, no_url):
    return render(request, "base/confirmation.html", ctx(
        "Confirm action",
        msg=message,
        yes_text=yes_text,
        yes_url=yes_url,
        no_text=no_text,
        no_url=no_url
    ))


class CreateContestView(LoginRequiredMixin, UserIsAdmin, CreateView):
    template_name = "pages/new_contest.html"
    model = Contest
    fields = ("title", )
    success_url = "/"


class UpdateContestView(LoginRequiredMixin, UserIsAdmin, UpdateView):
    template_name = "pages/edit_contest.html"
    model = Contest
    fields = ("title", "task_ordering")
    success_url = "/"


class ListContestView(LoginRequiredMixin, ListView):
    template_name = "pages/list_contest.html"
    model = Contest


class DeleteContestView(LoginRequiredMixin, UserIsAdmin, DeleteView):
    template_name = "pages/delete_contest.html"
    model = Contest
    success_url = "/"


class CreateTaskView(LoginRequiredMixin, UserIsAdmin, CreateView):
    template_name = "pages/new_task.html"
    model = Task
    fields = ("contest", "title", "description", "max_points", "test_ordering")
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contests"] = Contest.objects.all()
        return context


class UpdateTaskView(LoginRequiredMixin, UserIsAdmin, UpdateView):
    template_name = "pages/edit_task.html"
    model = Task
    fields = ("contest", "title", "description", "max_points", "test_ordering")

    def get_success_url(self):
        return f"/task/{self.object.id}/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tests"] = AutoTest.objects.filter(task=self.object)
        return context


class ListTaskView(LoginRequiredMixin, ListView):
    template_name = "pages/list_task.html"
    model = Task

    def get_queryset(self):
        qs = super().get_queryset()
        return accessor.get_ordered_tasks(Contest.objects.get(id=int(self.kwargs["contest"])))


class DeleteTaskView(LoginRequiredMixin, UserIsAdmin, DeleteView):
    template_name = "pages/delete_task.html"
    model = Task
    success_url = "/"


class CreateTestView(LoginRequiredMixin, UserIsAdmin, CreateView):
    template_name = "pages/new_test.html"
    model = AutoTest
    fields = ("task", "input", "output", "time_limit", "show")
    success_url = "/"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["input"].required = False
        return form

    def get_success_url(self):
        return f"/task/{self.object.task.id}/"


class UpdateTestView(LoginRequiredMixin, UserIsAdmin, UpdateView):
    template_name = "pages/edit_test.html"
    model = AutoTest
    fields = ("task", "input", "output", "time_limit", "show")
    success_url = "/task/"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["input"].required = False
        return form


class DeleteTestView(LoginRequiredMixin, UserIsAdmin, DeleteView):
    template_name = "pages/delete_test.html"
    model = AutoTest
    success_url = "/"


class DetailTaskView(LoginRequiredMixin, DetailView):
    template_name = "pages/task.html"
    model = Task

    def get_object(self):
        bg.retrieve_results()
        return super().get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["compilers"] = [{"id": "python", "name": "Python 3.10"}]
        context["tasks"] = list(map(lambda t: {"task": t,
                                               "pts": accessor.get_points_for_task(self.request.user, t),
                                               "verdict": accessor.get_verdict_for_task(self.request.user, t)},
                                    accessor.get_ordered_tasks(self.object.contest)))
        context["tests"] = AutoTest.objects.filter(task=self.object, show=True)
        context["solutions"] = TaskSubmit.objects.filter(task=self.object, user=self.request.user)
        return context


class SubmitSolutionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            task = Task.objects.get(id=kwargs["pk"])
        except:
            return render(request, "base/error.html", context={""})
        solution = TaskSubmit(
            task=task,
            user=request.user,
            code=request.POST["code"],
            tests_total=0,
            tests_passed=0,
            tests_failed=0,
            points=0,
            verdict="queued",
            compiler=request.POST["compiler"]
        )
        solution.save()
        bg.enqueue_solutions()
        return redirect(f"/task/{kwargs['pk']}/")


class DetailSolutionView(LoginRequiredMixin, CanViewThisSolution, DetailView):
    template_name = "pages/solution.html"
    model = TaskSubmit

    def test_func(self):
        return self.get_object().user.id == self.request.user.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["protocol"] = AutoTestResult.objects.filter(submit=self.object)
        return context


class DetailStandingsView(LoginRequiredMixin, DetailView):
    template_name = "pages/standings.html"
    model = Contest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = accessor.get_ordered_tasks(self.object)
        context["task_count"] = len(context["tasks"])
        context["standings"] = filter(
            lambda x: x[1] != 0 if x is not None else None,
            sorted([[user.username] + accessor.get_stats_for_contest(self.object, user)
                    for user in User.objects.all()], key=lambda x: x[1] if x is not None else None, reverse=True)
        )
        return context


class ExportContextView(LoginRequiredMixin, UserIsAdmin, DetailView):
    


def ctx(page_name, **kwargs):
    return {
        "page_name": page_name,
        **kwargs
    }


@login_required
def admin_panel_view(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return error(request, [
            "Insufficient rights to view this page",
            "If you believe that this is a mistake, contact site administrator"
        ], "To homepage", "/")

    if "cmd" in request.GET:
        if request.GET["cmd"] == "create_user" and request.method == "POST":
            user = User.objects.create_user(
                username=request.POST["name"],
                password=request.POST["pass"]
            )
            try:
                user.save()
            except Exception as e:
                return error(request, ["Unexpected error", str(e)], "Back to panel", "/panel")
            return redirect("/panel")
        elif request.GET["cmd"] == "drop_user":
            if "user_id" not in request.GET:
                return error(request, ["Malformed command"], "Back", "/panel")
            try:
                user = get_object_or_404(User, id=int(request.GET["user_id"]))
            except Http404:
                return error(request, ["No such user"], "Back", "/panel")
            if request.user.id == user.id:
                return error(request, ["Cannot edit yourself"], "Back", "/panel")
            if "confirm" in request.GET:
                try:
                    user.delete()
                except Exception as e:
                    return error(request, ["Unexpected error", str(e)], "Back to panel", "/panel")
                return redirect("/panel")
            else:
                return confirmation(
                    request,
                    [f"Proceed deleting user {user.username}?"],
                    "Yes, delete", f"/panel?cmd=drop_user&user_id={user.id}&confirm",
                    "No, keep user", "/panel"
                )
        elif request.GET["cmd"] == "grant_admin":
            if "user_id" not in request.GET:
                return error(request, ["Malformed command"], "Back", "/panel")
            try:
                user = get_object_or_404(User, id=int(request.GET["user_id"]))
            except Http404:
                return error(request, ["No such user"], "Back", "/panel")
            if request.user.id == user.id:
                return error(request, ["Cannot edit yourself"], "Back", "/panel")
            if "confirm" in request.GET:
                user.is_staff = True
                try:
                    user.save()
                except Exception as e:
                    return error(request, ["Unexpected error", str(e)], "Back to panel", "/panel")
                return redirect("/panel")
            else:
                return confirmation(
                    request,
                    [f"Proceed making user {user.username} capable of admin rights?"
                     f"{user.username} will be able to access admin panel and edit prizes"],
                    "Yes, grant admin rights", f"/panel?cmd=grant_admin&user_id={user.id}&confirm",
                    "No, keep current rights", "/panel"
                )
        elif request.GET["cmd"] == "revoke_admin":
            if "user_id" not in request.GET:
                return error(request, ["Malformed command"], "Back", "/panel")
            try:
                user = get_object_or_404(User, id=int(request.GET["user_id"]))
            except Http404:
                return error(request, ["No such user"], "Back", "/panel")
            if request.user.id == user.id:
                return error(request, ["Cannot edit yourself"], "Back", "/panel")
            if "confirm" in request.GET:
                user.is_staff = False
                try:
                    user.save()
                except Exception as e:
                    return error(request, ["Unexpected error", str(e)], "Back to panel", "/panel")
                return redirect("/panel")
            else:
                return confirmation(
                    request,
                    [f"Proceed revoking admin rights from user {user.username}?",
                     f"{user.username} will no longer be able to access admin panel and edit prizes"],
                    "Yes, revoke admin rights", f"/panel?cmd=revoke_admin&user_id={user.id}&confirm",
                    "No, keep admin rights", "/panel"
                )
    context = ctx(
        "Admin panel",
        users=sorted(User.objects.all(), key=lambda x: x.is_staff, reverse=True)
    )
    return render(request, "pages/admin_panel.html", context)


@login_required
def profile_view(request):
    context = ctx(
        "Profile"
    )
    return render(request, "pages/profile.html", context)
