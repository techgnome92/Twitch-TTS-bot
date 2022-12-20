import os, sys, socket, uuid, time, re, traceback, threading, keyboard
from pydub import AudioSegment
import simpleaudio as sa
import config

# Getting variables from config.py
server = config.settings['server']
port = config.settings['port']
nickname = config.settings['nickname']
token = config.settings['token']
channel = config.settings['channel']
MODE = config.settings['MODE']
TMP_DIR = config.settings['TMP_DIR']
USER_IGNORE_PATH = config.settings['USER_IGNORE_PATH']
USER_ALLOW_PATH = config.settings['USER_ALLOW_PATH']
WORD_IGNORE_PATH = config.settings['WORD_IGNORE_PATH']
SILENCE_HOTKEY = config.settings['SILENCE_HOTKEY']
SAY_USERNAME = config.settings['SAY_USERNAME']

SUBSCRIBERS_ALLOWED = config.settings['SUBSCRIBERS_ALLOWED']
VIP_ALLOWED = config.settings['VIP_ALLOWED']
TURBO_ALLOWED = config.settings['TURBO_ALLOWED']
MODERATOR_ALLOWED = config.settings['MODERATOR_ALLOWED']
BIT_DONATION_ALLOWED = config.settings['BIT_DONATION_ALLOWED']
CHANNEL_POINT_REDEMPTION_ALLOWED = config.settings['CHANNEL_POINT_REDEMPTION_ALLOWED']
EVERYONE_ALLOWED = config.settings['EVERYONE_ALLOWED']

# Variables
USER_IGNORE_LIST = []
USER_ALLOW_LIST = []
WORD_IGNORE_LIST = []

user_ignore_file_updated = 0
user_allow_file_updated = 0
word_ignore_file_updated = 0

exit_event = threading.Event()

USERNAME_CHANNEL_MESSAGE_REGEX = ':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(\w+) :(.*)'

# Makes temporary dirs if they dont exist
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))
sock.send(f"CAP REQ :twitch.tv/tags\n".encode('utf-8'))
resp = sock.recv(2048).decode('utf-8')
resp = sock.recv(2048).decode('utf-8')

def say_single_message(message):
    try:
        session = str(uuid.uuid1())
        temp_wav = os.path.join(TMP_DIR, session+'.wav')
        message = message.replace('"', '').replace('&', '').replace('|', '').replace(';', '')
        if os.name == 'nt':
            #print("say.exe -d dtalk_us.dic -w "+temp_wav+" \"[:phoneme on]"+message+"\"")
            os.system("say.exe -d dtalk_us.dic -w "+temp_wav+" \"[:phoneme on]"+message+"\"")
        else:
            #print("wine say.exe -d dtalk_us.dic -w "+temp_wav+" \"[:phoneme on]"+message+"\"")
            os.system("wine say.exe -d dtalk_us.dic -w "+temp_wav+" \"[:phoneme on]"+message+"\"")
        wave_obj = sa.WaveObject.from_wave_file(temp_wav)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        os.remove(temp_wav)
    except Exception:
        traceback.print_exc()

def is_valid_line(line):
    if len(line) and not line.startswith("PING") and not line.startswith(":tmi.twitch.tv"):

        lineSplit = line.split(" ", 1)
        lineTags = lineSplit[0].split(";")
        lineMessage = lineSplit[1]
        username, channel, message = re.search(USERNAME_CHANNEL_MESSAGE_REGEX, lineMessage).groups()

        if not message:
            return False

        if username in USER_IGNORE_LIST:
            return False
        elif EVERYONE_ALLOWED:
            return True
        elif "badges=broadcaster/1" in lineTags:
            return True
        elif SUBSCRIBERS_ALLOWED and "subscriber=1" in lineTags:
            return True
        elif VIP_ALLOWED and "vip=1" in lineTags:
            return True
        elif TURBO_ALLOWED and "turbo=1" in lineTags:
            return True
        elif MODERATOR_ALLOWED and "mod=1" in lineTags:
            return True
        elif BIT_DONATION_ALLOWED and "bits=" in lineSplit[0]:
            if isinstance(BIT_DONATION_ALLOWED, int):
                bitAmount = lineSplit[0].split("bits=", 1)[1].split(";", 1)[0]
                return BIT_DONATION_ALLOWED <= int(bitAmount)
            else:
                return True
        elif CHANNEL_POINT_REDEMPTION_ALLOWED and "custom-reward-id=" in lineSplit[0]:
            return True
        elif username in USER_ALLOW_LIST:
            return True
        else:
            return False
    elif line.startswith("PING"):
        sock.send("PONG :tmi.twitch.tv\r\n".encode())
        return False

def refresh_lists():
    global user_ignore_file_updated, user_allow_file_updated, word_ignore_file_updated

    if user_ignore_file_updated < os.stat(USER_IGNORE_PATH).st_mtime:
        user_ignore_file_updated = os.stat(USER_IGNORE_PATH).st_mtime
        load_user_ignore_list()

    if user_allow_file_updated < os.stat(USER_ALLOW_PATH).st_mtime:
        user_allow_file_updated = os.stat(USER_ALLOW_PATH).st_mtime
        load_user_allow_list()

    if word_ignore_file_updated < os.stat(WORD_IGNORE_PATH).st_mtime:
        word_ignore_file_updated = os.stat(WORD_IGNORE_PATH).st_mtime
        load_word_ignore_list()

def filter_words(message):
    local_message = message

    for word in WORD_IGNORE_LIST:
        ignore = ""
        replace = ""

        if ":" in word:
            splitted = word.split(":", 1)
            ignore = splitted[0].lower()
            replace = splitted[1]
        else:
            ignore = word.lower()

        pattern = re.compile(re.escape(ignore), re.IGNORECASE)
        local_message = pattern.sub(replace, local_message)

    return local_message

def add_username_says(message, username):
    if SAY_USERNAME:
        return username + " says " + message
    else:
        return message


def ping_sender():
    while True:
        sock.send("PING :tmi.twitch.tv\r\n".encode())
        exit_event.wait(300)

        if exit_event.is_set():
            break

def load_user_ignore_list():
    global USER_IGNORE_LIST

    file = open(USER_IGNORE_PATH, "r")
    file_content = file.read()
    USER_IGNORE_LIST = []

    for line in file_content.split("\n"):
        USER_IGNORE_LIST.append(line.lower())

    while "" in USER_IGNORE_LIST:
        USER_IGNORE_LIST.remove("")

def load_user_allow_list():
    global USER_ALLOW_LIST

    file = open(USER_ALLOW_PATH, "r")
    file_content = file.read()
    USER_ALLOW_LIST = []

    for line in file_content.split("\n"):
        USER_ALLOW_LIST.append(line.lower())

    while "" in USER_ALLOW_LIST:
        USER_ALLOW_LIST.remove("")

def load_word_ignore_list():
    global WORD_IGNORE_LIST

    file = open(WORD_IGNORE_PATH, "r")
    file_content = file.read()
    WORD_IGNORE_LIST = file_content.split("\n")
    while "" in WORD_IGNORE_LIST:
        WORD_IGNORE_LIST.remove("")

def run_singlethread():
    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')
            refresh_lists()
            line = resp.split('\r\n')[0]
            if is_valid_line(line):
                lineSplit = line.split(" ", 1)
                lineMessage = lineSplit[1]
                username, channel, message = re.search(USERNAME_CHANNEL_MESSAGE_REGEX, lineMessage).groups()
                message = filter_words(message)
                message = add_username_says(message, username)

                say_single_message(message)
            
        except Exception:
            traceback.print_exc()

        if exit_event.is_set():
            break

def run_queue_single():
    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')
            refresh_lists()
            for line in resp.split('\r\n'):
                if is_valid_line(line):
                    lineSplit = line.split(" ", 1)
                    lineMessage = lineSplit[1]
                    username, channel, message = re.search(USERNAME_CHANNEL_MESSAGE_REGEX, lineMessage).groups()
                    message = filter_words(message)
                    message = add_username_says(message, username)

                    say_single_message(message)
            
        except Exception:
            traceback.print_exc()

        if exit_event.is_set():
            break

def run_multithread():
    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')
            refresh_lists()
            for line in resp.split('\r\n'):
                if is_valid_line(line):
                    lineSplit = line.split(" ", 1)
                    lineMessage = lineSplit[1]
                    username, channel, message = re.search(USERNAME_CHANNEL_MESSAGE_REGEX, lineMessage).groups()
                    message = filter_words(message)
                    message = add_username_says(message, username)

                    threading.Thread(target=say_single_message, args=(message,)).start()

        except Exception:
            traceback.print_exc()
            time.sleep(1)

        if exit_event.is_set():
            break

def silence_please():
    sa.stop_all()

def await_command():
    while True:
        try:
            global SUBSCRIBERS_ALLOWED, VIP_ALLOWED, TURBO_ALLOWED, MODERATOR_ALLOWED, BIT_DONATION_ALLOWED, CHANNEL_POINT_REDEMPTION_ALLOWED, EVERYONE_ALLOWED
            print("The bot should be running now.")
            print("")
            print("\tstop [s] \t\tStop all currently running audios.")
            print("\tquit [q] \t\tTurn off the bot.")
            print("")
            print("\ttoggle subscribers [ts] \t\tSubscribed users allowed: \t" + str(SUBSCRIBERS_ALLOWED))
            print("\ttoggle vip [tv] \t\t\tVIP users allowed: \t\t" + str(VIP_ALLOWED))
            print("\ttoggle turbo [tt] \t\t\tTurbo users allowed: \t\t" + str(TURBO_ALLOWED))
            print("\ttoggle mods [tm] \t\t\tModerator users allowed: \t" + str(MODERATOR_ALLOWED))
            print("\ttoggle bits (amount) [tb(amount)] \tBit donations allowed: \t\t" + str(BIT_DONATION_ALLOWED))
            print("\ttoggle points [tp] \t\t\tChannel point reward allowed: \t" + str(CHANNEL_POINT_REDEMPTION_ALLOWED))
            print("\ttoggle everyone [te] \t\t\tEveryone allowed: \t\t" + str(EVERYONE_ALLOWED))
            print("")
            value = input("Input: ")
            if value == "s" or value == "stop":
                sa.stop_all()
            elif value == "q" or value == "quit":
                exit_application()
            elif value == "ts" or value == "toggle subscribers":
                SUBSCRIBERS_ALLOWED = not SUBSCRIBERS_ALLOWED
            elif value == "tv" or value == "toggle vip":
                VIP_ALLOWED = not VIP_ALLOWED
            elif value == "tt" or value == "toggle turbo":
                TURBO_ALLOWED = not TURBO_ALLOWED
            elif value == "tm" or value == "toggle mods":
                MODERATOR_ALLOWED = not MODERATOR_ALLOWED
            elif value == "tp" or value == "toggle points":
                CHANNEL_POINT_REDEMPTION_ALLOWED = not CHANNEL_POINT_REDEMPTION_ALLOWED
            elif value == "te" or value == "toggle everyone":
                EVERYONE_ALLOWED = not EVERYONE_ALLOWED
            elif value == "tb" or value == "toggle bits":
                BIT_DONATION_ALLOWED = not BIT_DONATION_ALLOWED
            elif "tb" in value:
                amount, = re.search('tb(.*)', value).groups()
                BIT_DONATION_ALLOWED = int(amount)
            elif "toggle bits " in value:
                amount, = re.search('toggle bits (.*)', value).groups()
                BIT_DONATION_ALLOWED = int(amount)

        except KeyboardInterrupt:
            exit_application()
        except Exception as e:
            traceback.print_exc()

def exit_application():
    global thread_ping, thread_listen
    sock.close()
    silence_please()
    exit_event.set()
    thread_ping.join()
    thread_listen.join()
    sys.exit()

def start_listen():
    if MODE == 'keepup':
        run_singlethread()
    elif MODE == 'queue':
        run_queue_single()
    elif MODE == 'multi':
        run_multithread()
    else:
        print('Please select a mode by editing the MODE variable ')

# Processes
thread_ping = threading.Thread(target=ping_sender, args=())
thread_listen = threading.Thread(target=start_listen, args=())

# Hotkeys
if SILENCE_HOTKEY:
    keyboard.add_hotkey(SILENCE_HOTKEY, silence_please)

if __name__ ==  '__main__':
    thread_ping.start()
    thread_listen.start()
    await_command()
