""" Запускается в последнюю очередь для корректной загрузки информации бота"""
import asyncio
import threading
import time
import requests

from db.requests.events import EventDB
from misc.logger import Logger
from bot import bot, logger

from asyncio import sleep

import datetime
from misc.timer import timer_function

DO_SEARCHING = True
THREAD_LIFE = threading.Thread()

# Переменные для сбора неудачных сообщений
THREAD_LOCK_MASS = threading.Lock()
MISS_MASS = list()


# Функция сбора пропущенных или ошибочных сообщений
def add_miss_mass(user_id: str, text: str):
    global MISS_MASS

    with THREAD_LOCK_MASS:
        MISS_MASS.append([user_id, text])


# Основная функция запуска сбора событий из БД
def start_event_manager(token: str):
    ev_mng = EventManagerBD(token)

    print("Поиск событий Активен\n")
    time.sleep(2)
    index = 30

    while DO_SEARCHING:
        time.sleep(1)

        # Каждый 30 index проверяем базу на событие, сделано для быстрой остановки потока
        if index >= 30:
            index = 0
            events_for = ev_mng.take_events()

            if events_for:

                list_event_name = list()
                logger.add_log(f"EVENT\tstart_event_manager\t{events_for}", print_it=False)

                for it in ev_mng.events:
                    # Создаем отдельный поток на запрос
                    # ev_mng.send_telegram(it['FTGUID'], it['FEventMessage'])

                    tr = threading.Thread(target=ev_mng.send_telegram, args=[it['FTGUID'], it['FEventMessage']])

                    tr.start()
                    # ev_mng.send_telegram(it['FTGUID'], it['FEventMessage'])
                    time.sleep(0.1)     # TODO ПРОТЕСТИРОВАТЬ НА СКОРОСТЬ

                    if it['EFID'] not in list_event_name:
                        list_event_name.append(it['EFID'])

                        db_result = EventDB.done_event(it['EFID'])
                        logger.add_log(f"EVENT\tstart_event_manager\t{db_result}", print_it=False)

        index += 1

    logger.add_log(f"WARNING\tstart_event_manager\tПоток для поиска событий в БД завершил свою жизнь.")


class EventManagerBD:
    """ Класс служит для обработки Event из Базы данных """

    def __init__(self, token):
        self.events = list()
        self.token = token

    def take_events(self) -> bool:
        """ Получаем список событий из БД (TEvent)"""
        db_result = EventDB.find_events()

        if db_result['RESULT'] == "SUCCESS":
            self.events = db_result['DATA']
        else:
            return False

        return True

    def update_event(self, fid) -> bool:
        """ Функция меняет поле FProcessed = 1 в БД TEvent по FID """

        db_result = EventDB.done_event(fid)

        if db_result['RESULT'] == "SUCCESS":
            logger.add_log(f"EVENT\tEventManager.update_event\tСобытие {fid} было успешно обработано", print_it=False)
        else:
            logger.add_log(f"ERROR\tEventManager.update_event\tОшибка редактирования события: {db_result}")
            return False

        return True

    def send_telegram(self, user_id: str, text: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={user_id}&text={text}"

        try:
            result = requests.get(url, timeout=5).json()

            if not result.get('ok'):
                add_miss_mass(user_id, text)
                logger.add_log(f"WARNING\tsend_telegram\tНе удалось отправить сообщение пользователю: {user_id}")
            else:   # TODO добавить print_if=False
                logger.add_log(f"SUCCESS\tsend_telegram\tУспешно отправлено сообщение для {user_id}")

        except Exception as ex:
            add_miss_mass(user_id, text)
            logger.add_log(f"ERROR\tsend_telegram\tВозникла ошибка при попытке сделать запрос {ex}")

        return True


class EventThread:
    """ Класс служит для запуска и остановки потока который ожидает событие """

    @staticmethod
    def start(user_id: str, token: str):  # TODO убрать глобальный токен
        """ Функция создает поток для поиска событий в БД """

        global DO_SEARCHING
        global THREAD_LIFE

        if not THREAD_LIFE.is_alive():

            DO_SEARCHING = True
            THREAD_LIFE = threading.Thread(target=start_event_manager, args=[token, ])
            THREAD_LIFE.start()

            logger.add_log(f"EVENT\tEventThread.start\t"
                           f"Пользователь {user_id} запустил поиск событий для рассылки сообщений")
        else:
            logger.add_log(f"ERROR\t\tОшибка запуска потока для отслеживания Событий из БД")

    @staticmethod
    async def stop(user_id: str):
        """ Функция останавливает цикл поиска событий в БД """
        ret_value = False

        logger.add_log(f"EVENT\tEventThread.stop\t"
                       f"Пользователь {user_id} отправил запрос на остановку поиска событий")

        global DO_SEARCHING
        DO_SEARCHING = False

        index = 0
        # Цикл проверяет завершение потока примерно 35 секунд
        while index < 350:
            index += 1

            if THREAD_LIFE.is_alive():
                # Асинхронное ожидание sleep предоставляет действие другим методам бота для действия
                await asyncio.sleep(0.1)
            else:
                # Если поток остановлен возвращаем успех
                ret_value = True
                break

        if ret_value:
            logger.add_log(f"EVENT\tEventThread.stop\tУспешно остановлен поток для событий")
        else:
            logger.add_log(f"ERROR\tEventThread.stop\t"
                           f"Не удалось дождаться за отведенное время завершение потока Событий")

        return ret_value
