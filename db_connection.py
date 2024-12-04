from flask import *
import pymysql
import datetime

class db_connection:
    def __init__(self):
        pass
    
		# DB 연결
		# Connection을 반환하는 메서드
		# 클래스메서드는 인스턴스 생성 없이 호출 가능: db_connection.get_db()
    @classmethod
    def get_db(self):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='qwer1234',
            db='mini2',
            charset='utf8',
            autocommit=True  # 테스트환경에서는 이렇게 사용
        )
# 클래스 수정해서 사용
        
if __name__ == '__main__':
    # 새로운 UserDao 테스트 코드
    user = UserDao().get_user('test_user@example.com', 'test_password') # 확인용
    if user:
        print(f"User found: {user}")
    else:
        print("User not found")
    
