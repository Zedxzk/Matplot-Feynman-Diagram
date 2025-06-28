import os
import subprocess
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(base_dir, "feynplot_GUI")

os.chdir(target_dir)
subprocess.run([sys.executable, "-m", "feynplot_gui"])

