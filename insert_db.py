from flask import Blueprint, request, jsonify
import pymysql
import traceback

# 创建蓝图
insert_db = Blueprint('insertdb', __name__)

# 数据库连接函数
def get_connect():
    """获取数据库连接"""
    # 根据实际情况填写数据库连接参数
    connection = pymysql.connect(
        host='192.168.20.81',  # 数据库主机地址
        user='root',           # 数据库用户名
        password='HkLjYQt4J8C%',  # 数据库密码
        database='devops',     # 连接的数据库名
        charset='utf8mb4',     # 使用的字符集
        port=4306              # 数据库端口
    )
    return connection

# 执行插入操作的函数
def insert(sql, params=None):
    """
    执行SQL插入操作。
    
    :param sql: SQL 插入语句
    :param params: SQL 参数（可选）
    :return: 最后插入行的ID
    """
    try:
        # 使用 with 语句确保连接关闭
        with get_connect() as connection:
            with connection.cursor() as cursor:
                # 执行 SQL 插入
                cursor.execute(sql, params)
                # 提交事务
                connection.commit()
                # 返回最后插入行的 ID
                return cursor.lastrowid
    except pymysql.err.DataError as e:
        # 如果发生数据错误，打印错误信息
        print(f"Data error during insert operation: {e}")
        raise
    except Exception as e:
        # 如果插入失败（非数据错误），打印错误信息
        print(f"An error occurred during insert operation: {e}")
        raise

# 插入函数
@insert_db.route('/add', methods=['POST'])
def add():
    try:
        # 获取请求数据并解析为JSON
        info = request.get_json()
        if not info:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # 构建 SQL 插入语句
        sql_insert = "INSERT INTO deploy (name, hosts_path, hosts_pattern, module, args, forks) VALUES (%s, %s, %s, %s, %s, %s)"
        
        # 构建参数元组
        insert_params = (
            info.get('name'),
            info.get('hosts_path'),
            info.get('hosts_pattern'),
            info.get('module'),
            info.get('args'),
            info.get('forks')
        )
        
        # 调用 insert 函数执行插入操作
        insert_result = insert(sql_insert, params=insert_params)
        
        # 返回成功响应
        return jsonify({'message': f'Record added successfully, Inserted row ID: {insert_result}'}), 201
    
    except pymysql.err.DataError as e:
        # 如果发生数据错误，返回错误信息
        return jsonify({"error": f"DataError occurred: {str(e)}"}), 400
    
    except Exception as e:
        # 打印完整的错误堆栈信息
        print("Error occurred in add function:")
        print(traceback.format_exc())
        # 捕获并返回错误信息
        return jsonify({"error": str(e)}), 500