"""Wrapper script to execute the shell build pipeline."""
import logging
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

# Use the root logger for utility scripts
logger = logging.getLogger(__name__)


def run_build_script() -> NoReturn:
    """Execute the build.sh shell script and exit with its status code."""
    build_script_path = Path.cwd() / "build.sh"

    if not build_script_path.exists():
        logger.error("Error: build.sh not found at %s", build_script_path)
        sys.exit(1)

    if not build_script_path.stat().st_mode & 0o100:
        logger.error("Error: build.sh is not executable. Run: chmod +x build.sh")
        sys.exit(1)

    logger.info("--- Executing build.sh via Python wrapper ---")
    try:
        result = subprocess.run([build_script_path], check=True, stdout=sys.stdout)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        logger.exception("Build script failed with error code %s", e.returncode)
        sys.exit(e.returncode)
    except FileNotFoundError:
        logger.exception("Error: build.sh not found. Ensure it is in the project root.")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    run_build_script()
