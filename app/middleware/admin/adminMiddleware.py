from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def adminRequired(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        claims = get_jwt()
        vaiTro = claims.get("vaiTro")

        if vaiTro != "ADMIN":
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Bạn không có quyền truy cập chức năng Admin",
                    }
                ),
                403,
            )

        return func(*args, **kwargs)

    return wrapper
