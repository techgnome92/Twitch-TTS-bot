import os

voices = {
    "ms_sam": "MSSam",
    "ms_mike": "MSMike",
    "ms_mary": "MSMary",
    "ms_david": "TTS_MS_EN-US_DAVID_11.0",
    "ms_zira": "TTS_MS_EN-US_ZIRA_11.0",
    "dektalk": "dektalk"
}


def create_wave(tmp_dir: str, message: str, tts: str = "ms_sam"):

    if tts == "dektalk":
        cmd_line = f"say.exe -d dtalk_us.dic -w {tmp_dir} [:phoneme on] '{message}'"
        if os.name != "nt":
            cmd_line = f"wine {cmd_line}"

    else:
        # if tts is not valid voice is empty
        voice = ""
        if tts in voices.keys():
            voice = f"--voice {voices[tts]}"

        cmd_line = f'python ms_sam/ms_sam.py {voice} {tmp_dir} "{message}"'

    os.system(cmd_line)


if __name__ == "__main__":
    for voice in voices:
        create_wave(f"{voice}.wav", "This is a test", voice)
