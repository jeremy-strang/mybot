import time
import os
import psutil
import subprocess
import sys

from utils.restart import process_exists, restart_game

MAX_RESTARTS = 5

def kill_mybot():
    os.system(f'taskkill /fi "USERNAME eq %USERNAME%" /fi "PID ne {os.getpid()}" /im python.exe /f')

def restart_mybot():
    time.sleep(2)
    # os.system("python src/main.py")
    # subprocess.run([sys.executable, 'src/main.py'])
    # subprocess.Popen(["python", "src/main.py"])
    os.startfile("bot.bat")

def main():
    checks = 0
    restarts = 0
    while 1:
        if not process_exists("D2R.exe"):
            restarts += 1
            if restarts > MAX_RESTARTS:
                return
            print("D2R.exe is not running, restarting MyBot and D2R...")
            kill_mybot()
            time.sleep(3)
            restart_game()
            time.sleep(20)
            restart_mybot()
        elif checks % 10 == 0:
            print(f"D2R.exe is running (checks: {checks}, restarts: {restarts})")
        checks += 1
        time.sleep(1)

if __name__ == "__main__":
    main()
