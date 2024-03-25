import os
from flask import Flask, abort, jsonify, request, send_from_directory
from flask import g
from flask_cors import CORS
from db.model.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.model.team import Team
from db.repository import PullRequestRepository, UserRepository, PullRequestReviewRepository, TeamRepository
from app_auth import validate_token
from services.githubService import GithubService
from services.statsService import StatsService
from services.userService import UsersService
from utils import entity_as_dict
import logging
from datetime import datetime
import app_config

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__, static_folder='static')
app.debug = os.getenv('DEBUG')
CORS(app) 

def authorize_api_endpoints():
    if request.path.startswith('/api/') and not validate_token():
        abort(401, description="Invalid or missing token.")

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('static/dist/assets', path)

@app.route('/thumbnails/<path:path>')
def serve_thumbnails(path):
    return send_from_directory('static/dist/thumbnails', path)

@app.route('/.well-known/<path:path>')
def serve_well_known(path):
    return send_from_directory('static/dist/.well-known', path)

@app.route('/public/<path:path>')
def serve_public(path):
    return send_from_directory('static/dist/', path)

@app.route('/')
def serve_react_app():
    return send_from_directory('static/dist', 'index.html')

connection_string = os.getenv('SQL_DATABASE_URI') #'postgresql://postgres:bonaventura@localhost:5432/developer_dashboard'
# connection_string = 'postgresql://postgres:bonaventura@host.docker.internal:5432/developer_dashboard'


app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
engine = create_engine(connection_string, echo=True)

Session = sessionmaker(bind=engine)
User.metadata.create_all(engine)
Team.metadata.create_all(engine)

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
    authorize_api_endpoints()

@app.after_request
def after_request(response):
    g.session.close()
    return response

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

@app.route('/api/users', methods=['PUT'])
def update_user():
    userRepository = UserRepository(g.session)

    data = request.get_json()
    user_data = User(**data)
    user = userRepository.update(user_data)
    return jsonify(entity_as_dict(user))


@app.route('/api/users', methods=['GET'])
def list_users():
    after = request.args.get('after')
    before = request.args.get('before')
    page = request.args.get('page_size', default=20, type=int)

    userRepository = UserRepository(g.session)
    result = userRepository.list_all(page, after=after, before=before)
    return jsonify({
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": page
    })

@app.route('/api/git/prs', methods=['GET'])
def get_git_prs():
    after = request.args.get('after')
    before = request.args.get('before')
    pageSize = request.args.get('page_size', default=20, type=int)

    start_date, end_date = _get_request_date_args(request) 
    manager_id = request.args.get('manager_id')
    user_id = request.args.get('user_id')
    sort_by = request.args.get('s')
    sort_order = request.args.get('so', default='asc')
    
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
    result = prRepository.list_all(
        limit=pageSize, 
        start_date=start_date,
        end_date=end_date, 
        users_ids=user_ids,  
        managers_ids=managers_ids, 
        after=after, 
        before=before,
        sort_by=sort_by,
        sort_order=sort_order)

    git_stats = {
        "before": result.before,
        "after": result.after,
        "data": result.data,
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

@app.route('/api/users/<int:id>/reviews', methods=['GET'])
def get_users_reviews(id:int):
    start_date, end_date = _get_request_date_args(request)
    pageSize = request.args.get('page_size', default=20, type=int)
    after = request.args.get('after')
    before = request.args.get('before')

    reviewsRepo = PullRequestReviewRepository(g.session)
    result = reviewsRepo.list_all(id, start_date, end_date, limit=pageSize, after=after, before=before)


    return jsonify({
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": 20,
        "total_count": result.total_count
        })

@app.route('/api/teams', methods=['GET'])
def get_teams():
    pageSize = request.args.get('page_size', default=20, type=int)
    after = request.args.get('after')
    before = request.args.get('before')

    teamsRepo = TeamRepository(g.session)
    result = teamsRepo.list_all(limit=pageSize, after=after, before=before)
    
    return jsonify({
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": pageSize,
        "total_count": result.total_count
    })

@app.route('/api/teams', methods=['POST'])
def create_team():
    data = request.get_json()
    team = Team(**data)

    teamsRepo = TeamRepository(g.session)
    result = teamsRepo.create_team(team) 
    
    return jsonify(entity_as_dict(result))

@app.route('/wh/github', methods=['POST'])
def github_wh_callback():
    event = request.headers["X-GitHub-Event"]
    deliveryId = request.headers["X-GitHub-Delivery"]
    signature = request.headers["X-Hub-Signature-256"]
    userAgent = request.headers["User-Agent"]
    installationTargetType = request.headers["X-GitHub-Hook-Installation-Target-Type"]
    installationTargetId = request.headers["X-GitHub-Hook-Installation-Target-Id"]

    if not userAgent.startswith("GitHub-Hookshot/"):
        print(f"Invalid user agent: {userAgent}")
        return "", 404

    data = request.get_json()
    
    githubService = GithubService()
    # TODO: vlidate signature
    githubService.record_event(event, deliveryId, installationTargetType, installationTargetId, data)
    
    return "", 200


@app.route('/api/teams', methods=['PUT'])
def update_team():
    data = request.get_json()
    team = Team(**data)

    teamsRepo = TeamRepository(g.session)
    result = teamsRepo.update_team(team) 
    
    return jsonify(entity_as_dict(result))

@app.route('/api/teams/<id>', methods=['DELETE'])
def delete_team(id:str):
    teamsRepo = TeamRepository(g.session)
    teamsRepo.delete_team(id) 
    
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

    

    