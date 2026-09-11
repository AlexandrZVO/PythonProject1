# Учебный проект по уроку 10.2

## Создаем ветку разработки и ветку разработки текущего домашнего задания. Реализуем в ней выполнение функций :
filter_by_state, sort_by_date, get_mask_card_number, get_mask_account, mask_account_card и get_date.
Тестируем все функции. Создаем  README-файл . Создана папка с отчетом покрытия тестами в формате HTML.
Отправляем на удаленный репозиторий и делаем pull request.

## Установка
1. Клонируйте репозитарий:
git@github.com:AlexandrZVO/PythonProject1.git
2. Создайте виртуальное окружение:
poetry shell
3. Установите зависимости:
pip install -r requirements.txt
4. Установите pytest:
poetry add --group dev pytest-cov


## Использование: 
1.1. Откройте приложение в вашем веб-браузере.
2. Создайте новый проект и начните добавлять задачи.
3. Назначайте сроки выполнения и приоритеты для задач, чтобы эффективно управлять проектами.
4. Функция filter_by_state - фильтрует список словарей, оставляя только те, у которых ключ 'state' равен значению `state`
вызов функции: print(filter_by_state([{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'}, 
                                       {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}, 
                                       {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                                       {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}]))
5. Функция sort_by_date - сортирует список словарей по дате, по возрастанию.
вызов функции: print(sort_by_date([{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                                   {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:28:58.425572'},
                                   {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:25:25.241689'},
                                   {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:20:33.419441'}
6. Функция get_mask_card_number принимает на вход номер карты и возвращает ее маску. Номер карты 
замаскирован и отображается в формате XXXX XX** **** XXXX, где X — это цифра номера. 
Вызов функции:print(get_mask_card_number("12345") 
              print(get_mask_card_number("123a4567-8901-20345"))
              print(get_mask_card_number("1234 567812345 678"))
              print(get_mask_card_number("1234567812345678"))
7. Функция get_mask_account принимает на вход номер счета и возвращает его маску. 
Номер счета замаскирован и отображается в формате **XXXX , где X  — это цифра номера. 
То есть видны только последние 4 цифры номера, а перед ними — две звездочки.
Вызов функции:print(get_mask_account("7000792  289606361"))
              print(get_mask_account("73654108430135874305  "))
              print(get_mask_account("1" * 20))
              print(get_mask_account("Visa Platinum 7000792289606361"))
              print(get_mask_account("Счет 64686473678894779589"))
8. Функция mask_account_card, которая умеет обрабатывать информацию как о картах, так и о счетах.
Вызов функции:print(mask_account_card(""))
              print(mask_account_card("Visa Classic 683198247677658"))
              print(mask_account_card("Visa Classic 683 1982 4767 37658"))
              print(mask_account_card("Visa Gold 599941 4228426353"))
9. Функция get_date, которая принимает на вход строку с датой в формате "2024-03-11T02:26:18.671407"
и возвращает строку с датой в формате "ДД.ММ.ГГГГ"  ("11.03.2024").
Вызов функции:print(get_date("2024-03-11T02:26:18.671407"))
              print(get_date("2025-06-20T15:30:45.123456"))
              print(get_date("2025-13-04"))
              print(get_date(""))

## Тестирование
Все тесты расположены в папке tests. Сделаны тестирования с помощью assert, фикстур и параметеризации. 
Тестирование расположены в файлах: test_filter_by_state.py, test_get_date.py, test_get_mask_account.py,
test_get_mask_card_number.py, test_mask_account_card.py, test_sort_by_date.py
запуск тестирвания всех тестов: введите в терминале pytest
запуск процента покрытия: введите в терминале pytest --cov
Итоговый результат тестирования:
--------------------------------------------------------
src\__init__.py                          0      0   100%
src\masks.py                            20      0   100%
src\processing.py                       13      0   100%
src\widget.py                           36      1    97%
test_main.py                             0      0   100%
tests\__init__.py                        0      0   100%
tests\test_filter_by_state.py           18      0   100%
tests\test_get_date.py                  11      0   100%
tests\test_get_mask_account.py           9      0   100%
tests\test_get_mask_card_number.py      13      1    92%
tests\test_mask_account_card.py          5      0   100%
tests\test_sort_by_date.py              24      0   100%
--------------------------------------------------------
TOTAL                                  149      2    99%


##  Лицензия:
Проект распространяется под [лицензией MIT](LICENSE).
