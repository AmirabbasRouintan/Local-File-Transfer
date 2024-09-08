import os
import subprocess

def create_shell_script(send_py_path):
    shell_script_content = f"#!/bin/bash\npython3 {send_py_path}"
    with open("send.sh", "w") as file:
        file.write(shell_script_content)
        
def make_script_executable():
    subprocess.run(["chmod", "+x", "send.sh"])

def move_script_to_usr_bin():
    subprocess.run(["sudo", "mv", "send.sh", "/usr/bin/send"])

def main():
    send_py_path = os.path.abspath("main.py")

    create_shell_script(send_py_path)

    make_script_executable()

    move_script_to_usr_bin()

    print("The 'send' command has been set up successfully.")

if __name__ == "__main__":
    main()
