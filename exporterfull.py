import pymssql
import time
from prometheus_client import start_http_server, Gauge, Info

def get_db_connection(server, user, password, port):
    """Establish a connection to the SQL Server."""
    return pymssql.connect(server=server, user=user, password=password, port=port)

def check_replica_status(server, user, password, port):
    """Check the status of SQL Server replicas."""
    with get_db_connection(server, user, password, port) as connection:
        cursor = connection.cursor(as_dict=True)
        cursor.execute("""
            SELECT ars.replica_id, ars.synchronization_health, 
                   ars.connected_state, ars.role, ar.replica_server_name 
            FROM sys.dm_hadr_availability_replica_states ars 
            JOIN sys.availability_replicas ar ON ars.replica_id = ar.replica_id
        """)

        replica_statuses = {}
        for row in cursor:
            replica_statuses[row['replica_id']] = {
                'replica_name': row['replica_server_name'],
                'synchronization_health': row['synchronization_health'],
                'connected_state': row['connected_state'],
                'role': row['role']
            }

    return replica_statuses

def check_db_status(server, user, password, port):
    """Check the status of SQL databases."""
    with get_db_connection(server, user, password, port) as connection:
        cursor = connection.cursor(as_dict=True)
        cursor.execute("SELECT name, state_desc, is_read_only FROM sys.databases")

        db_statuses = {}
        for row in cursor:
            db_statuses[row['name']] = {
                'state_desc': row['state_desc'],
                'is_read_only': row['is_read_only']
            }

    return db_statuses

def check_availability_group_status(server, user, password, port):
    """Check the status of SQL Server availability groups."""
    with get_db_connection(server, user, password, port) as connection:
        cursor = connection.cursor(as_dict=True)
        cursor.execute("""
            SELECT primary_recovery_health, primary_replica, primary_recovery_health_desc 
            FROM sys.dm_hadr_availability_group_states
        """)

        availability_group_status = {}
        for row in cursor:
            availability_group_status = {
                'primary_recovery_health': row['primary_recovery_health'],
                'primary_replica': row['primary_replica'],
                'primary_recovery_health_desc': row['primary_recovery_health_desc']
            }

    return availability_group_status

if __name__ == '__main__':
    server = 'servernameorIP'
    user = 'userlogin'
    password = 'userpassword'
    port = 1433

    start_http_server(8000)

    synchronization_health_gauge = Gauge('synchronization_health_status', 'Replica synchronization health status', ['replica'])
    connected_state_gauge = Gauge('connected_state_status', 'Replica connection state', ['replica'])
    role_gauge = Gauge('role_status', 'Replica role', ['replica'])
    state_desc_info = Info('state_desc_status', 'Database state description', ['database'])
    read_only_gauge = Gauge('read_only_status', 'Database read-only status', ['database'])
    
    recovery_health_gauge = Gauge('primary_recovery_health', 'Primary recovery health status', ['availability_group'])
    primary_replica_info = Info('primary_replica_info', 'Primary replica of the availability group', ['availability_group'])
    recovery_health_desc_info = Info('recovery_health_desc_info', 'Primary recovery health description', ['availability_group'])

    while True:
        try:
            replica_statuses = check_replica_status(server, user, password, port)
            for replica_id, status in replica_statuses.items():
                synchronization_health_gauge.labels(replica=status['replica_name']).set(status['synchronization_health'])
                connected_state_gauge.labels(replica=status['replica_name']).set(status['connected_state'])
                role_gauge.labels(replica=status['replica_name']).set(status['role'])

            db_statuses = check_db_status(server, user, password, port)
            for db_name, status in db_statuses.items():
                state_desc_info.labels(database=db_name).info({'state_desc': status['state_desc']})
                read_only_gauge.labels(database=db_name).set(int(status['is_read_only']))  # Convert boolean to int

            availability_group_status = check_availability_group_status(server, user, password, port)
            recovery_health_gauge.labels(availability_group='Default').set(availability_group_status['primary_recovery_health'])
            primary_replica_info.labels(availability_group='Default').info({'primary_replica': availability_group_status['primary_replica']})
            recovery_health_desc_info.labels(availability_group='Default').info({'primary_recovery_health_desc': availability_group_status['primary_recovery_health_desc']})

        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(60)
