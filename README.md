# Twitch-TTS-bot
Twitch text-to-speech bot is a bot that reads out chat messages using Microsoft Voices. Includes voices are MS Sam, MS Mike, MS Mary, MS David, MS Zira 

## Using the twitch bot
1. Install the requirements with `python -m pip install -r requirements.txt`
2. Install ms_sam/WinXP_TTS_Voices_v1.3.exe
3. Copy config.py.example to config.py in the same path
   1. Valid entries for TTS_VOICE are [ms_sam, ms_mike, ms_mary, ms_david, ms_zira]
4. Change the nickname, token and channel variables in config.py
5. Run the bot with `python main.py`
