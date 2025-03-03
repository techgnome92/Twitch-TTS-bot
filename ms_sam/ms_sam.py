import typer
import pyttsx3


voice_prefix = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens"


def main(wave: str, message: str, rate: float = 137.89, voice: str = "MSSam"):
    engine = pyttsx3.init()

    engine.setProperty('voice', f"{voice_prefix}\\{voice}")
    engine.setProperty("rate", rate)

    engine.save_to_file(message, wave)

    engine.runAndWait()


if __name__ == "__main__":
    typer.run(main)
