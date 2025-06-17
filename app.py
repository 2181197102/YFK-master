from flask import Flask
from flask_cors import CORS
from config import config
import os
from utils.extensions import db, jwt
from utils.response import (
    success_response,
    error_response,
    unauthorized_response,
    not_found_response,
    server_error_response
)
from datetime import datetime
import pytz


def create_app(config_name=None):
    app = Flask(__name__)

    print("当前本地时间:", datetime.now())
    print("当前 UTC 时间:", datetime.utcnow())
    print("当前北京时间:", datetime.now(pytz.timezone("Asia/Shanghai")))

    # 配置应用
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # 注册蓝图
    from modules.auth.routes import auth_bp
    from modules.user_management.routes import user_mgmt_bp
    from modules.data_management.routes import data_mgmt_bp
    from modules.audit.routes import audit_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_mgmt_bp, url_prefix='/api/users')
    app.register_blueprint(data_mgmt_bp, url_prefix='/api/data_management')
    app.register_blueprint(audit_bp, url_prefix='/api/audit')

    # 统一错误处理
    @app.errorhandler(400)
    def bad_request(error):
        return error_response("请求参数错误", 400)

    @app.errorhandler(401)
    def unauthorized(error):
        return unauthorized_response("未授权访问")

    @app.errorhandler(403)
    def forbidden(error):
        return error_response("权限不足", 403)

    @app.errorhandler(404)
    def not_found(error):
        return not_found_response("请求的资源不存在")

    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response("请求方法不被允许", 405)

    @app.errorhandler(500)
    def internal_error(error):
        return server_error_response("服务器内部错误")

    # 处理其他异常
    @app.errorhandler(Exception)
    def handle_exception(error):
        # 如果是HTTP异常，使用其状态码
        if hasattr(error, 'code'):
            if error.code == 400:
                return error_response("请求参数错误", 400)
            elif error.code == 401:
                return unauthorized_response("未授权访问")
            elif error.code == 403:
                return error_response("权限不足", 403)
            elif error.code == 404:
                return not_found_response("请求的资源不存在")
            elif error.code == 405:
                return error_response("请求方法不被允许", 405)
            else:
                return error_response(str(error), error.code)
        else:
            # 对于其他异常，返回500错误
            return server_error_response("服务器内部错误")

    # JWT 统一错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return unauthorized_response("Token已过期，请重新登录")

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return unauthorized_response("无效的Token")

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return unauthorized_response("缺少Token，请先登录")

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return unauthorized_response("Token需要刷新")

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return unauthorized_response("Token已被撤销")

    # 健康检查 - 使用统一响应格式
    @app.route('/health')
    def health_check():
        return success_response(
            result={'timestamp': datetime.now().isoformat()},
            message='Medical System API is running'
        )

    # 添加全局异常捕获中间件
    @app.before_request
    def before_request():
        # 这里可以添加请求前的统一处理逻辑
        pass

    @app.after_request
    def after_request(response):
        # 这里可以添加响应后的统一处理逻辑
        # 例如添加统一的响应头
        response.headers['X-API-Version'] = '1.0'
        return response

    return app


if __name__ == '__main__':
    app = create_app()

    # 运行应用
    app.run(
        host=app.config['APP_HOST'],
        port=app.config['APP_PORT'],
        debug=app.config['DEBUG']
    )