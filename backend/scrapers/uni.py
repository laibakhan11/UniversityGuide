import os
import subprocess
import sys

folder = os.path.dirname(os.path.abspath(__file__))

env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

print("Starting all scrapers (UTF-8 safe)...\n")

for file in sorted(os.listdir(folder)):
    if file.endswith(".py") and file not in {"uni.py", "__init__.py"}:
        path = os.path.join(folder, file)
        print(f"Running {file} ...")
        try:
            result = subprocess.run(
                [sys.executable, path],
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout.strip():
                print(result.stdout)
            print(f"✓ {file} done\n")
        except subprocess.CalledProcessError as e:
            print(f"✗ {file} failed!\n{e.stderr}\n")

print("All scrapers finished!")