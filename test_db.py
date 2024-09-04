import pymysql

# 获取数据库连接的函数
def get_connect():
    try:
        # 创建数据库连接
        connection = pymysql.connect(
            host='192.168.20.81',  # 数据库主机地址
            user='root',           # 数据库用户名
            password='HkLjYQt4J8C%',  # 数据库密码
            database='devops',     # 连接的数据库名
            charset='utf8mb4',     # 使用的字符集
            port=4306              # 数据库端口
        )
        return connection
    except Exception as e:
        # 如果连接失败，打印错误信息并抛出异常
        print(f"Failed to connect to database: {e}")
        raise

# 执行查询操作的函数
def select(sql, params=None):
    try:
        # 使用 with 语句确保连接关闭
        with get_connect() as connection:
            # 使用字典游标，查询结果将以字典形式返回
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 执行 SQL 查询
                cursor.execute(sql, params)
                # 获取所有查询结果
                result = cursor.fetchall()
                return result
    except Exception as e:
        # 如果查询失败，打印错误信息并抛出异常
        print(f"An error occurred during query execution: {e}")
        raise

# 执行更新操作的函数（包括更新和删除）
# def update(sql, params=None):
#     try:
#         # 使用 with 语句确保连接关闭
#         with get_connect() as connection:
#             with connection.cursor() as cursor:
#                 # 执行 SQL 更新
#                 cursor.execute(sql, params)
#                 # 提交事务
#                 connection.commit()
#                 # 返回受影响的行数
#                 return cursor.rowcount
#     except Exception as e:
#         # 如果更新失败，打印错误信息并回滚事务
#         print(f"An error occurred during update operation: {e}")
#         connection.rollback()
#         raise
def update(sql=None, params=None):
    """
    执行数据库更新操作的函数。

    参数:
    - sql (str): 要执行的 SQL 查询语句。
    - params (tuple): SQL 查询语句的参数，用于安全防止 SQL 注入。

    返回值:
    - int: 受影响的行数。

    异常处理:
    - 如果在执行过程中出现异常，会打印错误信息并回滚事务。
    """
    try:
        # 使用 with 语句管理数据库连接，确保在操作结束后自动关闭连接
        with get_connect() as connection:
            # 使用 with 语句管理游标，确保在操作结束后自动关闭游标
            with connection.cursor() as cursor:
                # 打印 SQL 语句和参数，帮助调试和确认 SQL 是否正确
                print(f"Executing SQL: {sql} with params: {params}")
                # 执行 SQL 语句，传入参数
                cursor.execute(sql, params)
                # 提交事务，确保更改保存到数据库
                connection.commit()
                # 返回受影响的行数，例如删除、更新的行数
                return cursor.rowcount
    except Exception as e:
        # 如果执行过程中出现异常，打印错误信息
        print(f"An error occurred during update operation: {e}")
        # 回滚事务，撤销未提交的更改，确保数据一致性
        connection.rollback()
        # 抛出异常，以便调用者处理
        raise

def execute_sql(sql=None, params=None):  
    try:  
        with get_connect() as connection:  
            with connection.cursor() as cursor:  
                print(f"Executing SQL: {sql} with params: {params}")  
                cursor.execute(sql, params)  
                connection.commit()  
                return cursor.rowcount  
    except Exception as e:  
        print(f"An error occurred during database operation: {e}")  
        if connection:  
            connection.rollback()  
        raise 

# 批量删除操作的函数
def batch_delete(ids):
    try:
        # 构建 SQL 语句
        ids_placeholder = ','.join(['%s'] * len(ids))
        sql = f'DELETE FROM deploy WHERE id IN ({ids_placeholder})'
        
        # 执行 SQL 语句
        rows_affected = update(sql, ids)
        
        return rows_affected
    except Exception as e:
        print(f"An error occurred during batch delete operation: {e}")
        raise

# 主程序用于测试各个数据库操作
if __name__ == '__main__':
    # 示例：查询所有服务器信息
    sql = "SELECT * FROM deploy"
    result = select(sql)
    print(result)

    # 示例：批量删除操作
    ids_to_delete = [1, 2, 3]  # 这里的 ID 需要根据实际情况提供
    deleted_count = batch_delete(ids_to_delete)
    print(f"Deleted {deleted_count} rows")
