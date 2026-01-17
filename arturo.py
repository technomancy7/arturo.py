import os, subprocess, json, textwrap
from pathlib import Path

example = """
signal "test"
signal.key: "user" "chat"
print "hey there world"
setv "testkey" "completed the test"
"""

class Arturo:
    def __init__(self, executable = None):
        self.executable = executable

        if self.executable == None:
            self.find_executable()

        self.store = {}

        self.art_path = Path.home() / ".arturo"
        self.stores_path = Path.home() / ".arturo" / "stores"

        self.store_path = Path.home() / ".arturo" / "stores" / "rpc.json"
        self.code_path = Path.home() / ".arturo" / "_code.art"

        if not self.art_path.exists():
            self.art_path.mkdir(parents=True, exist_ok=True)

        if not self.stores_path.exists():
            self.stores_path.mkdir(parents=True, exist_ok=True)

        if self.store_path.exists():
            self.pull_store()

    def template(self):
        return textwrap.dedent("""
        ; Template

        ; Create persistent storage so we can send signals between script and host
        rpc: store.global.json.deferred "rpc"

        ; If the default important keys are not found in the store, generate them
        unless key? to :dictionary rpc 'signals [
            rpc\\signals: []
        ]

        unless key? to :dictionary rpc 'vars [
            rpc\\vars: #[]
        ]


        ; Utility functions

        signal: function [body][
            ; Send a signal to the RPC

            key: attr 'key
            if key = null [
                key: "message"
            ]
            rpc\\signals: rpc\\signals ++ ~"|key|->|body|"
        ]

        setv: function [key v][
            rpc\\vars\\[key]: v
        ]

        getv: function [key][
            return rpc\\vars\\[key]
        ]

        ; Code
        """)

    def get_store(self):
        with open(self.store_path) as f:
            return json.load(f)

    def pull_store(self):
        self.store = self.get_store()
        return self.store

    def put_store(self, overwrite = None):
        if overwrite != None and type(overwrite) == dict:
            self.store = overwrite

        with open(self.store_path, "w") as f:
            json.dump(self.store, f, indent = 4)

    def version(self):
        return self.run(["--version"])['output']

    def code(self, s):
        with open(self.code_path, "w") as f:
            f.write(self.template()+s)

        return self.run([str(self.code_path)])

    def run(self, args=None):
        """
        Runs the binary file and returns the standard output as a string.

        Args:
            args (list): A list of arguments to pass to the binary (optional).

        Returns:
            str: The standard output of the binary.
        """
        if args is None:
            args = []

        # Construct the command list (binary path + arguments)
        command = [self.executable] + args
        try:
            result = subprocess.run(
                command,
                capture_output=True, # Captures both stdout and stderr
                text=True,           # Decodes bytes to string (UTF-8 by default)
                check=True           # Raises exception if binary fails
            )

            self.pull_store()
            self.store["output"] = result.stdout.strip()
            return self.store

        except FileNotFoundError:
            return {"error": f"The binary '{self.executable}' was not found."}

        except subprocess.CalledProcessError as e:
            print(e.stderr)
            self.pull_store()
            self.store["error_code"] = e.returncode
            self.store["error"] = e.stderr
            return self.store

    def find_executable(self):
        """finds the arturo binary in your PATH"""
        for directory in os.getenv("PATH", "").split(os.pathsep):
            if not directory:
                continue
            path = os.path.join(directory, "arturo")
            if os.path.isfile(path) and os.access(path, os.X_OK):
                self.executable = path
                return path

        return None

if __name__ == "__main__":
    try:
        a = Arturo()
        output = a.version()
        print("Output received:\n", output)
        output = a.code(example)
        print("Example test received:\n", output)
        #a.put_store({})
    except Exception as e:
        print(e.stderr)
