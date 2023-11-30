from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Contest(models.Model):
    title = models.CharField(max_length=255)
    task_ordering = models.TextField(null=True, default=None)

    def __str__(self):
        return f"#{self.id} {self.title}"


class Task(models.Model):
    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    max_points = models.IntegerField()
    test_ordering = models.TextField()

    def __str__(self):
        return f"{str(self.contest)}: #{self.id} {self.title}"



class AutoTest(models.Model):
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE)
    input = models.TextField(default="", null=True)
    output = models.TextField()
    time_limit = models.IntegerField()
    show = models.BooleanField()


class TaskSubmit(models.Model):
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    code = models.TextField()
    points = models.IntegerField()
    tests_total = models.IntegerField()
    tests_passed = models.IntegerField()
    tests_failed = models.IntegerField()
    verdict = models.CharField(max_length=255)
    compiler = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)


class AutoTestResult(models.Model):
    submit = models.ForeignKey(to=TaskSubmit, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    test = models.ForeignKey(to=AutoTest, on_delete=models.CASCADE)
    present_output = models.TextField()
    is_passed = models.BooleanField()
    error = models.TextField(null=True, default=None)
