from db.requests.author import AuthorDB
from misc.buttons import *

from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from bot import dp, bot, logger, TOKEN

from misc.events import EventThread
from misc.allowed_users import AllowedUser


async def anti_flood(*args, **kwargs):
    msg = args[0]
    logger.add_log(f"WARNING\tanti_flood\t"
                   f"Ошибка многократного запроса от пользователя: {msg.from_user.id}.", print_it=False)


# Функция первого обращения к боту
@dp.message_handler(Text(equals=['/start'], ignore_case=True))
@dp.throttled(anti_flood, rate=3)
async def process_start_command(msg: types.Message, state: FSMContext):

    # Главное меню ----------------------------------------------------------------------
    user_id = msg.from_user.id
    user_name = msg.from_user.first_name

    logger.add_log(f"EVENT\tprocess_start_command\tПользователь {user_id} - {user_name} обратился к телеграм боту")

    # Проверяем пользователя
    test_user = AuthorDB.find_active_session(msg.from_user.id)
    logger.add_log(f"EVENT\tprocess_start_command\t{test_user}", print_it=False)

    if test_user.get("RESULT") == "SUCCESS":
        await bot.send_message(msg.from_user.id, f'С возвращением! Ждем новых сообщений.',
                               reply_markup=UserAuthor.take_status())
    else:
        await bot.send_message(msg.from_user.id, f'Добро пожаловать. Для регистрации нажмите кнопку {SEND_CONTACTS} '
                                                 f'и разрешите отправить ваши контактные данные.',
                               reply_markup=UserAuthor.take_contacts())


# Функция вывода сообщение и создания кнопки для регистрации
@dp.message_handler(Text(equals=['/subscribe'], ignore_case=True))
@dp.throttled(anti_flood, rate=3)
async def subscribe(msg: types.Message, state: FSMContext):
    await bot.send_message(msg.from_user.id, f'Для регистрации нажмите кнопку {SEND_CONTACTS} '
                                             f'и разрешите отправить ваши контактные данные.',
                           reply_markup=UserAuthor.take_contacts())


# Функция отписки от бота
@dp.message_handler(Text(equals=['/unsubscribe'], ignore_case=True))
@dp.throttled(anti_flood, rate=3)
async def unsubscribe(msg: types.Message, state: FSMContext):

    # Проверяем пользователя
    test_user = AuthorDB.find_active_session(msg.from_user.id)
    logger.add_log(f"EVENT\tunsubscribe\t{test_user}", print_it=False)

    if test_user.get('RESULT') == "SUCCESS":
        db_result = AuthorDB.deactivate_session(msg.from_user.id)
        logger.add_log(f"EVENT\techo_def\t{db_result}", print_it=False)

        if db_result['RESULT'] == "SUCCESS":
            await bot.send_message(msg.from_user.id, f"Вы успешно отписались от канала. "
                                                     f"Для повторной регистрации нажмите кнопку {SEND_CONTACTS}",
                                   reply_markup=UserAuthor.take_contacts())
        else:
            await bot.send_message(msg.from_user.id, f"Не удалось отписаться.",
                                   reply_markup=UserAuthor.take_status())
    else:
        await bot.send_message(msg.from_user.id, f"В доступе отказано. Требуется регистрация.",
                               reply_markup=UserAuthor.take_contacts())


# Функция подсказок
@dp.message_handler(Text(equals=['/help'], ignore_case=True))
@dp.throttled(anti_flood, rate=3)
async def help_func(msg: types.Message, state: FSMContext):
    # Проверяем пользователя
    test_user = AuthorDB.find_active_session(msg.from_user.id)
    logger.add_log(f"EVENT\thelp_func\t{test_user}", print_it=False)

    if test_user.get('RESULT') == "SUCCESS":

        test_user = AllowedUser()

        # Ищем id пользователя в файле allowed_users.ini
        if test_user.find_user(str(msg.from_user.id)):
            await bot.send_message(msg.from_user.id, TEXT_HELP_ADMIN, reply_markup=UserAuthor.take_status())
        else:
            await bot.send_message(msg.from_user.id, TEXT_HELP, reply_markup=UserAuthor.take_status())
    else:
        await bot.send_message(msg.from_user.id, f"В доступе отказано. Требуется регистрация.",
                               reply_markup=UserAuthor.take_contacts())


# Функция получения статуса зарегистрированного лица
@dp.message_handler(Text(equals=['/take_status'], ignore_case=True))
@dp.throttled(anti_flood, rate=3)
async def take_status(msg: types.Message, state: FSMContext):
    # Проверяем пользователя
    test_user = AuthorDB.find_active_session(msg.from_user.id)
    logger.add_log(f"EVENT\ttake_status\t{test_user}", print_it=False)

    if test_user.get('RESULT') == "SUCCESS":
        await bot.send_message(msg.from_user.id, f"Дата регистрации: {test_user['DATA']['FDateCreate']}.\n"
                                                 f"Имя: {test_user['DATA']['FName']}\n"
                                                 f"Телеграм имя: {test_user['DATA']['FTGName']}\n"
                                                 f"Телефон: {test_user['DATA']['FPhone']}",
                               reply_markup=UserAuthor.take_status())
    else:
        await bot.send_message(msg.from_user.id, f"Не удалось найти ваш статус. Требуется повторная регистрация.",
                               reply_markup=UserAuthor.take_contacts())


# Функция регистрации пользователя после нажатия на кнопку и передачи данных
@dp.message_handler(content_types=['contact'])
@dp.throttled(anti_flood, rate=5)
async def subscribe(msg: types.Message):

    if msg.contact is not None:

        # keyboard2 = types.ReplyKeyboardRemove()

        phone_number = str(msg.contact.phone_number)
        user_id = str(msg.contact.user_id)
        user_name = str(msg.contact.first_name)

        logger.add_log(f"EVENT\tsubscribe\tПользователь {user_id} предоставил номер телефона: {phone_number}")

        db_result = AuthorDB.new_session(user_id, user_name, phone_number)
        logger.add_log(f"EVENT\tsubscribe\t{db_result}", print_it=False)

        if db_result.get("RESULT") == "SUCCESS":
            await bot.send_message(msg.chat.id, f'Вы успешно зарегистрированы в системе.\n'
                                                    f'Для регистрации были предоставлены тел. {phone_number}\n'
                                                    f'телеграм имя {user_name} и '
                                                    f'id telegram {user_id}', reply_markup=UserAuthor.take_status())
        else:
            await bot.send_message(msg.chat.id,
                                   f"{db_result.get('DESC')}")

    else:
        logger.add_log(f"WARNING\tsubscribe\tОбращение от {msg.from_user.id} с пустым полем 'contact'")


# Функция запускает процесс поиска событий для рассылки
@dp.message_handler(Text(equals=['/on_newsletter'], ignore_case=True))
@dp.throttled(anti_flood, rate=3)
async def on_newsletter(msg: types.Message, state: FSMContext):

    test_user = AllowedUser()

    # Ищем id пользователя в файле allowed_users.ini
    if test_user.find_user(str(msg.from_user.id)):

        EventThread.start(msg.from_user.id, TOKEN)
        await bot.send_message(msg.from_user.id,
                               f"Был запущен процесс поиска событий для рассылки сообщений.")
    else:
        await bot.send_message(msg.from_user.id,
                               f"Данная команда для вас не доступна")

    # Функция запускает процесс поиска событий для рассылки


@dp.message_handler(Text(equals=['/off_newsletter'], ignore_case=True))
@dp.throttled(anti_flood, rate=3)
async def off_newsletter(msg: types.Message, state: FSMContext):
    test_user = AllowedUser()

    # Ищем id пользователя в файле allowed_users.ini
    if test_user.find_user(str(msg.from_user.id)):

        await bot.send_message(msg.from_user.id,
                               f"Ожидаем завершения процесса рассылки.")

        result = await EventThread.stop(msg.from_user.id)

        if result:
            await bot.send_message(msg.from_user.id,
                                   f"Был ОСТАНОВЛЕН процесс поиска событий для рассылки сообщений.")
        else:
            await bot.send_message(msg.from_user.id,
                                   f"Не удалось остановить процесс поиска событий. Попробуйте еще раз.")
    else:
        await bot.send_message(msg.from_user.id,
                               f"Данная команда для вас не доступна")


# Функция эхо имеет ряд команд для русского языка
@dp.message_handler(content_types=['text'])
@dp.throttled(anti_flood, rate=1)
async def echo_def(msg: types.Message, state: FSMContext):

    logger.add_log(f"EVENT\techo_def\tОбращение от пользователя {msg.from_user.id} text = {msg.text}", print_it=False)

    if msg.text.lower() == "получить статус":
        await take_status(msg, state)
    elif msg.text.lower() == "отписаться":
        await unsubscribe(msg, state)
    elif msg.text.lower() == "помощь":
        await help_func(msg, state)
