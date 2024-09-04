import pandas as pd
import test_db

def load_servers_from_excel(file_path, engine='openpyxl'):
    # 使用 pandas 读取 Excel 文件
    df = pd.read_excel(file_path, engine=engine)
    servers = df.to_dict(orient='records')
    return servers

def insert_from_excel(excelPath):
    # 从 Excel 文件加载服务器信息
    servers = load_servers_from_excel(excelPath)
    
    # 遍历服务器信息并插入数据库
    for server in servers:
        sql = 'REPLACE INTO servers (name, ip, port, user) VALUES (%s, %s, %s, %s);'
        test_db.update(sql, (server['name'], server['ip'], server['port'], server['user']))

if __name__ == "__main__":
    insert_from_excel('/devops/servers/excel/servers.xlsx')