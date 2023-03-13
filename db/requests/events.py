from db.connect_db import DBCon


class EventDB:
    """ Класс запросов к БД связанных с событиями VIG_sender.TEvent """
    @staticmethod
    def find_events() -> dict:
        """ Проверяем в БД поле VIG_sender.TEvent на не обработанные события и ставит FProcessed = 1 """

        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": dict()}

        # Создаем подключение
        db_con = DBCon()
        connection = db_con.connect()

        if connection['RESULT'] == "SUCCESS":
            connection = connection['DATA']['pool']

            try:
                with connection.cursor() as cur:
                    # Ищем активную сессию и активного пользователя
                    cur.execute(f"select tsession.FTGUID, tevent.FEventMessage, tevent.FDateEvent, "
                                f"tevent.FID as EFID "
                                f"from vig_sender.Tevent, vig_sender.tgroupeventtype, vig_sender.tusergroup, "
                                f"vig_sender.tuser, vig_sender.tsession "
                                f"where TGroupEventType.FGroupID = TUserGroup.FGroupID "
                                f"and TGroupEventType.FEventTypeID = TEvent.FEventTypeID "
                                f"and tuser.FID = tsession.FUserID "
                                f"and tuser.fid = tusergroup.FUserID "
                                f"and TEvent.FProcessed = 0 "
                                f"and tuser.FActivity = 1 "
                                f"and tsession.FActivity = 1 "
                                f"order by EFID")

                    ret_value['DATA']['FOR_SEND'] = cur.fetchall()

                    connection.commit()

                    # Выгружаем все события, для завершения которые не имеют получателя
                    cur.execute(f"select FID from vig_sender.tevent where FProcessed = 0")

                    ret_value['DATA']['ALL'] = cur.fetchall()

                    if ret_value['DATA']['ALL']:
                        ret_value['RESULT'] = "SUCCESS"
                    else:
                        ret_value['DESC'] = "Не удалось найти активные события"

            except Exception as ex:
                ret_value['DESC'] = f"Процесс связи с базой данных вызвал исключение: {ex}"
        else:
            ret_value = connection

        return ret_value

    @staticmethod
    def done_event(fid: str) -> dict:
        """ ставит FProcessed = 1 """

        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": dict()}

        # Создаем подключение
        db_con = DBCon()
        connection = db_con.connect()

        if connection['RESULT'] == "SUCCESS":
            connection = connection['DATA']['pool']

            try:
                with connection.cursor() as cur:
                    # Ищем активную сессию и активного пользователя
                    cur.execute(f"update vig_sender.tevent set FProcessed = 1 where FID = {fid}")

                    connection.commit()
                    ret_value['DATA']['row_change'] = cur.rowcount

                ret_value['RESULT'] = "SUCCESS"

            except Exception as ex:
                ret_value['DESC'] = f"Процесс связи с базой данных вызвал исключение: {ex}"
        else:
            ret_value = connection

        return ret_value

    @staticmethod
    def done_events(list_event_name: list) -> dict:
        """ ставит FProcessed = 1 """

        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": dict()}

        # Создаем строку из FID событий для обновления их в БД
        fids = ', '.join(str(fid) for fid in list_event_name)

        # Создаем подключение
        db_con = DBCon()
        connection = db_con.connect()

        if connection['RESULT'] == "SUCCESS":
            connection = connection['DATA']['pool']

            try:
                with connection.cursor() as cur:
                    # Ищем активную сессию и активного пользователя
                    cur.execute(f"update vig_sender.tevent set FProcessed = 1 where FID in ({fids})")

                    connection.commit()

                    result = cur.rowcount

                ret_value['RESULT'] = "SUCCESS"
                ret_value['DESC'] = f"Успешно изменено {result} из {len(list_event_name)} полей"

            except Exception as ex:
                ret_value['DESC'] = f"Процесс связи с базой данных вызвал исключение: {ex}"
        else:
            ret_value = connection

        return ret_value

    @staticmethod
    def find_users(group_id: str) -> dict:
        """ Поиск пользователей связанных с группой в БД (TUserGroup)"""

        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": dict()}

        # Создаем подключение
        db_con = DBCon()
        connection = db_con.connect()

        if connection['RESULT'] == "SUCCESS":
            connection = connection['DATA']['pool']

            try:
                with connection.cursor() as cur:
                    # Ищем пользователей
                    cur.execute(f"select FUserID from vig_sender.tusergroup where FGroupID = {group_id}")
                    event_find = cur.fetchall()

                    if event_find:
                        ret_value['RESULT'] = "SUCCESS"
                        ret_value['DATA'] = event_find
                    else:
                        ret_value['DESC'] = "Не удалось найти пользователей"

                ret_value['RESULT'] = "SUCCESS"

            except Exception as ex:
                ret_value['DESC'] = f"Процесс связи с базой данных вызвал исключение: {ex}"
        else:
            ret_value = connection

        return ret_value
