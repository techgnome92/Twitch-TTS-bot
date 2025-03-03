import os


def create_wave(tmp_dir: str, message: str, tts: str = "ms_sam",):
    if tts == "ms_sam":
        cmd_line = f'python ms_sam/ms_sam.py {tmp_dir} "{message}"'

    if os.name != "nt":
        cmd_line = f"wine {cmd_line}"

    os.system(cmd_line)
