import subprocess
import sys
import os


def run_build_script():
    """Wrapper function to execute the build.sh shell script."""

    # Ensure build.sh exists and is executable
    build_script_path = os.path.join(os.getcwd(), "build.sh")
    if not os.path.exists(build_script_path):
        print(f"Error: build.sh not found at {build_script_path}", file=sys.stderr)
        sys.exit(1)

    if not os.access(build_script_path, os.X_OK):
        print(
            "Error: build.sh is not executable. Run: chmod +x build.sh",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        # Execute the shell script using subprocess.run
        # shell=True is needed to run a shell command directly
        result = subprocess.run(
            ["./build.sh"], check=True, stdout=sys.stdout, stderr=sys.stderr
        )
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Build script failed with error code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(
            "Error: build.sh not found. Ensure it is in the project root.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    run_build_script()
