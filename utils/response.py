# utils/response.py
from flask import jsonify
from typing import Any, Optional, Union

'''
请求统一返回接口格式为：
  code: number | string;
  result: T;
  message: string;
  status: string | number;
'''


class ResponseHandler:
    """统一响应处理器"""

    # 成功状态码
    SUCCESS = 200
    # 错误状态码
    ERROR = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

    @staticmethod
    def success(result: Any = None, message: str = "操作成功", code: Union[int, str] = SUCCESS):
        """成功响应"""
        return jsonify({
            "code": code,
            "result": result,
            "message": message,
            "status": "ok"
        }), 200

    @staticmethod
    def error(message: str = "操作失败", code: Union[int, str] = ERROR, result: Any = None):
        """错误响应"""
        return jsonify({
            "code": code,
            "result": result,
            "message": message,
            "status": "error"
        }), code if isinstance(code, int) and 400 <= code <= 599 else 400

    @staticmethod
    def unauthorized(message: str = "未授权访问", result: Any = None):
        """未授权响应"""
        return jsonify({
            "code": 401,
            "result": result,
            "message": message,
            "status": "error"
        }), 401

    @staticmethod
    def forbidden(message: str = "权限不足", result: Any = None):
        """禁止访问响应"""
        return jsonify({
            "code": 403,
            "result": result,
            "message": message,
            "status": "error"
        }), 403

    @staticmethod
    def not_found(message: str = "资源不存在", result: Any = None):
        """资源不存在响应"""
        return jsonify({
            "code": 404,
            "result": result,
            "message": message,
            "status": "error"
        }), 404

    @staticmethod
    def server_error(message: str = "服务器内部错误", result: Any = None):
        """服务器错误响应"""
        return jsonify({
            "code": 500,
            "result": result,
            "message": message,
            "status": "error"
        }), 500


# 为了方便使用，提供简化的函数
def success_response(result: Any = None, message: str = "操作成功", code: Union[int, str] = 200):
    """成功响应的简化函数"""
    return ResponseHandler.success(result, message, code)


def error_response(message: str = "操作失败", code: Union[int, str] = 400, result: Any = None):
    """错误响应的简化函数"""
    return ResponseHandler.error(message, code, result)


def unauthorized_response(message: str = "未授权访问", result: Any = None):
    """未授权响应的简化函数"""
    return ResponseHandler.unauthorized(message, result)


def forbidden_response(message: str = "权限不足", result: Any = None):
    """禁止访问响应的简化函数"""
    return ResponseHandler.forbidden(message, result)


def not_found_response(message: str = "资源不存在", result: Any = None):
    """资源不存在响应的简化函数"""
    return ResponseHandler.not_found(message, result)


def server_error_response(message: str = "服务器内部错误", result: Any = None):
    """服务器错误响应的简化函数"""
    return ResponseHandler.server_error(message, result)