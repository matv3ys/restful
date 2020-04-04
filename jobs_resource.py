from main import *
from parsers import job_parser
from parsers import job_edit_parser


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'jobs': job.to_dict(
            only=('id', 'job',
                  'team_leader', 'work_size',
                  'collaborators', 'is_finished'))})

    def put(self, job_id):
        abort_if_job_not_found(job_id)
        args = job_edit_parser.parse_args()
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        job_dict = job.to_dict(only=('id', 'job',
                                     'team_leader', 'work_size',
                                     'collaborators', 'is_finished'))
        for key in args:
            job_dict[key] = args[key]
        job.id = job_dict['id']
        job.job = job_dict['job']
        job.team_leader = job_dict['team_leader']
        job.work_size = job_dict['work_size']
        job.collaborators = job_dict['collaborators']
        job.is_finished = job_dict['is_finished']
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=('id', 'job', 'is_finished')) for item in jobs]})

    def post(self):
        args = job_parser.parse_args()
        session = db_session.create_session()
        job = Jobs(
            job=args['job'],
            team_leader=args['team_leader'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            is_finished=args['is_finished'],
        )
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")
