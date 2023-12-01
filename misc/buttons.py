from aiogram import types

SEND_CONTACTS = "Подписаться"
TAKE_STATUS = "Получить статус"
HELP = "Помощь"

TEXT_HELP = "Команды для канала.\n" \
            "Для отписки от канала: /Unsubscribe\n" \
            "Для получения статуса: /Take_status\n" \
            "Для получение подсказок: /help"

TEXT_HELP_ADMIN = "Команды для канала.\n" \
            "Для отписки от канала: /Unsubscribe\n" \
            "Для получения статуса: /Take_status\n" \
            "Включить рассылку: /on_newsletter\n" \
            "Отключить рассылку: /off_newsletter\n" \
            "Уведомить о тех. работе /system_warning\n" \
            "Для получение подсказок: /help"

LIST_ECHO = ["включить рассылку", "выключить рассылку"]


class UserAuthor:
    """ Класс создания кнопок регистрации """

    @staticmethod
    def take_status():
        """ Кнопка 'Получить статус' """
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text=TAKE_STATUS)
        button_help = types.KeyboardButton(text=HELP)
        keyboard.add(button_phone)
        keyboard.add(button_help)

        return keyboard

    @staticmethod
    def take_contacts():
        """ Кнопка 'Отправить телефон' """

        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text=SEND_CONTACTS,
                                            request_contact=True)
        keyboard.add(button_phone)

        return keyboard
