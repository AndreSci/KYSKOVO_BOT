import asyncio
import threading
import datetime
import time
from asyncio import sleep

import requests

from misc.timer import timer_function
from misc.consts import BOT


TIME_QUEUE = 0.04


def to_fixed(num_obj, digits=0):
    return float(f"{num_obj:.{digits}f}")


async def send_async(it: dict, loop_list: list, e_loop):
    url = f"https://api.telegram.org/bot{it.get('token')}" \
          f"/sendMessage?chat_id={it.get('user_id')}&text={it.get('text')}"

    try:
        # await sleep(to_fixed(index * TIME_QUEUE, 2))
        await sleep(TIME_QUEUE)
        loop_list.append(e_loop.run_in_executor(None, requests.get, url))

        # print(f"{index} - {to_fixed(index * TIME_QUEUE, 2)} - {url}")
    except Exception as ex:
        print(f"EXCEPTION: {ex} in {url}")


async def send_async_bot(it: dict):

    try:
        await sleep(TIME_QUEUE)

        await BOT.send_message(chat_id=it.get('user_id'), text=it.get('text'))

        with open('./error.jpg', 'rb') as photo:
            await BOT.send_photo(chat_id=it.get('user_id'), photo=photo)

        # print(f"{index} - {to_fixed(index * TIME_QUEUE, 2)} - {url}")
    except Exception as ex:
        print(f"EXCEPTION: {ex} in {it}")


async def main_proc(some_list: list) -> list:
    """ Создаем асинхронную очередь """
    e_loop = asyncio.get_event_loop()

    done_index = set()
    done_user = dict()

    loop_list = list()

    while True:
        index = 0

        # Обход по массиву сообщений
        for it in some_list:

            user_id = str(it.get('user_id'))

            if index in done_index:
                # Если index уже был обработан, пропускаем
                index += 1
                continue

            # Получаем данные пользователя из временного списка
            if user_id in done_user:
                time_user = done_user[user_id].get('time')
            else:
                time_user = None

            if time_user:
                # Сравниваем время у пользователя и время на момент запроса
                time_res = datetime.datetime.now() - time_user

                if time_res.seconds > 1:
                    done_user[user_id]['time'] = datetime.datetime.now()
                    done_index.add(index)
                    # await send_async(it, loop_list, e_loop)
                    await send_async_bot(it)
                # else:
                #     print(f"{index}: Еще рано отправлять этому пользователю сообщение")
            else:
                done_index.add(index)

                done_user[user_id] = {'time': datetime.datetime.now()}
                # await send_async(it, loop_list, e_loop)
                await send_async_bot(it)

            index += 1

        for t in loop_list:
            await t
            t.result().json()

        if len(done_index) == len(some_list):
            break
        else:
            time.sleep(0.4)

    print("Дождался результата")


res_proc = list()


def main_async(message_list):
    global res_proc
    res_proc = asyncio.run(main_proc(message_list))

    print(res_proc)


@timer_function
def process_sender(message_list: list):

    # proc = multiprocessing.Process(target=main_async, args=(some_list, ))
    proc = threading.Thread(target=main_async, args=(message_list,), daemon=True)

    proc.start()
    proc.join()


if __name__ == "__main__":
    # Проверяем работоспособность
    test_list = [{'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello1'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello2'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello3'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello4'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello5'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello6'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello7'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello8'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello9'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello10'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello11'},
               {'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello12'}]

    process_sender(test_list)
