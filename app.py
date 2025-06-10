from flask import Flask, jsonify
from flask_cors import CORS
from config import config
import os
from utils.extensions import db, jwt


def create_app(config_name=None):
    app = Flask(__name__)

    # 配置应用
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # 注册蓝图
    from modules.auth.routes import auth_bp
    from modules.user_management.routes import user_mgmt_bp
    from modules.data_management.routes import data_mgmt_bp
    from modules.audit.routes import audit_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_mgmt_bp, url_prefix='/api/users')
    app.register_blueprint(data_mgmt_bp, url_prefix='/api/data_management')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Invalid token'}), 401

    # 健康检查
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Medical System API is running'})

    return app


if __name__ == '__main__':
    app = create_app()

    # 运行应用
    app.run(
        host=app.config['APP_HOST'],
        port=app.config['APP_PORT'],
        debug=app.config['DEBUG']
    )