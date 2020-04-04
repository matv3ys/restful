import flask
from data import db_session
from data.jobs import Jobs
from flask import jsonify, make_response, request

blueprint = flask.Blueprint('jobs_api', __name__,
                            template_folder='templates')


# все работы (задача 1)
@blueprint.route('/api/jobs')
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('id', 'job', 'team_leader'))
                 for item in jobs]
        }
    )


# одна работа (задача 2)
@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'job': job.to_dict(only=('id', 'job',
                                     'team_leader', 'work_size',
                                     'collaborators', 'is_finished'))
        }
    )


# добавление работы (задача 3)
@blueprint.route('/api/jobs', methods=['POST'])
def create_job():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'job', 'team_leader', 'work_size', 'collaborators', 'is_finished']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    exist = bool(session.query(Jobs).get(request.json['id']))  # задача 5
    if exist:
        return jsonify({'error': 'Id already exists'})
    job = Jobs(
        id=request.json['id'],
        job=request.json['job'],
        team_leader=request.json['team_leader'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators'],
        is_finished=request.json['is_finished']
    )
    session.add(job)
    session.commit()
    return jsonify({'success': 'OK'})


# удаление работы (задача 7)
@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_news(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    session.delete(job)
    session.commit()
    return jsonify({'success': 'OK'})


# редактирование работы (задача 9)
@blueprint.route('/api/jobs/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    if not request.json:  # проверка пустого запроса
        return jsonify({'error': 'Empty request'})
    for key in request.json:  # проверяем все ключи на корректность
        if key not in ['id', 'job', 'team_leader', 'work_size', 'collaborators', 'is_finished']:
            return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:  # проверяем, есть ли нужная работа в БД
        return jsonify({'error': 'Not found'})
    job_dict = job.to_dict(only=('id', 'job',
                                 'team_leader', 'work_size',
                                 'collaborators', 'is_finished'))  # приводим нужную работу к словарю
    for key in request.json:
        job_dict[key] = request.json[key]  # редактируем нужные данные
    job.id = job_dict['id']  # работаем непосредственно с объектом, некоторые значения останутся без изменения
    job.job = job_dict['job']
    job.team_leader = job_dict['team_leader']
    job.work_size = job_dict['work_size']
    job.collaborators = job_dict['collaborators']
    job.is_finished = job_dict['is_finished']
    session.commit()
    return jsonify({'success': 'OK'})


# обработчики ошибок

@blueprint.app_errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@blueprint.app_errorhandler(500)
def value(error):
    return make_response(jsonify({'error': 'ValueError'}), 500)
