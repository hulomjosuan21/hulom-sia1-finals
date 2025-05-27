from src.auth import auth_bp
from src.routes.user_routes import user_bp
from src.routes.assignment_routes import assignment_bp
from src.agent import agent_dp

def register_routes(app):
    app.register_blueprint(auth_bp,url_prefix="/api/auth")
    app.register_blueprint(user_bp,url_prefix="/api/user")
    app.register_blueprint(assignment_bp,url_prefix="/api/assignment")
    app.register_blueprint(agent_dp,url_prefix="/api/agent")
    print(app.url_map)