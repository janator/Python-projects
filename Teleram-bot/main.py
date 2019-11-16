import telegram
import time
from constants import *

telegram = telegram.Telegram(TOKEN)

while True:
    telegram.get_updates()
    time.sleep(1)
