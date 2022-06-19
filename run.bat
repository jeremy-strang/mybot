@ECHO OFF
CLS
:MENU
ECHO.
ECHO ...............................................
ECHO PRESS 1, 2, 3, 4, 5 or 6 to select your task
ECHO ...............................................
ECHO.
ECHO 1 - Install Env
ECHO 2 - Update Env
ECHO 3 - Compile
ECHO 4 - Run MyBot
ECHO 5 - Run Crash Recovery
ECHO 6 - Exit
ECHO.
SET /P M=Type 1, 2, 3, 4, 5 or 6 then press ENTER:
IF %M%==1 GOTO INSTALL
IF %M%==2 GOTO UPDATE
IF %M%==3 GOTO COMPILE
IF %M%==4 GOTO RUN
IF %M%==5 GOTO CRASHRECOVERY
IF %M%==6 GOTO EXIT
:INSTALL
start cmd /c conda env create environment.yml
GOTO MENU
:UPDATE
start cmd /c conda env update environment.yml
GOTO MENU
:COMPILE
python ./build.py
GOTO MENU
:RUN
conda activate mybot && python src/main.py
GOTO MENU
:CRASHRECOVERY
conda activate mybot && python src/crash_recovery.py
GOTO MENU
:EXIT
EXIT
