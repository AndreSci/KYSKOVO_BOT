from aiogram import Bot, Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from misc.settings import SettingsIni
from misc.logger import Logger

from misc.consts import ChangeConst


TOKEN = ''
# HTTP_REG = 'http://yurok3000.ru:8084/RegisterTGUser'
# REG_WORD = '/checkin'
# LOG_PATH = './logs/'

set_ini = SettingsIni()
ret_value = set_ini.take_settings()

# Проверяем успешность загрузки настроек API
if ret_value['RESULT'] != "SUCCESS":
    print(ret_value)
    print("ERROR\tОшибка загрузки данных из файла settings.ini\tРабота сервиса будет завершена.")
    input()
    exit(1)
else:
    TOKEN = set_ini.token

# Создаем глобальный объект для логирования
logger = Logger(set_ini.log_path)

# Объявляем бота
bot = Bot(token=TOKEN)

# Делаем объект bot общедоступным через файл consts.py
ChangeConst.update_bot(bot)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
