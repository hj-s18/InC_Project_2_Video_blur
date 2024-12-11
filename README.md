## InC_Project_2 
- 사용자가 업로드한 영상을 자동으로 모자이크 처리하는 웹 서비스
- Amazon Rekognition Video를 활용해 업로드된 영상에서 얼굴 객체를 감지하고, OpenCV 라이브러리를 통해 감지된 얼굴 영역을 모자이크 처리
- Jenkins CI/CD 파이프라인을 구축해 소스 코드 변경 시 자동으로 Docker 이미지를 빌드하고 AWS ECR에 푸시
- AWS ECS(Fargate)를 이용해 컨테이너 기반의 확장 가능한 서비스로 운영, 서비스 가용성과 안정성 확보
- AWS S3를 사용해 원본 및 모자이크 처리된 영상을 안전하게 저장하고, CloudFront로 빠르고 안전한 콘텐츠 전송 제공
- 서비스 상태 모니터링을 위해 AWS CloudWatch사용, Auto Scaling이 감지되면 Slack에 알림이 가도록 구현
- IAM 역할과 보안 그룹 설정을 통해 안전한 서비스 운영 환경 조성.
---
### 프로젝트 아키텍처
![project2 drawio (2)](https://github.com/user-attachments/assets/b6e784ee-07d3-4950-b9bf-9be615e1246d)
