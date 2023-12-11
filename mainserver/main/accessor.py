from main.models import *


def get_last_solution_for_task(user, task):
    submits = TaskSubmit.objects.filter(user=user, task=task)
    if len(submits) == 0:
        return None
    else:
        return submits.latest("created_on")

def get_points_for_task(user, task):
    best = get_last_solution_for_task(user, task)
    if best is None:
        return 0
    else:
        return best.points


def get_verdict_for_task(user, task):
    best = get_last_solution_for_task(user, task)
    if best is None:
        return "no"
    else:
        return best.verdict


def get_ordered_tasks(contest):
    tasks = Task.objects.filter(contest=contest)
    if contest.task_ordering is None:
        return tasks
    else:
        try:
            return [tasks.get(id=int(i)) for i in contest.task_ordering.split(";")]
        except:
            return tasks


def get_stats_for_contest(contest, user):
    s = [(lambda x: x.points if x is not None else None)(get_last_solution_for_task(user, task))
         for task in get_ordered_tasks(contest)]
    s.insert(0, sum([i for i in s if i is not None]))
    return s

