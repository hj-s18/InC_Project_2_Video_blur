from flask import Flask, session, redirect, request, render_template, jsonify
import requests, os

app = Flask(__name__)
app.secret_key = "1234"  # Flask의 세션 암호화를 위한 키

# 카카오 API 설정
REST_API_KEY = "d37e3286aa4a1b7e3a2c084309f70d72"
REDIRECT_URI = "http://127.0.0.1:8000/kakaoLoginLogicRedirect"

# 업로드된 동영상 저장 경로
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # 현재 작업 디렉토리 기준으로 경로 설정
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 폴더가 없으면 생성
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Flask 앱 설정에 추가

# 동영상 업로드
@app.route('/videoUpload', methods=['GET'])
def videoUpload():
    return render_template('videoUpload.html')

# 동영상 업로드 처리
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file in the request'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 파일 저장
    try:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        video.save(video_path)
        return jsonify({'message': 'Video uploaded successfully', 'file_path': video_path}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 네이버 로그인
@app.route('/auth/naver')
def naver_login():
    client_id = 'IoxHlG8bqpaBGQ8xNrFZ'
    redirect_uri = 'http://127.0.0.1:8000/callback/naver'
    url = f'https://nid.naver.com/oauth2.0/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code'
    return redirect(url)

# 네이버 로그인 콜백
# @app.route('/callback/naver')
# def naver_callback():
#     code = request.args.get('code')
#     client_id = 'IoxHlG8bqpaBGQ8xNrFZ'
#     client_secret = '66WI_Bp8e3'
#     redirect_uri = 'http://127.0.0.1:8000/callback/naver'

#     # Access Token 요청
#     token_request = requests.get(
#         f'https://nid.naver.com/oauth2.0/token?grant_type=authorization_code'
#         f'&client_id={client_id}&client_secret={client_secret}&code={code}'
#     )
#     token_json = token_request.json()

#     if token_request.status_code != 200 or 'access_token' not in token_json:
#         error_description = token_json.get('error_description', 'Unknown error')
#         print(f"Token Request Error: {error_description}")
#         return f"Error: {error_description}", 400

#     # Access Token 저장
#     naver_access_token = token_json['access_token']
#     session['naver_access_token'] = naver_access_token  # 여기에 저장 추가

#     # 사용자 정보 요청
#     profile_request = requests.get(
#         'https://openapi.naver.com/v1/nid/me',
#         headers={'Authorization': f'Bearer {naver_access_token}'}
#     )
#     profile_data = profile_request.json()

#     if profile_data.get('message') != 'success':
#         return f"Error: {profile_data.get('message')}", 400

#     user_info = profile_data.get('response', {})
#     session['user'] = {
#         'id': user_info.get('id'),
#         'email': user_info.get('email'),
#         'name': user_info.get('name')
#     }
    
#     return redirect('/home')
@app.route('/callback/naver')
def naver_callback():
    code = request.args.get('code')
    client_id = 'IoxHlG8bqpaBGQ8xNrFZ'
    client_secret = '66WI_Bp8e3'
    redirect_uri = 'http://127.0.0.1:8000/callback/naver'

    # Access Token 요청
    token_request = requests.get(
        f'https://nid.naver.com/oauth2.0/token?grant_type=authorization_code'
        f'&client_id={client_id}&client_secret={client_secret}&code={code}'
    )
    token_json = token_request.json()

    if token_request.status_code != 200 or 'access_token' not in token_json:
        error_description = token_json.get('error_description', 'Unknown error')
        print(f"Token Request Error: {error_description}")
        return f"Error: {error_description}", 400

    # Access Token 저장
    naver_access_token = token_json['access_token']
    session['naver_access_token'] = naver_access_token  # 여기에 저장 추가

    # 사용자 정보 요청
    profile_request = requests.get(
        'https://openapi.naver.com/v1/nid/me',
        headers={'Authorization': f'Bearer {naver_access_token}'}
    )
    profile_data = profile_request.json()

    if profile_data.get('message') != 'success':
        return f"Error: {profile_data.get('message')}", 400

    user_info = profile_data.get('response', {})
    session['user'] = {
        'id': user_info.get('id'),
        'email': user_info.get('email'),
        'name': user_info.get('name')
    }
    
    return redirect('/home')


@app.route("/home", methods=["GET"])
def home():
    # 카카오 토큰 확인
    kakao_access_token = session.get("access_token")
    if kakao_access_token:
        headers = {"Authorization": f"Bearer {kakao_access_token}"}
        kakao_user_info = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers=headers
        ).json()
        return render_template("home.html", user_info=kakao_user_info)
    
    # 네이버 토큰 확인
    naver_access_token = session.get("naver_access_token")
    if naver_access_token:
        headers = {"Authorization": f"Bearer {naver_access_token}"}
        naver_user_info = requests.get(
            "https://openapi.naver.com/v1/nid/me", headers=headers
        ).json()
        return render_template("home.html", user_info=naver_user_info.get("response"))
    
    return redirect("/")  # 로그인이 안 된 상태라면 로그인 페이지로 리다이렉트


@app.route("/login", methods=["GET"])
def kakaologin():
    # access_token = session.get("access_token")

    # if access_token:
    #     account_info = requests.get(
    #         "https://kapi.kakao.com/v2/user/me",
    #         headers={"Authorization": f"Bearer {access_token}"}
    #     ).json()

    # return render_template("login.html")
    kakao_access_token = session.get("kakao_access_token")
    naver_access_token = session.get("naver_access_token")
    
    kakao_user_info = None
    naver_user_info = None

    # 카카오 사용자 정보 가져오기
    if kakao_access_token:
        kakao_user_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {kakao_access_token}"}
        ).json()
    
    # 네이버 사용자 정보 가져오기
    if naver_access_token:
        naver_user_info = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {naver_access_token}"}
        ).json()

    return render_template(
        "login.html",
        kakao_user_info=kakao_user_info,
        naver_user_info=naver_user_info,
    )


@app.route("/kakaoLoginLogic", methods=["GET"])
def kakaoLoginLogic():
    url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(url)

# 카카오 로그인 리다이렉트 처리
# 카카오 로그인 리다이렉트 처리
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
        
        # 카카오 사용자 정보 가져오기
        kakao_user_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        # 카카오 사용자 정보에 'properties'와 'kakao_account'가 존재하는지 확인
        if 'properties' in kakao_user_info and 'nickname' in kakao_user_info['properties']:
            nickname = kakao_user_info['properties']['nickname']
        else:
            nickname = "No nickname"

        email = kakao_user_info.get('kakao_account', {}).get('email', 'No email')
        
        # 사용자 정보를 세션에 저장
        session['user'] = {
            'id': kakao_user_info['id'],
            'name': nickname,
            'email': email
        }

        return redirect("/home")  # 로그인 성공 후 홈으로 리다이렉트
    else:
        print("Access token 발급 실패:", response.json())
        return "Access token 발급 실패.", 500


# @app.route("/kakaoLoginLogicRedirect", methods=["GET"])
# def kakaoLoginLogicRedirect():
#     code = request.args.get("code")
#     if not code:
#         print("Error: 인증 코드가 없습니다.")
#         return "카카오 로그인 인증 코드가 없습니다.", 400

#     token_url = "https://kauth.kakao.com/oauth/token"

#     response = requests.post(
#         token_url,
#         data={
#             "grant_type": "authorization_code",
#             "client_id": REST_API_KEY,
#             "redirect_uri": REDIRECT_URI,
#             "code": code,
#         },
#     )

#     access_token = response.json().get("access_token")
#     if access_token:
#         session["access_token"] = access_token
#         print("Access token 저장 성공:", access_token)
#         return redirect("/home")  # 로그인 성공 후 홈으로 리다이렉트
#     else:
#         print("Access token 발급 실패:", response.json())
#         return "Access token 발급 실패.", 500

@app.route('/logout')
def logout():
    session.clear()  # 세션 초기화
    return redirect('/')

@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 