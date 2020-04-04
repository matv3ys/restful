from requests import get, post, delete

print('Тест 1: получение списка пользователей')
print(get('http://localhost:5000/api/v2/users').json())
print()
print('Тест 2: добавление нового пользователя')
print(post('http://localhost:5000/api/v2/users', json={"name": "Test2",
                                                       "surname": "User2",
                                                       "age": 99,
                                                       "position": "astronaut",
                                                       "speciality": "testing",
                                                       "address": "module_test",
                                                       "email": "test_2@mars.org"}).json())
print('Тест 3: добавление пользователя с пустым запросом')
print(post('http://localhost:5000/api/v2/users').json())
print('Тест 4: добавление нового пользователя с неполным набором аргументов')
print(post('http://localhost:5000/api/v2/users', json={"name": "Test2",
                                                       "surname": "User2",
                                                       "age": 99,
                                                       "speciality": "testing",
                                                       "address": "module_test",
                                                       "email": "test@mars.org"}).json())
print()
print('Список пользователей после 2,3,4 тестов')
print(get('http://localhost:5000/api/v2/users').json())
print()
print('Тест 5: удаление последнего добавленного пользователя')
print(delete('http://localhost:5000/api/v2/users/8').json())  # 8 - id последнего в моей БД
print()
print('Тест 6: удаление пользователя (вместо id - строка)')
print(delete('http://localhost:5000/api/v2/users/q').json())
print()
print('Тест 7: удаление пользователя (несуществующий id)')
print(delete('http://localhost:5000/api/v2/users/121').json())
print()
print('Список пользователей после 5,6,7 тестов')
print(get('http://localhost:5000/api/v2/users').json())
print()
print('Тест 8: получение одного пользователя')
print(get('http://localhost:5000/api/v2/users/1').json())
print()
print('Тест 9: получение одного пользователя (вместо id - строка)')
print(get('http://localhost:5000/api/v2/users/q').json())
print()
print('Тест 10: получение одного пользователя (несуществующий id)')
print(get('http://localhost:5000/api/v2/users/122').json())