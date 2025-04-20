import subprocess
import tempfile
from typing import Tuple

def run_flake8_on_code(code: str) -> str:
    """Run flake8 on the snippet, return stdout/stderr."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tf:
        tf.write(code)
        tf.flush()
        proc = subprocess.run(
            ["flake8", tf.name],
            capture_output=True,
            text=True
        )
    report = proc.stdout + proc.stderr
    return report or "No linting issues found."

def apply_black(code: str) -> str:
    """Auto‑format with black."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as tf:
        tf.write(code)
        tf.flush()
        subprocess.run(["black", tf.name, "--quiet"])
        tf.seek(0)
        return tf.read()
