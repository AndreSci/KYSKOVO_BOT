

class NormalizeNumber:
    """ Класс предназначен для правки номера """

    @staticmethod
    def do_normal(number: str) -> str:
        normal = list()

        for it in number:

            if it.isdigit():
                normal.append(it)

        ret_value = ''.join(normal)

        if len(ret_value) >= 10:
            ret_value = '7' + ret_value[-10:]
        elif len(ret_value) < 10:
            print("Возможно ошибка в номере")

        return ret_value


if __name__ == "__main__":
    print(NormalizeNumber.do_normal('8966-111-00-11'))
    print(NormalizeNumber.do_normal('8 966-111-00-11'))
    print(NormalizeNumber.do_normal('+78966-111-00-11'))
    print(NormalizeNumber.do_normal('8 966 111 00 11'))
    print(NormalizeNumber.do_normal('8 966 111 00 11.'))
    print(NormalizeNumber.do_normal('8 966 111b 00 11a'))
    print(NormalizeNumber.do_normal('8 966 ф111 00 11'))
