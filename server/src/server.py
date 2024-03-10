from flask import Flask, jsonify, request
from flask import g
from flask_cors import CORS
from db.repository import UserRepository
from db.model.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.model.team import Team
from db.model.tribe import Tribe
from db.repository import PullRequestRepository
from services.statsService import StatsService
from services.userService import UsersService, get_manager_chain
from utils import entity_as_dict
from datetime import date
from statistics import mean, median, quantiles

import logging
from datetime import datetime, timedelta
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


app = Flask(__name__)
app.debug = True # Make this False if you are not debugging
CORS(app) 

connection_string = 'postgresql://postgres:bonaventura@localhost:5432/developer_dashboard'

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string


engine = create_engine(connection_string, echo=True)


Session = sessionmaker(bind=engine)
User.metadata.create_all(engine)
Team.metadata.create_all(engine)
Tribe.metadata.create_all(engine)

def _get_request_date_args(request) -> tuple[int, datetime, datetime]:
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    return start_date, end_date

def _get_request_scope_args(request) -> tuple[int, datetime, datetime]:
    start_date, end_date = _get_request_date_args(request) 
    managerId = request.args.get('manager_id')

    return managerId, start_date, end_date

@app.before_request
def before_request():
    g.session = Session()

@app.after_request
def after_request(response):
    g.session.close()
    return response

@app.route('/api/users', methods=['GET'])
def get_users():
    isManager = request.args.get('isManager')
    userService = UserRepository(g.session)

    if isManager:
        users = userService.list_all_managers()
    else:
        users = userService.list_all().data
    
    return jsonify([entity_as_dict(user) for user in users])


@app.route('/api/stats', methods=['GET'])
def get_stats():
    managerId, start_date, end_date = _get_request_scope_args(request)
    
    statsService = StatsService(g.session)

    cues = statsService.build_cues(managerId, start_date, end_date)
    line_charts = statsService.build_line_charts(managerId, start_date, end_date)
    
    return jsonify({
        'lineCharts': line_charts,
        'cues': cues
    })


    
@app.route('/api/users', methods=['POST'])
def create_user():
    userRepository = UserRepository(g.session)

    data = request.get_json()
    user_data = User(**data)
    user = userRepository.create(user_data)
    return jsonify(entity_as_dict(user))

@app.route('/api/users', methods=['GET'])
def list_users():
    after = request.args.get('after')
    before = request.args.get('before')
    page = request.args.get('page_size')

    userRepository = UserRepository(g.session)
    page = min(int(page), 50) 
    result = userRepository.list_all(page, after=after, before=before)
    user_dicts = [entity_as_dict(user) for user in result.data]
    return jsonify({
        "before": result.before,
        "after": result.after,
        "data": user_dicts,
        "page_size": page
    })


@app.route('/api/git/prs', methods=['GET'])
def get_git_prs():
    after = request.args.get('after')
    before = request.args.get('before')
    pageSize = request.args.get('page_size')

    start_date, end_date = _get_request_date_args(request) 
    manager_id = request.args.get('manager_id')
    user_id = request.args.get('user_id')
    
    prRepository = PullRequestRepository(g.session)
    userService = UsersService(g.session)
    
    managers_ids = None
    if manager_id is not None:
        managers_ids = userService.get_manager_chain(manager_id)

    user_ids = None
    if user_id is not None:
        user_id = int(user_id)
        user_ids = [user_id]

    pageSize = min(int(pageSize), 50) 
    result = prRepository.list_all(limit=pageSize, start_date=start_date, end_date=end_date, users_ids=user_ids,  managers_ids=managers_ids, after=after, before=before)
    prs_dicts = [entity_as_dict(user) for user in result.data]

    git_stats = {
        "before": result.before,
        "after": result.after,
        "data": prs_dicts,
        "page_size": pageSize,
        "total_count": result.total_count
    }

    return jsonify(git_stats)

@app.route('/api/git/prs_stats', methods=['GET'])
def get_git_prs_stats():
    managerId, start_date, end_date = _get_request_scope_args(request)

    prRepository = PullRequestRepository(g.session)
    userService = UsersService(g.session)
    managerIds = userService.get_manager_chain(managerId)

    result = prRepository.get_avg_stats(start_date=start_date, end_date=end_date, managerIds=managerIds)

    git_stats = {
        "avg_loc": result.avg_loc,
        "avg_duration": result.avg_duration,
        "avg_files_changed": result.avg_files_changed,
        "avg_comments_count": result.avg_comments_count
    }

    return jsonify(git_stats)

@app.route('/api/users/stats', methods=['GET'])
def get_users_stats():
    managerId, start_date, end_date = _get_request_scope_args(request)
    
    userService = UsersService(g.session)
    managerIds = userService.get_manager_chain(managerId)
    statsService = StatsService(g.session)

    result = statsService.build_user_stats(managerIds, start_date, end_date)

    return jsonify(result)

@app.route('/api/users/<int:id>/stats', methods=['GET'])
def get_users_details(id:int):
    start_date, end_date = _get_request_date_args(request)
    
    userService = UsersService(g.session)
    result = userService.get_user_details(id, start_date, end_date)


    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)