import os, socket, uuid
from pydub import AudioSegment
import simpleaudio as sa


server = 'irc.chat.twitch.tv'
port = 6667
nickname = '' #The bots nickname
token = 'oauth:' #Get it from https://twitchapps.com/tmi/
channel = '#' #Channel username like '#moistcr1tikal'

TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

sock = socket.socket()
sock.connect((server, port))

sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))
resp = sock.recv(2048).decode('utf-8')
resp = sock.recv(2048).decode('utf-8')

while True:
    try:
        resp = sock.recv(2048).decode('utf-8')
        print(resp)
        message = resp.split(':',2)[2]
        session = str(uuid.uuid1())
        temp_wav = os.path.join(TMP_DIR, session+'.wav')

        message = message.replace('"', '').replace('&', '').replace('|', '').replace(';', '')

        if os.name == 'nt':
            print("say.exe -d dtalk_us.dic -w "+temp_wav+" \"[:phoneme on]"+message+"\"")
            os.system("say.exe -d dtalk_us.dic -w "+temp_wav+" \"[:phoneme on]"+message+"\"")
        else:
            print("wine say.exe -d dtalk_us.dic -w "+temp_wav+" \"[:phoneme on]"+message+"\"")
            os.system("wine say.exe -d dtalk_us.dic -w "+temp_wav+" \"[:phoneme on]"+message+"\"")

        wave_obj = sa.WaveObject.from_wave_file(temp_wav)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        os.remove(temp_wav)
    except Exception:
        pass

sock.close()
