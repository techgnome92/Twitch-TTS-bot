import os, socket, uuid, time, re, traceback, threading
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
WORD_IGNORE_PATH = config.settings['WORD_IGNORE_PATH']

# Variables
USER_IGNORE_LIST = []
WORD_IGNORE_LIST = []

user_ignore_file_updated = 0
word_ignore_file_updated = 0

# Makes temporary dirs if they dont exist
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))
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
    global user_ignore_file_updated, word_ignore_file_updated

    if len(line) and not line.startswith("PING") and not line.startswith(":tmi.twitch.tv"):
        username = line.split(':',1)[1].split('!', 1)[0]
        if user_ignore_file_updated < os.stat(USER_IGNORE_PATH).st_mtime:
            user_ignore_file_updated = os.stat(USER_IGNORE_PATH).st_mtime
            load_user_ignore_list()

        if word_ignore_file_updated < os.stat(WORD_IGNORE_PATH).st_mtime:
            word_ignore_file_updated = os.stat(WORD_IGNORE_PATH).st_mtime
            load_word_ignore_list()

        if username not in USER_IGNORE_LIST:
            return True
        else:
            return False
    elif line.startswith("PING"):
        sock.send("PONG :tmi.twitch.tv\r\n".encode())
        return False

def filter_words(message):
    local_message = message

    for word in WORD_IGNORE_LIST:
        ignore = ""
        replace = ""

        if ":" in word:
            splitted = word.split(":")
            ignore = splitted[0].lower()
            replace = splitted[1]
        else:
            ignore = word.lower()

        pattern = re.compile(re.escape(ignore), re.IGNORECASE)
        local_message = pattern.sub(replace, local_message)

    return local_message

def ping_sender():
    while True:
        sock.send("PING :tmi.twitch.tv\r\n".encode())
        time.sleep(300)

def load_user_ignore_list():
    global USER_IGNORE_LIST

    file = open(USER_IGNORE_PATH, "r")
    file_content = file.read()
    USER_IGNORE_LIST = file_content.split("\n")
    while "" in USER_IGNORE_LIST:
        USER_IGNORE_LIST.remove("")

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
            line = resp.split('\r\n')[0]
            if is_valid_line(line):
                message = line.split(':',2)[2]
                message = filter_words(message)
                say_single_message(message)
            
        except Exception:
            traceback.print_exc()

def run_queue_single():
    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')
            for line in resp.split('\r\n'):
                if is_valid_line(line):
                    message = line.split(':',2)[2]
                    message = filter_words(message)
                    say_single_message(message)
            
        except Exception:
            traceback.print_exc()

def run_multithread():
    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')
            for line in resp.split('\r\n'):
                if is_valid_line(line):
                    message = line.split(':',2)[2]
                    message = filter_words(message)
                    threading.Thread(target=say_single_message, args=(message,)).start()

        except Exception:
            traceback.print_exc()
            time.sleep(1)

if __name__ ==  '__main__':
    threading.Thread(target=ping_sender, args=()).start()
    if MODE == 'keepup':
        run_singlethread()
    elif MODE == 'queue':
        run_queue_single()
    elif MODE == 'multi':
        run_multithread()
    else:
        print('Please select a mode by editing the MODE variable ')
