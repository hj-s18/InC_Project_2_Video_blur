from flask import Flask, session, redirect, request, render_template, jsonify
import requests

app = Flask(__name__)
app.secret_key = "1234"  # Flask의 세션 암호화를 위한 키

# 카카오 API 설정
REST_API_KEY = "d37e3286aa4a1b7e3a2c084309f70d72"
REDIRECT_URI = "http://127.0.0.1:8000/kakaoLoginLogicRedirect"

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

@app.route("/home", methods=["GET"])
def home():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/")  # 로그인이 안 된 상태라면 로그인 페이지로 리다이렉트

    # 카카오 사용자 정보 가져오기
    account_info = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    # 사용자 정보를 출력하거나 HTML 템플릿으로 전달
    print("카카오 사용자 정보:", account_info)
    return render_template("home.html", user_info=account_info)

@app.route("/login", methods=["GET"])
def kakaologin():
    access_token = session.get("access_token")

    if access_token:
        account_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

    return render_template("login.html")


@app.route("/kakaoLoginLogic", methods=["GET"])
def kakaoLoginLogic():
    url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(url)


@app.route("/kakaoLoginLogicRedirect", methods=["GET"])
def kakaoLoginLogicRedirect():
    code = request.args.get("code")
    if not code:
        print("Error: 인증 코드가 없습니다.")
        return "카카오 로그인 인증 코드가 없습니다.", 400

    token_url = "https://kauth.kakao.com/oauth/token"

    response = requests.post(
        token_url,
        data={
            "grant_type": "authorization_code",
            "client_id": REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
    )

    access_token = response.json().get("access_token")
    if access_token:
        session["access_token"] = access_token
        print("Access token 저장 성공:", access_token)
        return redirect("/home")  # 로그인 성공 후 홈으로 리다이렉트
    else:
        print("Access token 발급 실패:", response.json())
        return "Access token 발급 실패.", 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 