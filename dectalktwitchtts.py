import os, socket, uuid
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

def run_singlethread():
    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')
            message = resp.split(':',2)[2]
            say_single_message(message)
            
        except Exception:
            pass

    sock.close()

def run_queue_single():
    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')
            for line in resp.split('\n'):
                message = line.split(':',2)[2]
                say_single_message(message)
            
        except Exception:
            pass

if __name__ ==  '__main__':
    if MODE == 'keepup':
        run_singlethread()
    elif MODE == 'queue':
        run_queue_single()
    else:
        print('Please select a mode by editing the MODE variable ')