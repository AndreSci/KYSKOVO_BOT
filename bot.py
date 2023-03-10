from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from misc.settings import SettingsIni
from misc.logger import Logger


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
logger = Logger(set_ini)

# Объявляем бота
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
