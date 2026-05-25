import subprocess
from pathlib import Path
import shutil
import os

class RecordingNotFound(Exception): # To catch calls that were not picked up
    pass

def copy_recording(phone):
    uid = os.getuid()
    gvfs = Path(f"/run/user/{uid}/gvfs")
    mount = None
    for item in gvfs.iterdir():
        if item.name.startswith("mtp:host=Xiaomi_Redmi_Note_13_5G"):
            mount = item
            break

    if mount is None:
        raise Exception("Phone not connected")

    call_dir = (
        mount
        / "Internal shared storage"
        / "MIUI"
        / "sound_recorder"
        / "call_rec"
    )

    recordings = Path("./recordings")

    recordings.mkdir(
        exist_ok=True
    )

    pattern = f"{phone}"
    matches = [f for f in call_dir.glob("*.mp3") if pattern in f.name]

    if not matches:
        raise RecordingNotFound(f"No recording for {phone}")

    latest = max(matches,key=lambda x: x.stat().st_mtime)
    dest = recordings / latest.name
    shutil.copy2(latest, dest)

    return str(dest)

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

def call_status():
    cmd = (
        "adb shell dumpsys telecom | "
        "grep -iE 'SET_DIALING|SET_ACTIVE|SET_CONNECTING|SET_DISCONNECTED' | "
        "tail -1"
    )

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )

    line = result.stdout.strip()

    if "SET_ACTIVE" in line:
        return 2
    elif "SET_DIALING" in line:
        return 1
    else:
        return 0


def end_call():
    subprocess.run([
        "adb",
        "shell",
        "input",
        "keyevent",
        "6"
    ]) # If the call has already ended, this does nothing

def play_audio(audio_path):
    subprocess.run(
        [
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel", "quiet",
            audio_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )