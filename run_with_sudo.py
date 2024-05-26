import os
import sys

if __name__ == "__main__":
    script = sys.argv[1]
    args = sys.argv[2:]
    os.execvp("sudo", ["sudo", "python3", script] + args)
