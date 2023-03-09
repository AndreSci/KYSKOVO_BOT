from db.connect_db import DBCon


class AuthorDB:
    """ Класс запросов к БД связанных с авторизацией """
    @staticmethod
    def find_active_session(tg_user: str) -> dict:
        """ Проверяем telegram id на активную сессию и пользователя в (tsession и tuser)"""

        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": dict()}

        # Создаем подключение
        db_con = DBCon()
        connection = db_con.connect()

        if connection['RESULT'] == "SUCCESS":
            connection = connection['DATA']['pool']

            try:
                with connection.cursor() as cur:
                    # Ищем активную сессию и активного пользователя
                    cur.execute(f"select tsession.*, tuser.FName, tuser.FPhone "
                                    f"from VIG_sender.tuser, VIG_sender.tsession "
                                    f"where tsession.FTGUID = '{tg_user}' "
                                    f"and tuser.FID = tsession.FUserID "
                                    f"and tuser.FActivity = 1 "
                                    f"and tsession.FActivity = 1")
                    user_find = cur.fetchall()

                    if user_find:
                        ret_value['RESULT'] = "SUCCESS"
                        ret_value['DATA'] = user_find[0]

                        cur.execute(f"update vig_sender.tsession "
                                    f"set FLastAccessDate = now() "
                                    f"where FID = {user_find[0]['FID']}")
                        connection.commit()

                    else:
                        ret_value['DESC'] = "Не удалось найти активного пользователя"

            except Exception as ex:
                ret_value['DESC'] = f"Процесс связи с базой данных вызвал исключение: {ex}"
        else:
            ret_value = connection

        return ret_value

    @staticmethod
    def new_session(tg_user: str, tg_name: str, phone: str) -> dict:
        """ Проверяет пользователя по номеру телефона в tuser и добавляет в tsession """

        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": dict()}

        # Создаем подключение
        db_con = DBCon()
        connection = db_con.connect()

        if connection['RESULT'] == "SUCCESS":
            connection = connection['DATA']['pool']

            try:
                with connection.cursor() as cur:
                    cur.execute(f"select * from vig_sender.tuser where FActivity = 1 and FPhone = '{phone}'")
                    user_id = cur.fetchall()

                    if user_id:
                        cur.execute(f"update vig_sender.tsession "
                                    f"set FDateClose = now(),  FActivity = 0 "
                                    f"where FTGUID = '{tg_user}' "
                                    f"and FUserID = {user_id[0]['FID']} "
                                    f"and FActivity = 1")
                        connection.commit()

                        cur.execute(f"insert into vig_sender.tsession "
                                    f"(FUserID, FTGUID, FTGName, FDateCreate, FLastAccessDate) "
                                    f"value "
                                    f"({user_id[0]['FID']}, '{tg_user}', '{tg_name}', now(), now())")

                        connection.commit()

                        ret_value['RESULT'] = "SUCCESS"
                    else:
                        ret_value['DESC'] = "Не удалось найти активного пользователя"

            except Exception as ex:
                ret_value['DESC'] = f"Процесс связи с базой данных вызвал исключение: {ex}"
        else:
            ret_value = connection

        return ret_value

    @staticmethod
    def deactivate_session(tg_user: str) -> dict:
        """ Меняет активность сессии пользователя на 0 в (tsession) """

        ret_value = {"RESULT": "ERROR", "DESC": "", "DATA": dict()}

        # Создаем подключение
        db_con = DBCon()
        connection = db_con.connect()

        if connection['RESULT'] == "SUCCESS":
            connection = connection['DATA']['pool']

            try:
                with connection.cursor() as cur:
                    # Ищем старую сессию
                    cur.execute(f"select tsession.* from VIG_sender.tuser, VIG_sender.tsession "
                                f"where tsession.FTGUID = '{tg_user}' "
                                f"and tuser.FID = tsession.FUserID "
                                f"and tuser.FActivity = 1 "
                                f"and tsession.FActivity = 1")
                    session_find = cur.fetchall()

                    if session_find:
                        cur.execute(f"update vig_sender.tsession "
                                    f"set tsession.FActivity = 0 and FLastAccessDate = now() "
                                    f"where tsession.FID = {session_find[0]['FID']}")

                        connection.commit()

                        ret_value['RESULT'] = "SUCCESS"
                    else:
                        ret_value['DESC'] = "Не удалось найти активного пользователя"

            except Exception as ex:
                ret_value['DESC'] = f"Процесс связи с базой данных вызвал исключение: {ex}"
        else:
            ret_value = connection

        return ret_value
