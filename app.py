from flask import *
app = Flask(__name__)

# 메인페이지
@app.route('/')
def index():
    return render_template('home.html')

# 네이버 로그인 구현
@app.route('/auth/naver')
def naver_login():
    # 클라이언트 id , secret 추가
    client_id = ''
    redirect_uri = 'http://localhost:8000/callback/naver'
    url = f'https://nid.naver.com/oauth2.0/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code'
    return redirect(url)

# 네이버 로그인 리디렉션
@app.route('/callback/naver')
def naver_callback():
    params = request.args.to_dict()
    code = params.get('code')
    # 클라이언트 id , secret 추가
    client_id = ''
    client_secret = ''
    redirect_uri = 'http://localhost:8000/callback/naver'
    
    token_request = requests.get(f'https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}')
    token_json = token_request.json()
    print(token_json)
    
    access_token = token_json.get('access_token')
    profile_request = requests.get('https://openapi.naver.com/v1/nid/me', headers={'Authorization' : f'Bearer {access_token}'},)
    profile_data = profile_request.json()
    
    print(profile_data)
    return 'Login Success' # 메인페이지로 리디렉션 되도록 수정

# 카카오 로그인 구현
@app.route('/auth/kakao')
def method_name():
    pass

# 구글 로그인 구현
@app.route('/auth/google')
def method_name():
    pass

# 동영상 모자이크 페이지
@app.route('/video')
def method_name():
    pass

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 