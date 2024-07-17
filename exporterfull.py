import pymssql
import time
from prometheus_client import start_http_server, Gauge

# Функция для проверки состояния is_read_only для каждой БД на сервере MSSQL
def check_database_status(server, user, password, port):
    connection = pymssql.connect(server=server, user=user, password=password, port=port)
    cursor = connection.cursor(as_dict=True)
    cursor.execute("SELECT name, is_read_only FROM sys.databases")
    
    db_statuses = {}
    for row in cursor:
        db_name = row['name']
        is_read_only = row['is_read_only']
        db_statuses[db_name] = 1 if is_read_only else 0

    connection.close()
    return db_statuses

if __name__ == '__main__':
    # Параметры подключения к MSSQL
    server = 'servername'
    user = 'userlogin'
    password = 'userpassword'
    port = 1433  # Порт MSSQL

    # Запуск HTTP сервера Prometheus на порту 8000
    start_http_server(8000)

    # Создание метрик для Prometheus
    db_read_only_status = Gauge('db_read_only_status', 'Database read-only status', ['database'])

    while True:
        database_statuses = check_database_status(server, user, password, port)
        for db_name, status in database_statuses.items():
            db_read_only_status.labels(database=db_name).set(status)
        time.sleep(20)
