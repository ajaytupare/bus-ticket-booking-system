from werkzeug.security import generate_password_hash, check_password_hash
from models.db import query_db

class UserModel:
    @staticmethod
    def create_user(name, email, phone, password, role='user'):
        hashed_password = generate_password_hash(password)
        query = "INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)"
        return query_db(query, (name, email.lower().strip(), phone, hashed_password, role), commit=True)

    @staticmethod
    def get_by_email(email):
        query = "SELECT * FROM users WHERE email = ?"
        return query_db(query, (email.lower().strip(),), one=True)

    @staticmethod
    def get_by_id(user_id):
        query = "SELECT id, name, email, phone, role, created_at FROM users WHERE id = ?"
        return query_db(query, (user_id,), one=True)

    @staticmethod
    def get_all():
        query = "SELECT id, name, email, phone, role, created_at FROM users ORDER BY created_at DESC"
        return query_db(query)

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

    @staticmethod
    def count_all():
        res = query_db("SELECT COUNT(*) as total FROM users WHERE role = 'user'", one=True)
        return res['total'] if res else 0
