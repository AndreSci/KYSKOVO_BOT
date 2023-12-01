from aiogram import Bot

BOT: Bot

class ChangeConst:

    @staticmethod
    def update_bot(bot) -> bool:
        global BOT
        BOT = bot

        return True