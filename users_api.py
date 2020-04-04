import flask
from data import db_session
from data.users import User
from flask import jsonify, make_response, request

blueprint = flask.Blueprint('users_api', __name__,
                            template_folder='templates')


# все пользователи
@blueprint.route('/api/users')
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'name', 'surname'))
                 for item in users]
        }
    )


# один пользователь
@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'user': user.to_dict(only=('id', 'surname',
                                       'name', 'age',
                                       'position', 'speciality',
                                       'address', 'email',
                                       'city_from'))
        }
    )


# добавление пользователя
@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'password']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    exist = bool(session.query(User).get(request.json['id']))
    if exist:
        return jsonify({'error': 'Id already exists'})
    user = User(
        id=request.json['id'],
        surname=request.json['surname'],
        name=request.json['name'],
        age=request.json['age'],
        position=request.json['position'],
        speciality=request.json['speciality'],
        address=request.json['address'],
        email=request.json['email']
    )
    user.set_password(request.json['password'])
    session.add(user)
    session.commit()
    return jsonify({'success': 'OK'})


# редактирование пользователя
@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    if not request.json:  # проверка пустого запроса
        return jsonify({'error': 'Empty request'})
    for key in request.json:  # проверяем все ключи на корректность
        if key not in ['id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'password']:
            return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:  # проверяем, есть ли пользователь в БД
        return jsonify({'error': 'Not found'})
    user_dict = user.to_dict(only=('id', 'surname',
                                   'name', 'age',
                                   'position', 'speciality',
                                   'address', 'email'))  # приводим нужного пользователя к словарю
    if 'password' in request.json:
        user.set_password(request.json['password'])
    for key in request.json:
        if key == 'password':
            continue
        user_dict[key] = request.json[key]  # редактируем нужные данные
    user.id = user_dict['id']  # работаем непосредственно с объектом, некоторые значения останутся без изменения
    user.name = user_dict['name']
    user.surname = user_dict['surname']
    user.age = user_dict['age']
    user.position = user_dict['position']
    user.speciality = user_dict['speciality']
    user.address = user_dict['address']
    user.email = user_dict['email']
    session.commit()
    return jsonify({'success': 'OK'})


# удаление пользователя
@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    session.delete(user)
    session.commit()
    return jsonify({'success': 'OK'})


# обработчики ошибок

@blueprint.app_errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@blueprint.app_errorhandler(500)
def value(error):
    return make_response(jsonify({'error': 'ValueError'}), 500)
