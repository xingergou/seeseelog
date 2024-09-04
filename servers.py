import os
import subprocess
import threading
import time
from flask import Blueprint, json, jsonify, request, send_from_directory
import pymysql
import test_db
import traceback

servers = Blueprint('servers', __name__)

@servers.route('/index')
def index():
    return 'Servers'

@servers.route('/get_by_page', methods=['GET', 'POST'])
def get_by_page():
    info = request.get_data()
    info = json.loads(info)
    pagenow = info['pagenow']
    pagesize = info['pagesize']
    search = info['search']
    # SQL 查询，使用参数化查询防止 SQL 注入
    sql = 'SELECT * FROM deploy WHERE name LIKE %s LIMIT %s, %s'
    params = (f"%{search}%", (pagenow - 1) * pagesize, pagesize)  # 修正参数数量
    # 执行查询并返回结果
    result = test_db.select(sql, params=params)
    return json.dumps(result)


@servers.route('/get_by_id')
def get_by_id():
    id = int(request.args.get('id'))
    sql = "SELECT * FROM deploy WHERE id=%s"
    result = test_db.select(sql, params=(id,))
    return json.dumps(result)

def shellRun(command):
    (status, output) = subprocess.getstatusoutput(command)
    return (status, output)


@servers.route('/update', methods=['GET', 'POST'])
def update():
    info = request.get_data()
    info = json.loads(info)
    sql = 'REPLACE INTO deploy(id,name,hosts_path, hosts_pattern, module, args, forks) VALUES(%s, %s, %s, %s, %s, %s, %s)'
    params = (info['id'], info['name'], info['hosts_path'], info['hosts_pattern'], info['module'], info['args'], info['forks'])
    test_db.update(sql, params=params)
    return 'ok'

@servers.route('/deploy_by_id', methods=['GET', 'POST'])
def deploy_by_id():
    id = int(request.args.get('id'))
    sql = "SELECT * FROM deploy WHERE id=%s"
    result = test_db.select(sql, params=(id,))[0]
    tmpnumber = int(time.time() * 1000)
    # name, hosts_path, hosts_pattern, module, args, forks
    runcommand = """ /usr/local/python3.8/bin/ansible -i {0} {1} -m {2} -a '{3}' -f {4} """.format(
        result['hosts_path'],
        result['hosts_pattern'],
        result['module'],
        result['args'],
        result['forks']
    )
    command = """  /usr/local/python3.8/bin/ansible -i {0} {1} -m {2} -a '{3}' -f {4} >static/logs/{5} 2>&1; printf '\n\t\t\t' >>static/logs/{6} """.format(
        result['hosts_path'],
        result['hosts_pattern'],
        result['module'],
        result['args'],
        result['forks'], tmpnumber, tmpnumber
    )    
    t1 = threading.Thread(target=shellRun, args=(command,))
    t1.start()
    return json.dumps({"command": runcommand, "logpath": tmpnumber})

@servers.route('/static/logs/<path:filename>', methods=['GET'])
def serve_log(filename):
    # 设置 Content-Type 为 text/plain，并确保以 UTF-8 编码发送
    return send_from_directory(directory='static/logs', filename=filename, as_attachment=False, mimetype='text/plain')

@servers.route('/delete', methods=['GET', 'POST'])
def delete_server():
    # 从 GET 参数或 POST 请求体中获取 server_id
    server_id = request.args.get('id') if request.method == 'GET' else request.json.get('id')
    
    # 验证 server_id 是否存在并且类型正确
    if server_id is None:
        return jsonify({"status": "error", "message": "缺少 ID 参数"}), 400
    
    try:
        server_id = int(server_id)
    except ValueError:
        return jsonify({"status": "error", "message": "ID 必须是一个整数"}), 400
    
    # 构造 SQL 语句和参数
    sql = "DELETE FROM deploy WHERE id = %s"
    params = (server_id,)
    print(f"Executing SQL: {sql} with params: {params}")

    # 执行数据库删除操作
    try:
        # 检查是否存在该 ID
        check_sql = "SELECT * FROM deploy WHERE id = %s"
        existing_record = test_db.execute_sql(check_sql, params)
        print(f"Existing record check result: {existing_record}")

        if not existing_record:
            return jsonify({"status": "error", "message": "ID 在数据库中不存在"}), 404

        # 删除操作
        affected_rows = test_db.execute_sql(sql, params)
        print(f"AFFECTED ROWS: {affected_rows}")
        
        if affected_rows > 0:
            return jsonify({"status": "success"}), 200
        else:
            # 检查事务是否已提交
            print("Check if the transaction is committed, or if there are any constraints.")
            return jsonify({"status": "error", "message": "没有行受影响"}), 404
    except Exception as e:
        print(f"删除操作过程中发生错误: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# 批量删除配置
@servers.route('/batch_delete', methods=['POST'])
def batch_delete_servers():
    try:
        # 解析 JSON 数据
        data = request.get_json()
        if data is None:
            print("Error: Request body is not valid JSON or empty")
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        
        # 获取 IDs 列表
        ids = data.get('ids', [])
        
        # 验证 ids 是否为列表且不为空
        if not isinstance(ids, list) or not ids:
            print(f"Error: Invalid or missing 'ids' field. Received: {ids}")
            return jsonify({'error': 'No IDs provided or IDs must be a list'}), 400

        # 尝试将字符串转换为整数
        try:
            ids = [int(id) for id in ids]
        except ValueError as ve:
            print(f"Error: All IDs must be integers. Received: {ids}")
            return jsonify({'error': 'All IDs must be integers'}), 400

        # 打印要删除的 IDs
        print(f"IDs to delete: {ids}")

        # 执行批量删除操作
        try:
            sql = "DELETE FROM deploy WHERE id IN %s"
            params = (tuple(ids),)
            print(f"Executing batch delete SQL: {sql} with params: {params}")

            # 执行 SQL 语句并提交事务
            rows_affected = test_db.execute_sql(sql, params)
            print(f"{rows_affected} rows deleted")

            # 提交事务

            return jsonify({'message': f'{rows_affected} rows deleted'}), 200
        except Exception as db_error:
            # 回滚事务
            print(f"Database error during batch delete: {db_error}")
            return jsonify({'error': 'Failed to delete records'}), 500

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An error occurred during batch delete'}), 500



