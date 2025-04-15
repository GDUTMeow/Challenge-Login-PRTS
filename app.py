from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    send_from_directory,
    send_file,
    render_template_string,
)
import jwt
import os
import datetime
import urllib.request
from urllib.error import URLError
import socket
import re
from io import BytesIO
from functools import wraps
import pycurl
from urllib.parse import quote

app = Flask(__name__)
app.config["SECRET_KEY"] = "{{secret}}"

with open("templates/index.html", "r", encoding="utf-8") as f:
    prts_template = f.read()
    os.remove("templates/index.html")


def generate_jwt(sub):
    payload = {
        "sub": sub,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
    return token


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect("/login")
        try:
            jwt.decode(
                token,
                app.config["SECRET_KEY"],
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError:
            response = redirect("/login")
            response.set_cookie("token", "", expires=0)
            return response
        except jwt.InvalidTokenError:
            response = redirect("/login")
            response.set_cookie("token", "", expires=0)
            return response
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login")
def login_handler():
    return render_template("login.html")


@app.route("/prts")
@jwt_required
def prts_handler():
    user = request.cookies.get("user")
    payload = jwt.decode(
        request.cookies.get("token"),
        app.config["SECRET_KEY"],
        algorithms=["HS256"],
        options={"verify_aud": False},
    )
    username = payload.get("sub")
    if not username:
        return redirect("/login")
    return render_template_string(prts_template, user=user, username=username)


@app.errorhandler(404)
def page_not_found(e):
    return redirect("/login")


@app.route("/api/login", methods=["POST"])
def login_api_handler():
    username = request.json.get("username")
    password = request.json.get("password")
    if username == "VFTS352" and password == "48399110":
        token = generate_jwt(sub="doctor")
        response = redirect("/prts")
        response.set_cookie("token", token, httponly=True, samesite="Strict")
        response.set_cookie("user", "doctor", httponly=True, samesite="Strict")
        return response
    else:
        return {"status": "error", "message": "用户名或密码错误"}, 401


@app.route("/static/<path:path>")
def static_handler(path):
    return send_from_directory("static", path)


@app.route("/api/get_avatar")
def avatar_handler():
    file = request.args.get("filename")
    return send_file("static/img/" + file)


@app.route("/api/get_resource", methods=["POST"])
def resource_handler():
    try:
        data = request.get_json()
        target_url = data.get("url")

        # 移除所有协议和端口限制
        parsed = urllib.parse.urlparse(target_url)
        buffer = BytesIO()
        c = pycurl.Curl()

        if parsed.scheme == "file":
            # 因为改用 CentOS 后 curl 的版本太低了没有 PATH_AS_IS 选项，所以这里进行手动处理
            try:
                with open(parsed.path, "rb") as f:
                    content = f.read()
                return jsonify(
                    {
                        "code": 200,
                        "success": True,
                        "data": {"url": target_url, "content": content.decode("utf-8")},
                    }
                )
            except Exception as e:
                return jsonify(
                    {
                        "code": 500,
                        "success": False,
                        "data": {"url": target_url, "content": str(e)},
                    }
                )
            
        buffer = BytesIO()
        c = pycurl.Curl()

        # 全协议支持配置
        c.setopt(pycurl.URL, target_url.encode("utf-8"))
        c.setopt(pycurl.WRITEDATA, buffer)
        c.setopt(pycurl.PROTOCOLS, pycurl.PROTO_ALL)  # 允许所有协议
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(pycurl.TIMEOUT, 120)
        c.setopt(pycurl.FOLLOWLOCATION, 1)  # 允许重定向
        c.setopt(pycurl.MAXREDIRS, 5)

        # 执行请求
        c.perform()

        # 获取原始响应
        content = buffer.getvalue().decode("utf-8", errors="replace")
        status_code = c.getinfo(pycurl.RESPONSE_CODE)

        # 统一响应格式
        return jsonify(
            {
                "code": status_code,
                "success": 200 <= status_code < 400 or status_code == 0,
                "data": {"url": target_url, "content": content},
            }
        )

    except pycurl.error as e:
        return jsonify(
            {
                "code": 500,
                "success": False,
                "data": {"url": target_url, "content": f"CURL Error: {e.args[1]}"},
            }
        )

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "success": False,
                "data": {"url": target_url, "content": str(e)},
            }
        )

    finally:
        if "c" in locals():
            c.close()
        buffer.close()


if __name__ == "__main__":
    with open("/flag", "r") as f:
        flag = f.read()
    os.remove("/flag")
    # flag = "{{flag}}"
    prts_template.replace("<<flag>>", flag)
    app.run("0.0.0.0", 5000)
