import subprocess
import pandas as pd
import time

def make_call(phone):
    subprocess.run([
        "adb",
        "shell",
        "am",
        "start",
        "-a",
        "android.intent.action.CALL",
        "-d",
        f"tel:{phone}"
    ])

def end_call():
    subprocess.run([
        "adb",
        "shell",
        "input",
        "keyevent",
        "6"
    ]) # If the call has already ended, this does nothing

numbers = list(pd.read_excel("numbers.xlsx")["phone"])

for number in numbers:
    make_call(number)
    time.sleep(60)
    end_call()
    time.sleep(10)
    