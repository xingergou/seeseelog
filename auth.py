from flask import Blueprint, make_response, redirect, request, send_from_directory, session
import test_db
import tool_pass

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 处理登录逻辑
        username = request.form.get('username')
        password = request.form.get('password')
        password = tool_pass.md5(password)
        sql = 'SELECT * FROM user WHERE username = %s AND password = %s'
        result = test_db.select(sql, (username, password))
        
        # 添加调试输出
        print(f"Query Result: {result}")
        
        if result:
            session['username'] = username
            return redirect("/servers")
        else:
            # 显式返回一个重定向，即使登录失败也要返回一个有效的响应
            return redirect("/static/login.html")
    
    # GET 请求时返回登录页面
    return send_from_directory('static', 'login.html')