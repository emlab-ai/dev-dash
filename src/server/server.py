import os
from db.model.githubOrg import GithubOrg
from flask import Flask, abort, jsonify, redirect, request, send_from_directory
from flask import g

from flask_cors import CORS
from db.model.user import User

from db.model.team import Team
from db.repository import PullRequestRepository, UserRepository, PullRequestReviewRepository, TeamRepository, TenantRepository
from app_auth import validate_token
from db.model import GithubInstallation, GithubUser
from db.repository.repository import Repository
from app_sql import setup_sql_engine
from db.repository.githubUserRepository import GithubUserRepository
from services.githubClient import setup_github_app
from services.githubImportService import GithubImportService
from services.githubWebhookService import GithubWebhookService
from services.statsService import StatsService
from services.userService import UsersService
from datetime import datetime
import app_config
import uuid
from app_logger import logger

from utils import none_if_empty

app = Flask(__name__, static_folder='static')
app.debug = app_config.DEBUG
CORS(app) 

Session = setup_sql_engine(app)
setup_github_app()

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
    g.trace_id = request.headers.get('x-ms-request-id') or str(uuid.uuid4().hex)
    authorize_api_endpoints()

@app.after_request
def after_request(response):
    g.session.close()
    return response

@app.route('/api/stats', methods=['GET'])
def get_stats():
    managerId, start_date, end_date = _get_request_scope_args(request)
    
    statsService = StatsService(g.session)

    cues = statsService.build_cues(g.tenant.id, managerId, start_date, end_date)
    line_charts = statsService.build_line_charts(g.tenant.id, managerId, start_date, end_date)
    
    return jsonify({
        'lineCharts': line_charts,
        'cues': cues
    })


@app.route('/api/users', methods=['POST'])
def create_user():
    userRepository = UserRepository(g.session)

    data = request.get_json()
    user_data = User.from_dict(data)
    user_data.tenant_id = g.tenant.id
    user = userRepository.create(user_data)
    return jsonify(user.to_dict())

@app.route('/api/users', methods=['PUT'])
def update_user():
    userRepository = UserRepository(g.session)

    data = request.get_json()
    user_data = User.from_dict(data)
    user_data.tenant_id = g.tenant.id
    user = userRepository.update(user_data)
    user = userRepository.get(user.id, tenant_id=g.tenant.id, expand=["manager", "team"])
    return jsonify(user.to_dict())


@app.route('/api/users', methods=['GET'])
def list_users():
    after = request.args.get('after')
    before = request.args.get('before')
    page = request.args.get('page_size', default=20, type=int)

    userRepository = UserRepository(g.session)
    result = userRepository.list_all(g.tenant.id, page, after=after, before=before)
    return jsonify({
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": page
    })
    
@app.route('/api/git/users', methods=['GET'])
def get_git_users():
    after = request.args.get('after')
    before = request.args.get('before')
    page = request.args.get('page_size', default=20, type=int)

    userRepository = GithubUserRepository(g.session)
    result = userRepository.list_all(g.tenant.id, page, after=after, before=before)
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
    sort_by = request.args.get('s', default='closed_at')
    sort_order = request.args.get('so', default='desc')
    
    prRepository = PullRequestRepository(g.session)
    userService = UsersService(g.session)
    
    managers_ids = None
    github_users_ids = None
    if manager_id is not None:
        # todo: find user id for manger_id which is github user id
        
        managers_ids = userService.get_manager_chain(g.tenant.id, manager_id)
        github_users_ids = userService.get_github_user_for_manager_ids(g.tenant.id, managers_ids)

    user_ids = None
    if user_id is not None:
        user_id = int(user_id)
        user_ids = [user_id]
        github_users_ids = user_ids

    pageSize = min(int(pageSize), 50) 
    result = prRepository.list_all(
        tenant_id=g.tenant.id,
        limit=pageSize, 
        start_date=start_date,
        end_date=end_date, 
        github_users_ids=github_users_ids,  
        after=after, 
        before=before,
        sort_by=sort_by,
        sort_order=sort_order)
        
    data = [{ "id": pr["id"], 
        "author": pr["author"],
        "authorId": pr["author_id"],
        "nodeId": pr["node_id"],
        "number": pr["number"],
        "closedAt": pr["closed_at"],
        "createdAt": pr["created_at"],
        "changedFiles": pr["changed_files"],
        "deletions": pr["deletions"],
        "additions": pr["additions"],
        "body": pr["body"],
        "title": pr["title"],
        "commitsCount": pr["commits_count"],
        "firstCommitMessage": pr["first_commit_message"],
        "firstCommitDate": pr["first_commit_date"],
        "reviewThreadsCount": pr["review_threads_count"],
        "commentsCount": pr["comments_count"],
        "url": pr["url"],
        "changes": pr["changes"],
        "totalDuration": pr["total_duration"] } for pr in result.data]

    git_stats = {
        "before": result.before,
        "after": result.after,
        "data": data,
        "page_size": pageSize,
        "total_count": result.total_count
    }

    return jsonify(git_stats)

@app.route('/api/git/prs_stats', methods=['GET'])
def get_git_prs_stats():
    managerId, start_date, end_date = _get_request_scope_args(request)

    prRepository = PullRequestRepository(g.session)
    userService = UsersService(g.session)
    managerIds = None
    github_user_ids = None
    if managerId is not None:
        managerIds = userService.get_manager_chain(g.tenant.id, managerId)
        github_user_ids = userService.get_github_user_for_manager_ids(g.tenant.id, managerIds)

    result = prRepository.get_avg_stats(g.tenant.id, start_date=start_date, end_date=end_date, github_user_ids=github_user_ids)

    git_stats = {
        "count": result.count,
        "avg_loc": result.avg_loc,
        "avg_duration": result.avg_duration,
        "avg_files_changed": result.avg_files_changed,
        "avg_comments_count": result.avg_comments_count
    }

    return jsonify(git_stats)

@app.route('/api/users/stats', methods=['GET'])
def get_users_stats():
    managerId, start_date, end_date = _get_request_scope_args(request)
    
    after = request.args.get('after')
    before = request.args.get('before')
    pageSize = request.args.get('page_size', default=20, type=int)
    sort_by = request.args.get('s', default='id')
    sort_order = request.args.get('so', default='desc')
    
    userService = UsersService(g.session)    
    statsService = StatsService(g.session)
    
    managerIds = None
    userIds = None
    if managerId is not None:
        managerIds = userService.get_manager_chain(g.tenant.id, managerId)
        userIds = userService.get_github_user_for_manager_ids(g.tenant.id, managerIds)
        
    result = statsService.build_user_stats(g.tenant.id, userIds, start_date, end_date, pageSize, after, before, sort_by, sort_order)

    return jsonify(result)

@app.route('/api/users/<int:gid>/stats', methods=['GET'])
def get_users_details(gid:int):
    start_date, end_date = _get_request_date_args(request)
    
    userService = UsersService(g.session)
    result = userService.get_user_details(g.tenant.id, gid, start_date, end_date)

    return jsonify(result)

@app.route('/api/users/<int:gid>/reviews', methods=['GET'])
def get_users_reviews(gid:int):
    start_date, end_date = _get_request_date_args(request)
    pageSize = request.args.get('page_size', default=20, type=int)
    after = request.args.get('after')
    before = request.args.get('before')

    reviewsRepo = PullRequestReviewRepository(g.session)
    result = reviewsRepo.list_all(g.tenant.id, gid, start_date, end_date, limit=pageSize, after=after, before=before)

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
    result = teamsRepo.list_all(g.tenant.id, limit=pageSize, after=after, before=before)
    
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
    
    team = Team(
            name = data.get('name'), 
            parent_id=none_if_empty(data.get('parentId', None)),
            tenant_id = g.tenant.id)

    teamsRepo = TeamRepository(g.session)
    result = teamsRepo.create_team(team) 
    
    return jsonify(result.to_dict())

@app.route('/github/wh', methods=['POST'])
def github_wh_callback():
    event = request.headers["X-GitHub-Event"]
    deliveryId = request.headers["X-GitHub-Delivery"]
    signature = request.headers["X-Hub-Signature-256"]
    userAgent = request.headers["User-Agent"]

    if not userAgent.startswith("GitHub-Hookshot/"):
        print(f"Invalid user agent: {userAgent}")
        return "", 404

    data = request.get_json()
    
    githubService = GithubWebhookService(g.session)
    # TODO: vlidate signature
    githubService.record_event(event, deliveryId, data)
        
    return "", 200


@app.route('/api/teams', methods=['PUT'])
def update_team():
    data = request.get_json()
    team = Team(**data)

    teamsRepo = TeamRepository(g.session)
    result = teamsRepo.update_team(team) 
    
    return jsonify(result.to_dict())

@app.route('/api/teams/<id>', methods=['DELETE'])
def delete_team(id:str):
    teamsRepo = TeamRepository(g.session)
    teamsRepo.delete_team(id) 
    
    return '', 204


@app.route('/api/tenant', methods=['GET'])
def get_tenant():
    return jsonify(g.tenant.to_dict())


@app.route('/github/installation', methods=['GET'])
def register_installation_id():
    installation_id = request.args.get('installation_id')
    setup_action = request.args.get('setup_action')
    installation_token = request.args.get('state')

    installationRepository = Repository(GithubInstallation, g.session)
    if setup_action == 'install':
        
        inst = installationRepository.find_one(GithubInstallation.installation_token == installation_token)
        if inst is None:
            logger.error("Invalid installation token")
            return redirect('/404')
        
        if inst.installation_id is not None:
            logger.error("Installation token already used")
            return redirect('/settings/github')
        
        inst.installation_id = installation_id
        inst.installation_token = None

        installationRepository.update(inst)

    return redirect('/settings/organisation')

@app.route('/api/github/installation', methods=['POST'])
def init_register_installation_id():
    installationRepository = Repository(GithubInstallation, g.session)
    inst = installationRepository.create(GithubInstallation(tenant_id=g.tenant.id, installation_token=str(uuid.uuid4())))

    return jsonify({
        "state": inst.installation_token
    })

@app.route('/api/github/installation', methods=['DELETE'])
def delete_installation_id():
    installationRepository = Repository(GithubInstallation, g.session)
    inst = installationRepository.create(GithubInstallation(tenant_id=g.tenant.id, installation_token=str(uuid.uuid4())))

    return jsonify({
        "state": inst.installation_token
    })

@app.route('/api/github/installation/import', methods=['POST'])
def import_installation():
    body = request.get_json()
    orgRepository = Repository(GithubOrg, g.session)
    org = orgRepository.find_one(GithubOrg.installation_id == body['installation_id'], GithubOrg.tenant_id == g.tenant.id)
    
    if org is None:
        return "", 404
    
    GithubImportService(g.session).create_import_request(org.tenant, org)

    return "", 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

    

    