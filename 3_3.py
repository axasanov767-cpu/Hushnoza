# 1 - misol

class FakeConnection:
    def commit(self):
        print(" Malumotlar commit qilindi (conn.commit())")

conn = FakeConnection()

def commit(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        conn.commit()
        return result
    return wrapper

# 2 - misol

def permission_required(action):
    def decorator(func):
        def wrapper(user, *args, **kwargs):
            if user.get("role") == "admin":
                return func(user, *args, **kwargs)
            else:
                return f" Ruxsat yo`q! Siz {action} qilish huquqiga ega emassiz."
        return wrapper
    return decorator

@commit
@permission_required("post yaratish")
def create_post(user, title):
    print(f"{user['name']} '{title}' nomli post yaratdi.")
    return "Post muvaffaqiyatli yaratildi!"


@commit
@permission_required("post o`chirish")
def delete_post(user, post_id):
    print(f" {user['name']} {post_id}-IDli postni o`chirdi.")
    return "Post muvaffaqiyatli o`chirildi!"

if __name__ == "__main__":
    admin_user = {"name": "Hushnoza", "role": "admin"}
    normal_user = {"name": "Dilnoza", "role": "user"}

    print("\n--- ADMIN bilan test ---")
    print(create_post(admin_user, "Python darsi"))
    print(delete_post(admin_user, 1))

    print("\n--- Oddiy foydalanuvchi bilan test ---")
    print(create_post(normal_user, "Python darsi"))
    print(delete_post(normal_user, 1))
