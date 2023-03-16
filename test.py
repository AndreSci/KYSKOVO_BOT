import math

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


if __name__ == '__main__':

    # test_001()

    print(gorgeous_text("21"))

    f_math()