from db.connect_db import DBCon


class SystemMsg:

    @staticmethod
    def take_all_users() -> dict:
        """ Метод предназначен для отправки всем активным пользователям сообщение о тех работах """

        ret_value = {"RESULT": "ERROR", "DESC": '', "DATA": list()}

        db_con = DBCon()
        connection = db_con.connect()

        if connection["RESULT"] == "SUCCESS":
            connection = connection['DATA']['pool']

            try:
                with connection as cur:
                    # Получаем список всех активных пользователей
                    cur.execute(f"select * from vig_sender.tuser, vig_sender.tsession "
                                f"where tuser.FActivity = 1 and tsession.FActivity = 1 and tuser.FID = FUserID")

                    ret_value['DATA'] = cur.fetchall()

                    if len(ret_value['DATA']) > 0:
                        ret_value['RESULT'] = "SUCCESS"
                    else:
                        ret_value['DESC'] = "Не удалось найти пользователей"

            except Exception as ex:
                print(f"SystemMsg:send_warning - Ошибка {ex}")