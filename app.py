from flask import Flask, render_template, request, jsonify, redirect, send_from_directory, send_file, render_template_string
import jwt
import os
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = "{{secret}}"

with open("templates/index.html", "r", encoding="utf-8") as f:
    prts_template = f.read()
    os.remove("templates/index.html")

# 签名 JWT
def generate_jwt(sub):
    payload = {
        'sub': sub,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    # 使用正确的encode方法
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# JWT 验证装饰器
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect('/login')
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'], options={'verify_aud': False})
        except jwt.ExpiredSignatureError:
            response = redirect('/login')
            response.set_cookie('token', '', expires=0)
            return response
        except jwt.InvalidTokenError:
            response = redirect('/login')
            response.set_cookie('token', '', expires=0)
            return response
        return f(*args, **kwargs)
    return decorated_function

# 登录页面
@app.route('/login')
def login_handler():
    return render_template('login.html')

# PRTS 页面（需要JWT鉴权）
@app.route('/prts')
@jwt_required
def prts_handler():
    user = request.cookies.get("user")
    payload = jwt.decode(request.cookies.get("token"), app.config['SECRET_KEY'], algorithms=['HS256'], options={'verify_aud': False})
    username = payload.get("sub")
    if not username:
        return redirect('/login')
    return render_template_string(prts_template, user=user, username=username)

@app.errorhandler(404)
def page_not_found(e):
    return redirect('/login')

# 登录处理
@app.route('/api/login', methods=['POST'])
def login_api_handler():
    username = request.json.get('username')
    password = request.json.get('password')
    if username == 'VFTS352' and password == '48399110':
        token = generate_jwt(sub="doctor")
        response = redirect('/prts')
        response.set_cookie('token', token, httponly=True, samesite='Strict')
        response.set_cookie('user', 'doctor', httponly=True, samesite='Strict')
        return response
    else:
        return {'status': 'error', 'message': '用户名或密码错误'}, 401

# 静态文件处理
@app.route('/static/<path:path>')
def static_handler(path):
    return send_from_directory('static', path)

@app.route("/api/get_avatar")
def avatar_handler():
    file = request.args.get('username')
    return send_file("static/img/" + file)

if __name__ == "__main__":
    with open("/flag", "r") as f:
        flag = f.read()
    os.remove("/flag")
    prts_template.replace("<<flag>>", flag)
    app.run("0.0.0.0", 5000)