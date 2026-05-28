import os
import sys


# Compatibility entrypoint for older launch commands.
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(current_dir)
sys.path.append(repo_root)

from teleop.xr_control_rpo import main


if __name__ == "__main__":
    raise SystemExit(main())
