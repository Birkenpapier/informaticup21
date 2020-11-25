import subprocess

def start_game_client(n):
    for i in range(n):
        subprocess.run("win.exe")