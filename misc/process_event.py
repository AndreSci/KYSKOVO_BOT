import multiprocessing
import asyncio
from asyncio import sleep

import requests

from misc.timer import timer_function


TIME_QUEUE = 0.03


def to_fixed(num_obj, digits=0):
    return float(f"{num_obj:.{digits}f}")


async def main_proc(some_list: list) -> list:
    """ Создаем асинхронную очередь """
    print("Создаём асинки")
    e_loop = asyncio.get_event_loop()

    loop_list = list()

    index = 1

    for it in some_list:
        url = f"https://api.telegram.org/bot{it.get('token')}" \
              f"/sendMessage?chat_id={it.get('user_id')}&text={it.get('text')}"

        try:
            # await sleep(to_fixed(index * TIME_QUEUE, 2))
            await sleep(TIME_QUEUE)
            loop_list.append(e_loop.run_in_executor(None, requests.get, url))

            # print(f"{index} - {to_fixed(index * TIME_QUEUE, 2)} - {url}")
        except Exception as ex:
            print(f"EXCEPTION: {ex} in {url}")

        index += 1

    for t in loop_list:
        await t

    print("Дождался результата")

    return loop_list

res_proc = list()


def main_async(some_list):
    global res_proc
    print("Запустил создавать асинки")
    res_proc = asyncio.run(main_proc(some_list))

    print(res_proc)


@timer_function
def process_sender(some_list: list):

    proc = multiprocessing.Process(target=main_async, args=(some_list, ))
    # proc = threading.Thread(target=main_async, args=(some_list,))

    proc.start()

    proc.join()

    if proc.is_alive():
        print("Был принудительно удалён")
        proc.kill()
    else:
        print("Процесс удалился сам")


if __name__ == "__main__":

    it_list = [{'token': '5449524516:AAFV-ay5kVR9dP3d7EsjwibWg65TbMBKgAY', 'user_id': '382507782', 'text': 'hello1'},
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

    process_sender(it_list)
