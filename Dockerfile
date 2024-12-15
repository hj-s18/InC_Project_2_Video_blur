# 베이스 이미지 설정
FROM python:3.9-slim
# python:3.9-slim 이미지를 사용하여 컨테이너 생성
# python:3.9-slim : python3.9를 포함한 가벼운 Linux 기반 Docker 이미지


# 작업 디렉토리 설정
WORKDIR /app
# 컨테이너 내부에서 작업이 수행될 기본 디렉토리를 /app으로 설정
# 이후 명령어들은 모두 이 디렉토리 기준으로 실행됨
# /app 디렉토리는 컨테이너 안에서 자동으로 생성됨


# 파일 복사
COPY requirements.txt .
# 호스트 머신에 있는 requirements.txt 파일을 컨테이너 내부의 현재 작업 디렉토리 (.=/app) 로 복사
# requirements.txt : Python 프로젝트의 의존 패키지 리스트가 정의되어있음


# 의존성 설치
RUN pip install --upgrade pip && pip install -r requirements.txt
# pip install --upgrade pip : Python의 패키지 관리 도구 pip을 최신 버전으로 업그레이드함
# pip install -r requirements.txt : requirements.txt에 나열된 Python 의존성 패키지를 모두 설치함


# 전체 프로젝트 복사
COPY . .
# 호스트 머신의 현재 디렉토리(.) 에 있는 모든 파일을 컨테이너의 현재 작업 디렉토리 (/app)로 복사
# => 프로젝트 코드 전체가 컨테이너에 포함됨


# 컨테이너가 실행될 때 사용할 명령어 정의
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
# gunicorn : Python WSGI HTTP 서버로, Flask나 Django 같은 웹 애플리케이션을 실행하는데 사용됨
# -w 2 : worker 프로세스 수를 2개로 설정 (worker : 동시에 처리할 수 있는 요청의 개수)
# -b 0.0.0.0:8000 : gunicorn이 0.0.0.0:8000 에서 요청을 수신하도록 설정
# app:app : Flask 애플리케이션의 실행 지점을 지정
  # 첫번째 app : Python 파일(app.py) 이름
  # 두번째 app : app.py 안에서 정의된 Flask 애플리케이션 객체
