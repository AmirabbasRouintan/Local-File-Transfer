import os
import subprocess

def create_shell_script(send_py_path):
    # Create the shell script content
    shell_script_content = f"#!/bin/bash\npython3 {send_py_path}"

    # Write the shell script to a file
    with open("send.sh", "w") as file:
        file.write(shell_script_content)

def make_script_executable():
    # Make the script executable
    subprocess.run(["chmod", "+x", "send.sh"])

def move_script_to_usr_bin():
    # Move the script to /usr/bin
    subprocess.run(["sudo", "mv", "send.sh", "/usr/bin/send"])

def main():
    # Get the current path of the send.py script
    send_py_path = os.path.abspath("send.py")

    # Create the shell script
    create_shell_script(send_py_path)

    # Make the script executable
    make_script_executable()

    # Move the script to /usr/bin
    move_script_to_usr_bin()

    print("The 'send' command has been set up successfully.")

if __name__ == "__main__":
    main()
