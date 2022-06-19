import subprocess
import os, sys
import keyboard
from template_finder import TemplateFinder
from utils.misc import wait, set_d2r_always_on_top
from utils.custom_mouse import mouse
from screen import Screen
from config import Config

MAIN_MENU_MARKERS = ["MAIN_MENU_TOP_LEFT", "MAIN_MENU_TOP_LEFT_DARK", "LOBBY_MENU_TOP_LEFT"]

def process_exists(process_name):
    call = f'tasklist /fi "IMAGENAME eq {process_name}" /fi "USERNAME eq {os.getlogin()}"'
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def kill_game():
    while process_exists("D2R.exe"):
            os.system(f'taskkill /fi "USERNAME eq %USERNAME%" /im D2R.exe /f')
            wait(1.0, 1.5)
    while process_exists("BlizzardError.exe"):
            os.system(f'taskkill /fi "USERNAME eq %USERNAME%" /im BlizzardError.exe /f')
            wait(1.0, 1.5)

def restart_game(d2_path = None):
    if not d2_path:
        path = "C:\Program Files (x86)\Diablo II Resurrected\D2R.exe"
    else:
        path = d2_path
    kill_game()
    wait(1.0, 1.5)

    # This method should function similar to opening the exe via double-click
    # os.startfile(path)
    os.startfile("d2r.bat")
    wait(4.4, 5.5)

    success = False
    attempts = 0
    set_d2r_always_on_top()
    
    while not success:
        screen = Screen()
        success = screen.found_offsets    
        wait(0.5, 1.0)
        screen.activate_d2r_window()

    click_pos_abs = screen.convert_abs_to_monitor((-300, -150))
    for _ in range(10):
        mouse.move(*click_pos_abs, delay_factor=[0.1, 0.2])
        mouse.click(button="left")
        wait(1.0, 1.5)

    template_finder = TemplateFinder(screen)
    
    while not template_finder.search(MAIN_MENU_MARKERS, screen.grab(), best_match=True).valid:
        # keyboard.send("space")
        mouse.move(*click_pos_abs, delay_factor=[0.1, 0.2])
        mouse.click(button="left")
        wait(2.0, 4.0)
        attempts += 1
        if attempts >= 10:
            print(f"Attempt #{attempts}")
            return False
    print("Successfully restarted D2R")
    return True

# For testing 
if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = restart_game(sys.argv[1])
        print(result)
    else:
        result = restart_game()
        print(result)
