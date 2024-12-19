import os
import uuid
import uvicorn
from app_auth import validate_token
from app_context import (
    context_session,
    context_trace_id,
    context_user,
    context_async_session,
)
from app_sql import setup_async_sql_engine, setup_sql_engine
import app_config
from controllers import (
    tenant_controller,
    repo_settings_controller,
    git_controller,
    github_installation_controller,
    github_integration_controller,
    stats_controller,
    teams_controller,
    users_controller,
)
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from db.model.metric import setup_tenant_metrics
from services.githubClient import setup_github_app
from contextlib import asynccontextmanager

# import tracemalloc
# import gc

app = FastAPI()
# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["*"]  # Allow all origins (use with caution in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Session = setup_sql_engine()
AsyncSession = setup_async_sql_engine()
setup_github_app()


def send_from_directory(directory, path):
    file_path = os.path.join(directory, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    return {"error": "File not found"}, 404


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSession() as session:
        await setup_tenant_metrics(session)
    yield


# @app.route('/assets/<path:path>')
@app.get("/assets/{path:path}")
def serve_assets(path: str):
    return send_from_directory("static/dist/assets", path)


@app.get("/thumbnails/{path:path}")
def serve_thumbnails(path):
    return send_from_directory("static/dist/thumbnails", path)


@app.get("/.well-known/{path:path}")
def serve_well_known(path):
    return send_from_directory("static/dist/.well-known", path)


@app.get("/public/{path:path}")
def serve_public(path):
    return send_from_directory("static/dist/", path)


@app.get("/health")
def health_check():
    return "Healthy", 200


def authorize_api_endpoints(request: Request):
    session = context_session.get()

    if request.url.path.startswith("/api/"):
        result, user = validate_token(session, request)
        if not result:
            raise HTTPException(status_code=401, detail="Invalid or missing token.")
        context_user.set(user)


@app.middleware("http")
async def request_middleware(request: Request, call_next):

    # snapshot1 = tracemalloc.take_snapshot()

    with Session() as session:
        async with AsyncSession() as asyncSession:
            context_session.set(session)
            context_async_session.set(asyncSession)
            trace_id = request.headers.get("x-ms-request-id") or str(uuid.uuid4().hex)
            context_trace_id.set(trace_id)
            authorize_api_endpoints(request)

            response = await call_next(request)
            context_session.set(None)
            context_async_session.set(None)
            return response

    # collected = gc.collect()
    # print(f"Garbage collector: collected {collected} objects.")
    # snapshot2 = tracemalloc.take_snapshot()
    # top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    # for stat in top_stats[:20]:
    #     print("\033[32m"+str(stat)+"\033[0m")


app.include_router(stats_controller.router, prefix="/api", tags=["Stats"])
app.include_router(users_controller.router, prefix="/api", tags=["Users"])
app.include_router(git_controller.router, prefix="/api", tags=["Git"])
app.include_router(teams_controller.router, prefix="/api", tags=["Teams"])
app.include_router(
    github_integration_controller.router, prefix="/github", tags=["GithubIntegration"]
)
app.include_router(tenant_controller.router, prefix="/api", tags=["Tenant"])
app.include_router(
    repo_settings_controller.router, prefix="/api", tags=["RepoSettings"]
)
app.include_router(
    github_installation_controller.router, prefix="/api", tags=["GithubInstallation"]
)


@app.get("/{path:path}")
def serve_react_app(path: str):
    if path.startswith("api"):
        return {"error": "API endpoint not found"}, 404

    return send_from_directory("static/dist", "index.html")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=app_config.HOT_RELOAD)
