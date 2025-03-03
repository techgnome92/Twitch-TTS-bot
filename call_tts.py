import os

voices = {
    "ms_sam": "MSSam",
    "ms_mike": "MSMike",
    "ms_mary": "MSMary",
    "ms_david": "TTS_MS_EN-US_DAVID_11.0",
    "ms_zira": "TTS_MS_EN-US_ZIRA_11.0",
}


def create_wave(tmp_dir: str, message: str, tts: str = "ms_sam"):

    if tts == "dektalk":
        os.system(f"say.exe -d dtalk_us.dic -w {tmp_dir} [:phoneme on] '{message}'")
        return

    # if tts is not valid voice is empty
    voice = ""
    if tts in voices.keys():
        voice = f"--voice {voices[tts]}"

    cmd_line = f'python ms_sam/ms_sam.py {voice} {tmp_dir} "{message}"'

    if os.name != "nt":
        cmd_line = f"wine {cmd_line}"

    os.system(cmd_line)

create_wave("tmp.wav", "THIS IS A TEST", "dektalk")
