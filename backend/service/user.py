from db.utils import execute_query, execute_query_one

class UserService:
    @staticmethod
    def login(username: str, password: str):
        query = 'SELECT id, username, role FROM users WHERE username = %s AND password = %s'
        return execute_query_one(query, (username, password))

    @staticmethod
    def get_users():
        query = 'SELECT id, username, email, role, status, create_time FROM users'
        users = execute_query(query)
        user_list = []
        for user in users:
            user_list.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3],
                'status': user[4],
                'createTime': str(user[5])
            })
        return user_list
