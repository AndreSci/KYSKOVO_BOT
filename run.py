from aiogram.utils import executor
import ctypes
from bot import dp, logger, TOKEN
from misc.events import EventThread

from main import *


def run_bot():
    # Меняем имя терминала
    ctypes.windll.kernel32.SetConsoleTitleW(f"VIG_Sender (TELEGRAM bot)")
    logger.add_log(f"EVENT\trun_bot\tНачало работы VIG_Sender (кусково бот)")

    # Запускаем поток поиск событий для рассылки
    EventThread.start('run_bot', TOKEN)

    # Запускаем телеграм-бот
    executor.start_polling(dp)

    input()


if __name__ == "__main__":
    run_bot()
