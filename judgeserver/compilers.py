import subprocess


class Compiler:
    file_ext: str = ""

    def __init__(self):
        pass

    def launch_and_get_output(self, file_path, proc_input, timeout):
        pass


class PythonInterpreter(Compiler):
    file_ext = "py"

    def launch_and_get_output(self, path, inp, to):
        protocol = []
        try:
            process = subprocess.run(["python3", path], input=inp.encode("utf-8"),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=to)
            return process.returncode, process.stdout.decode("utf-8"), process.stderr.decode("utf-8"), "OK"
        except subprocess.TimeoutExpired:
            return -1, "", "", "TL"


COMPILERS = {
    "python": PythonInterpreter
}
