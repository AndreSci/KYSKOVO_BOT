

def test_001():
    list_event_name = [1, 2, 3, 4]
    # Создаем строку из FID событий для обновления их в БД
    fids = ', '.join(str(fid) for fid in list_event_name)


    print(fids)


if __name__ == '__main__':
    test_001()