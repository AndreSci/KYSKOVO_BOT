import threading
import os
import configparser

from bot import bot, logger

TH_LOCK_FILE = threading.Lock()
TH_LOCK_USERS = threading.Lock()


class AllowedUser:
    """ Класс configparser работает с str """

    def __init__(self):
        self.allow_users = dict()
        self.file = configparser.ConfigParser()

    def read_file(self):
        """ Функция загрузки данных IP в словарь класса """

        with TH_LOCK_FILE:
            if os.path.isfile("allowed_users.ini"):
                try:
                    # Загружаем данные из динамичного файла allowed_ip.ini
                    self.file.read("allowed_users.ini", encoding="utf-8")

                    self.allow_users = dict()  # Обнуляем словарь доступа

                    for key, val in self.file["USERS"].items():
                        self.allow_users[key] = int(val)

                except KeyError as ex:
                    logger.add_log(f"ERROR\tAllowedUser.read_file\tОшибка по ключу словаря - {ex}")
                except Exception as ex:
                    logger.add_log(f"ERROR\tAllowedUser.read_file\tException - {ex}")

    def find_user(self, user_id: str, activity_lvl=1) -> bool:
        """ Функция поиска user в словаре """

        ret_value = False

        with TH_LOCK_USERS:  # Блокируем потоки

            self.read_file()  # Подгружаем данные из файла

            if user_id in self.allow_users:
                if int(self.allow_users[user_id]) >= activity_lvl:
                    ret_value = True
            else:
                logger.add_log(f"ERROR\tAllowedUser.read_file\t"
                               f"Пользователь {user_id} не имеет прав на данное действие.", print_it=False)

        return ret_value

    def add_user(self, new_user: str, activity=1) -> bool:
        """ Функция добавляет IP пользователя в файл со значением str(0)\n
            или если указан как allow_user='1' """
        ret_value = False

        with TH_LOCK_USERS:  # Блокируем потоки

            self.read_file()  # Подгружаем данные из файла

            self.file["USERS"][new_user] = str(activity)
            self.allow_users[new_user] = str(activity)  # Обязательно должна быть строка

            if os.path.isfile("allowed_users.ini"):
                try:
                    with open('allowed_users.ini', 'w') as configfile:
                        self.file.write(configfile)

                    ret_value = True

                    logger.add_log(f"SUCCESS\tAllowedUser.add_user\t"
                                   f"IP - {new_user} добавлен в систему со значением {activity} ")
                except Exception as ex:
                    logger.add_log(f"ERROR\tAllowedUser.add_user\tОшибка открытия или записи в файл - {ex}")

        return ret_value

