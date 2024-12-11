from flask import Flask, session, redirect, request, render_template, jsonify, send_file
from io import BytesIO
import requests, os, boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

app = Flask(__name__)
app.secret_key = "1234"  # Flask의 세션 암호화를 위한 키

# 카카오 API 설정
REST_API_KEY = "d37e3286aa4a1b7e3a2c084309f70d72"
REDIRECT_URI = "http://<alb DNS 이름>/kakaoLoginLogicRedirect"

# AWS S3 설정
S3_BUCKET = '<S3 upload-bucket 이름'
S3_OUTPUT = '<S3 download-bucket 이름>'
S3_ACCESS_KEY = '<ACCESS-KEY>'
S3_SECRET_KEY = '<SECRET_KEY>'
REGION_NAME = '<REGION_NAME>'

# S3 연결 함수
def s3_connection():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=REGION_NAME
        )
        # 연결 확인 (버킷 목록 조회)
        response = s3_client.list_buckets()
        print("S3 연결 성공! 버킷 목록:")
        for bucket in response['Buckets']:
            print(f"  - {bucket['Name']}")
        return s3_client
    except NoCredentialsError:
        print("AWS 자격 증명 실패")
    except PartialCredentialsError:
        print("AWS 자격 증명 실패")
    except Exception as e:
        print(f"S3 연결 실패: {e}")
    return None

# S3 클라이언트 초기화
s3_client = s3_connection()
if not s3_client:
    raise RuntimeError("S3 클라이언트 초기화 실패")

# 동영상 업로드 페이지
@app.route('/videoUpload', methods=['GET'])
def videoUpload():
    return render_template('videoUpload.html')

# 동영상 업로드 처리
@app.route('/upload', methods=['POST'])
def upload_video():
    
    access_token = session.get("access_token", None)

    if access_token:
        account_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        kakao_id = account_info.get("id")
        
    # 업로드 파일 확인
    if 'video' not in request.files:
        return jsonify({'error': 'No video file in the request'}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # S3에 파일 업로드
        video_key = f"{kakao_id}/{video.filename}"  # S3 내 파일 경로 설정
        s3_client.upload_fileobj(video, S3_BUCKET, video_key)

        # 업로드 성공 응답
        s3_url = f"https://{S3_BUCKET}.s3.{REGION_NAME}.amazonaws.com/{video_key}"
        return jsonify({'message': 'Video uploaded successfully', 'file_path': s3_url}), 200

    except Exception as e:
        # 예외 처리
        return jsonify({'error': str(e)}), 500

# 파일 목록 조회 및 다운로드 페이지
@app.route('/files', methods=['GET'])
def list_files():
    access_token = session.get("access_token", None)

    if access_token:
        account_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        kakao_id = account_info.get("id")

    try:
        # 사용자 ID 폴더에 있는 파일 목록 가져오기
        prefix = f"{kakao_id}/"  # 사용자 폴더 경로
        response = s3_client.list_objects_v2(Bucket=S3_OUTPUT, Prefix=prefix)

        # 파일 목록 생성
        files = []
        for obj in response.get('Contents', []):
            files.append(obj['Key'].replace(prefix, ''))  # 파일명만 저장

        return render_template('files.html', files=files, user_id=kakao_id)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 파일 다운로드 처리
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    access_token = session.get("access_token", None)

    if access_token:
        account_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        kakao_id = account_info.get("id")

    object_key = f"{kakao_id}/{filename}"  # 사용자 ID 기반 파일 경로

    try:
        # S3에서 파일 다운로드
        file_obj = BytesIO()
        s3_client.download_fileobj(S3_OUTPUT, object_key, file_obj)
        file_obj.seek(0)  # 스트림의 시작 위치로 이동

        # 클라이언트에게 파일 전송
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=filename,  # 다운로드 파일 이름
            mimetype='application/octet-stream'
        )
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
    app.run(host='0.0.0.0', port=8000)
 
