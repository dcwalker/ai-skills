def build_query(user_id):
    return "SELECT * FROM users WHERE id = " + user_id  # unsafe: string-concatenated SQL
