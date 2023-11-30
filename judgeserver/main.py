import compilers
import mysql.connector
import json
import time
import shutil
import os


class JudgeServer:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db

    def connect(self):
        self.db = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name
        )

    def disconnect(self):
        self.db.close()
        self.db = None

    def unzip_tests(self, str_tests):
        tests = json.loads(str_tests)
        print("Tests unzipped, got", tests)
        return tests

    def place_solution(self, code, ext):
        with open(f"testenv/solution.{ext}", "w") as f:
            f.write(code)

    def purge_solutions(self):
        for root, dirs, files in os.walk("testenv"):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    def generate_verdict(self, protocol):
        for i, test in enumerate(protocol):
            if test["result"] != "OK":
                return test["result"], i
        return "OK", -1

    def grab_and_check_solutions(self):
        print("Checking solutions")
        self.connect()
        cur = self.db.cursor()
        cur.execute("SELECT * FROM queued_solutions;")
        for row in cur.fetchall():
            r_id, s_id, s_code, s_tests_zipped, s_compiler = row
            print(f"Testing solution {r_id}")
            s_tests = self.unzip_tests(s_tests_zipped)
            compiler = compilers.COMPILERS[s_compiler]()
            self.place_solution(s_code, compiler.file_ext)
            print("Solution prepared:")
            print("SID", s_id)
            print("CODE", s_code)
            print("COMPILER", s_compiler)
            print("Running tests")
            protocol = self.run_tests(s_tests, compiler)
            self.purge_solutions()
            protocol_s = json.dumps(protocol)
            verdict = self.generate_verdict(protocol)
            cur.execute("INSERT INTO checked_solutions (solution_id, code, protocol, verdict, fail_test) " +
                        "VALUES (%s, %s, %s, %s, %s);", (s_id, s_code, protocol_s, verdict[0], verdict[1]))
            cur.execute(f"DELETE FROM queued_solutions WHERE id = '{r_id}'")
            self.db.commit()
            print("Solution tested. Verdict:", verdict)
        cur.close()
        self.disconnect()

    def run_single_test(self, t_input, t_output, t_timeout, compiler):
        t_input = t_input.replace("\r", "")
        t_output = t_output.replace("\r", "")
        protocol = {}
        returncode, stdout, stderr, result = compiler.launch_and_get_output(
                f"testenv/solution.{compiler.file_ext}", t_input, t_timeout)
        passed = t_output.strip() == stdout.strip()
        if returncode != 0:
            protocol["result"] = "RE"
            protocol["return"] = returncode
            protocol["stderr"] = stderr
        elif passed:
            protocol["result"] = "OK"
            protocol["output"] = stdout
        else:
            protocol["result"] = "WA"
            protocol["output"] = stdout
            protocol["expected"] = t_output
        return protocol
    
    def run_tests(self, tests, compiler):
        protocol = []
        for i, test in enumerate(tests):
            protocol.append(self.run_single_test(test[0], test[1], test[2], compiler))
            print(f"Test {i} finished: {protocol[-1]}")
        return protocol

    def run(self):
        while True:
            self.grab_and_check_solutions()
            time.sleep(2)


def main():
    server = JudgeServer("localhost", "judgeserver", "judgeserver", "judgeserverdb")
    server.run()


if __name__ == "__main__":
    main()

