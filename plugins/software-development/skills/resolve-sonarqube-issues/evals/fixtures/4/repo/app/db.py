"""Thin query helper around the app's database connection."""


def find_user_by_name(conn, username):
    query = "SELECT id, name, email FROM users WHERE name = '" + username + "'"
    cursor = conn.execute(query)
    return cursor.fetchone()
