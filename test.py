import math
import multiprocessing
import asyncio
from asyncio import sleep
import threading
import time
import datetime
from misc.timer import timer_function


def in_001():
    list_event_name = [1, 2, 3, 4]
    # Создаем строку из FID событий для обновления их в БД
    fids = ', '.join(str(fid) for fid in list_event_name)

    print(fids)


def gorgeous_text(number: str) -> str:
    """ Функция исправляет склонение слова (событие) к числу """

    if len(number):
        number_for = number[-1]

        if len(number) > 1 and number[-2] == '1':
            ret_value = f"{number} событий"
        elif number_for == '1':
            ret_value = f"{number} событие"
        elif number_for in ['2', '3', '4']:
            ret_value = f"{number} события"
        else:  # if number_for in ['0', '5', '6', '7', '8', '9']:
            ret_value = f"{number} событий"
    else:
        ret_value = 'none событий'

    return ret_value


def f_math():

    max_index = 36
    index_step = 10

    print(math.ceil(max_index / index_step))


async def some_pros_2(a, b):
    await sleep(b * 0.05)
    print(f"{a} - {b * 0.05}")


async def some_proc(some_list: list):
    print("Создаём асинки")
    e_loop = asyncio.get_event_loop()

    loop_list = list()

    index = 1

    for it in some_list:
        loop_list.append(e_loop.create_task(some_pros_2(it, index)))
        index += 1

    for t in loop_list:
        await t

    print("Дождался результата")


def main_async(some_list):
    print("Запустил создавать асинки")
    asyncio.run(some_proc(some_list))


@timer_function
def p_main(some_list: list):

    proc = multiprocessing.Process(target=main_async, args=(some_list, ))
    # proc = threading.Thread(target=main_async, args=(some_list,))

    proc.start()

    proc.join(timeout=3)

    if proc.is_alive():
        print("Был принудительно удалён")
        proc.kill()
    else:
        print("Процесс удалился сам")


if __name__ == '__main__':

    # test_001()

    # print(gorgeous_text("21"))
    #
    # f_math()
    t1 = datetime.datetime.now()
    time.sleep(3)
    t2 = datetime.datetime.now()
    result = t2 - t1

    print(result.seconds)

    it_list = [1, 2, 3]  # , 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    # p_main(it_list)
