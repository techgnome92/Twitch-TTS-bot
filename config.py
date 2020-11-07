import os

settings = dict(
    server = 'irc.chat.twitch.tv',
    port = 6667,
    nickname = '', #The bots nickname
    token = 'oauth:', #Get it from https://twitchapps.com/tmi/
    channel = '#', #Channel username like '#moistcr1tikal'

    # 'keepup'  Keeping up with recent messages, some messages might be skipped.
    # 'queue'   Queuing up messages and says every message.
    # 'multi'   Say multiple messages simultaneously.

    TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
)