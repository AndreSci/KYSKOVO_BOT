import threading
import asyncio
import datetime

from db.requests.author import AuthorDB


class RequestType:
    FIND_SESSION = 0  # Найти активную сессию по id телеграм
    NEW_SESSION = 1  # Добавить новую сессию на id телеграм
    DEL_SESSION = 2  # Деактивировать сессию пользователя


class BDThread:
    def __init__(self):
        self.ret_value = {"RESULT": "SUCCESS", "DESC": "", "DATA": dict()}

    def run_request(self, *args):
        """Описание значений: \n
        FIND_SESSION = 0  # Найти активную сессию по id телеграм \n
        NEW_SESSION = 1  # Добавить новую сессию по id телеграм - имя - номер телефона \n
        DEL_SESSION = 2  # Деактивировать сессию по id телеграм \n
        """

        request_item = args[0]

        if request_item == RequestType.FIND_SESSION:
            self.ret_value = AuthorDB.find_active_session(args[1])
        elif request_item == RequestType.NEW_SESSION:
            self.ret_value = AuthorDB.new_session(args[1], args[2], args[3])
        elif request_item == RequestType.DEL_SESSION:
            self.ret_value = AuthorDB.deactivate_session(args[1])
        else:
            msg = f"{datetime.datetime.now()}\tAsyncThread.run_request\tНе удалось найти {args[0]}"
            print(msg)
            self.ret_value['DESC'] = msg

    # Шаблонная функция создания потока с асинхронным ожиданием завершения потока
    async def thread_con_db(self, *args):
        """Описание значений: \n
        FIND_SESSION = 0  # Найти активную сессию по id телеграм \n
        NEW_SESSION = 1  # Добавить новую сессию по id телеграм - имя - номер телефона \n
        DEL_SESSION = 2  # Деактивировать сессию по id телеграм \n
        """

        th = threading.Thread(target=BDThread.run_request, args=args)
        th.start()

        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": dict()}
        index = 0

        # 50 итераций примерно 5 сек ожидания завершения потока
        # в случаи истечении времени возвращает ERROR
        # перепроверка данных отдана на усмотрение пользователя
        while index < 50:
            index += 1
            if not th.is_alive():
                break

            await asyncio.sleep(0.1)

        if ret_value['RESULT'] == "ERROR":
            ret_value['DESC'] = "Проблема связи с БД"
        else:
            ret_value = self.ret_value

        return ret_value
