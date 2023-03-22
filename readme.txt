Требуется строгое правило написания номера при регистрации в БД пример: 79991110022

Библиотеки:
aiogram
requests
pymysql
configparser


When sending messages inside a particular chat,
avoid sending more than one message per second.
We may allow short bursts that go over this limit,
but eventually you'll begin receiving 429 errors.

If you're sending bulk notifications to multiple users,
the API will not allow more than 30 messages per second or so.
Consider spreading out notifications over large intervals of 8—12 hours for best results.