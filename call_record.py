import subprocess
import pandas as pd
import time
from pathlib import Path
import os

def find_call_record_dir():
    uid = os.getuid()
    gvfs = Path(
        f"/run/user/{uid}/gvfs"
    ) # User space virtual filesystem path

    if not gvfs.exists():
        return None

    for mount in gvfs.iterdir():

        if (
            mount.is_dir()
            and mount.name.startswith(
                "mtp:host=Xiaomi_Redmi_Note_13_5G"
            )
        ):

            target = (
                mount
                / "Internal shared storage"
                / "MIUI"
                / "sound_recorder"
                / "call_rec"
            )

            if target.exists():
                return target

    return None

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

print(f"Phone mounted path: {find_call_record_dir()}")

numbers = list(pd.read_excel("numbers.xlsx")["phone"])

for number in numbers:
    make_call(number)
    time.sleep(60) # Max 1 minute call
    end_call()
    time.sleep(5) # Wait for data to sync

