import datetime
import os
from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
from auth import auth
from insert_db import insert_db
from servers import servers
from views import views

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mypwd'

# 设置session的不活跃有效期
app.permanent_session_lifetime = datetime.timedelta(minutes=1440)

# 注册蓝图
app.register_blueprint(servers, url_prefix='/servers')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(insert_db, url_prefix='/insertdb')
# app.register_blueprint(deploy, url_prefix='/deploy')
@app.route('/servers')
def servers():
    return render_template('/test/servers.html')
# 使用session方法
@app.before_request
def before_request():
    exempt_paths = [
        '/static/login.html',
        '/auth/login',
        '/static/css/*',
        '/static/js/*'
    ]
    
    path = request.path
    if any(path.startswith(p) for p in exempt_paths):
        pass
    elif 'username' not in session:
        return redirect(url_for('auth.login'))

if __name__ == '__main__':
    debug = False  # Set to False in production
    app.run(host='0.0.0.0', port=3113)