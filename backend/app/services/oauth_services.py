#app/services/oauth_service.py
from app.utils.db import get_db_connection

class OAuthService:
    @staticmethod
    def save_user(user):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (id, name, email, picture, provider)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
                SET name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    picture = EXCLUDED.picture,
                    provider = EXCLUDED.provider
            """,
            (user["id"], user["name"], user["email"], user["picture"], user["provider"])
        )
        conn.commit()
        cur.close()
        conn.close()
