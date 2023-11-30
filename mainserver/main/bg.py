import os
from threading import Thread
import mysql.connector
import json
import time

from django.apps import AppConfig


def build_test_list(tests):
    t = []
    for test in tests:
        t.append([test.input, test.output, test.time_limit])
    return t


def connect_db():
    db = mysql.connector.connect(
        host="localhost",
        user="judgeserver",
        password="judgeserver",
        database="judgeserverdb",
    )
    return db


def get_task_tests(task):
    from main.models import TaskSubmit, AutoTest, AutoTestResult
    tests = AutoTest.objects.filter(task=task)
    return list(map(lambda x: tests.get(id=int(x)), task.test_ordering.split(";")))


def enqueue_solutions():
    from main.models import TaskSubmit, AutoTest, AutoTestResult
    db = connect_db()
    cur = db.cursor()
    for submit in TaskSubmit.objects.filter(verdict="queued"):
        tests = get_task_tests(submit.task)
        r = cur.execute("INSERT INTO queued_solutions (solution_id, code, tests, compiler) VALUES (%s, %s, %s, %s);",
                    (submit.id, submit.code, json.dumps(build_test_list(tests)), submit.compiler))
        submit.verdict = "checking"
        submit.save()
    db.commit()
    cur.close()
    db.close()


def retrieve_results():
    from main.models import TaskSubmit, AutoTest, AutoTestResult
    db = connect_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM checked_solutions;")
    for row in cur.fetchall():
        r_id, solution_id, code, protocol, verdict, fail_test = row
        protocol = json.loads(protocol)
        try:
            solution = TaskSubmit.objects.get(id=solution_id)
        except:
            continue
        tests = get_task_tests(solution.task)
        tests_passed = 0
        for test, result in zip(tests, protocol):
            if result["result"] == "OK":
                tests_passed += 1
                test_result = AutoTestResult(
                    submit=solution,
                    user=solution.user,
                    test=test,
                    present_output=result["output"],
                    is_passed=True,
                    error="OK"
                )
            elif result["result"] == "WA":
                test_result = AutoTestResult(
                    submit=solution,
                    user=solution.user,
                    test=test,
                    present_output=result["output"],
                    is_passed=False,
                    error="WA"
                )
            elif result["result"] == "RE":
                test_result = AutoTestResult(
                    submit=solution,
                    user=solution.user,
                    test=test,
                    present_output="Return code: " + str(result["return"]) + "\n" + result["stderr"],
                    is_passed=False,
                    error=result["stderr"]
                )
            else:
                test_result = AutoTestResult(
                    submit=solution,
                    user=solution.user,
                    test=test,
                    present_output=result["result"],
                    is_passed=False,
                    error=result["result"]
                )
            test_result.save()
        solution.points = solution.task.max_points / len(tests) * tests_passed
        solution.tests_total = len(tests)
        solution.tests_passed = tests_passed
        solution.tests_failed = len(tests) - tests_passed
        solution.verdict = verdict
        solution.save()
        cur.execute(f"DELETE FROM checked_solutions WHERE id = '{r_id}';")
    db.commit()
    cur.close()
    db.close()


def communicate_with_judge_server():
    while True:
        enqueue_solutions()
        retrieve_results()
        time.sleep(2)


def start_bg_judge_server_communication():
    th = Thread(target=communicate_with_judge_server)
    th.daemon = True
    th.run()
    print("Communication started")

