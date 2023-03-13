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


class SendMiss:
    """ Класс сбора ошибок при отправках сообщений """
    def __init__(self):
        self.miss_list = list()

    def add(self, user_id: str, text: str):
        """ Функция сбора ошибок отправки """
        self.miss_list.append([user_id, text])

    def save(self):
        """ Функция сохраняет неудачные сообщения в файл если есть хотя бы одно пропущенное сообщение """

        if len(self.miss_list) > 0:
            today = datetime.datetime.today()
            for_file_name = str(today.strftime("%Y-%m-%d"))
            date_time = str(today.strftime("%Y-%m-%d/%H.%M.%S"))

            # Открываем и записываем логи в файл отчета.
            with open(f'./missed_message/{for_file_name}.txt', 'a', encoding='utf-8') as file:
                file.write(f"{date_time} - {self.miss_list}")


def start_event_manager(token: str):
    """ Основная функция запуска сбора событий из БД """

    ev_mng = EventManagerBD(token)

    logger.add_log(f"EVENT\tstart_event_manager\tПоиск событий Активен")

    time.sleep(2)
    index = 30

    while DO_SEARCHING:
        time.sleep(1)

        # Каждый 30 index проверяем базу на событие, сделано для быстрой остановки потока
        if index >= 30:
            index = 0
            events_for = ev_mng.take_events()

            # класс сбора пропущенных сообщений
            miss_mess = SendMiss()

            if events_for:

                list_event_name = list()
                logger.add_log(f"EVENT\tstart_event_manager\tНайдено {len(ev_mng.all_events_id)} событий, "
                               f"идет процесс обработки...")
                logger.add_log(f"EVENT\tstart_event_manager\tСписок FID событий: {ev_mng.all_events_id}",
                               print_it=False)

                for it in ev_mng.events:

                    # Если нужно срочно отменить рассылку
                    if not DO_SEARCHING:
                        logger.add_log(f"WARNING\tstart_event_manager\t"
                                       f"Рассылка была экстренно отключена администратором")
                        return 2

                    # отправляем сообщение
                    ev_mng.send_telegram(it['FTGUID'], f"{it['FDateEvent']}\n{it['FEventMessage']}", miss_mess)

                    # Проверяем и добавляем в список обработанных событий
                    if it['EFID'] not in list_event_name:
                        list_event_name.append(it['EFID'])

                logger.add_log(f"EVENT\tstart_event_manager\tПропущенных сообщение при рассылке "
                               f"{len(miss_mess.miss_list)}")
                logger.add_log(f"EVENT\tstart_event_manager\t"
                               f"Список всех событий которые имели адресата: {list_event_name}", print_it=False)

                result_update = EventDB.done_events(ev_mng.all_events_id)

                logger.add_log(f"{result_update['RESULT']}\tstart_event_manager\t"
                               f"Результат обновления БД: {result_update}")

        index += 1

    logger.add_log(f"WARNING\tstart_event_manager\tПоток для поиска событий в БД завершил свою жизнь.")


class EventManagerBD:
    """ Класс служит для обработки Event из Базы данных """

    def __init__(self, token):
        self.events = list()
        self.all_events_id = list()  # Список всех id событий для обнуления
        self.token = token

    def take_events(self) -> bool:
        """ Получаем список событий из БД (TEvent)"""

        ret_value = False

        db_result = EventDB.find_events()

        if db_result['RESULT'] == "SUCCESS":
            self.events = db_result['DATA']['FOR_SEND']
            self.all_events_id = []  # обнуляем список

            # Создаем список всех событий для обнуления
            for it in db_result['DATA'].get('ALL'):
                self.all_events_id.append(it.get('FID'))

            ret_value = True

        return ret_value

    def update_event(self, fid) -> bool:
        """ Функция меняет поле FProcessed = 1 в БД TEvent по FID """
        ret_value = False

        db_result = EventDB.done_event(fid)

        if db_result['RESULT'] == "SUCCESS":
            logger.add_log(f"EVENT\tEventManager.update_event\tСобытие {fid} было успешно обработано", print_it=False)
            ret_value = True
        else:
            logger.add_log(f"ERROR\tEventManager.update_event\tОшибка редактирования события: {db_result}")

        return ret_value

    def send_telegram(self, user_id: str, text: str, miss_mess: SendMiss):
        """ Функция отправляет сообщение пользователю через API telegram """

        ret_value = False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={user_id}&text={text}"

        try:
            result = requests.get(url, timeout=5).json()

            if not result.get('ok'):
                miss_mess.add(user_id, text)
                logger.add_log(f"WARNING\tsend_telegram\t"
                               f"Не удалось отправить сообщение пользователю: {user_id} - {text}")
            else:
                logger.add_log(f"SUCCESS\tsend_telegram\tУспешно отправлено сообщение для {user_id} - {text}",
                               print_it=False)
                ret_value = True

        except Exception as ex:
            logger.add_log(f"ERROR\tsend_telegram\tВозникла ошибка при попытке отправить сообщение: {ex}")
            miss_mess.add(user_id, text)

        return ret_value


class EventThread:
    """ Класс служит для запуска и остановки потока который ожидает событие """

    @staticmethod
    def start(user_id: str, token: str):
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
            logger.add_log(f"ERROR\tEventThread.start\tПоток для поиска событий уже запущен")

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
