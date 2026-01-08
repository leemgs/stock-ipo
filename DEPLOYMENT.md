# 배포 가이드 (Deployment Guide)

## Ubuntu 서버에 systemd 서비스로 배포하기

이 가이드는 Ubuntu 서버에서 공모주 IPO 분석 웹 애플리케이션을 systemd 서비스로 설정하여 부팅 시 자동으로 시작되도록 하는 방법을 설명합니다.

### 1. 애플리케이션 설치

```bash
# 애플리케이션을 /opt/stock-ipo 디렉토리에 설치
sudo mkdir -p /opt/stock-ipo
sudo chown $USER:$USER /opt/stock-ipo

# 저장소 클론
cd /opt
git clone https://github.com/leemgs/stock-ipo.git
cd stock-ipo

# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. systemd 서비스 파일 설정

```bash
# 서비스 파일을 systemd 디렉토리로 복사
sudo cp stock-ipo.service /etc/systemd/system/

# 서비스 파일 권한 설정
sudo chmod 644 /etc/systemd/system/stock-ipo.service
```

### 3. 사용자 및 권한 설정

기본 설정에서는 `www-data` 사용자로 실행됩니다. 다른 사용자로 실행하려면:

```bash
# 서비스 파일 수정
sudo nano /etc/systemd/system/stock-ipo.service

# User와 Group을 원하는 사용자로 변경
# 예: User=myuser, Group=myuser
```

애플리케이션 파일 소유권 설정:

```bash
# www-data 사용자로 실행하는 경우
sudo chown -R www-data:www-data /opt/stock-ipo

# 또는 특정 사용자로 실행하는 경우
sudo chown -R myuser:myuser /opt/stock-ipo
```

### 4. 서비스 활성화 및 시작

```bash
# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable stock-ipo.service

# 서비스 시작
sudo systemctl start stock-ipo.service

# 서비스 상태 확인
sudo systemctl status stock-ipo.service
```

### 5. 서비스 관리 명령어

```bash
# 서비스 중지
sudo systemctl stop stock-ipo.service

# 서비스 재시작
sudo systemctl restart stock-ipo.service

# 서비스 상태 확인
sudo systemctl status stock-ipo.service

# 로그 확인
sudo journalctl -u stock-ipo.service -f

# 최근 로그 100줄 보기
sudo journalctl -u stock-ipo.service -n 100
```

### 6. 방화벽 설정

포트 5701을 열어야 외부에서 접근할 수 있습니다:

```bash
# UFW 방화벽 사용 시
sudo ufw allow 5701/tcp

# firewalld 사용 시
sudo firewall-cmd --permanent --add-port=5701/tcp
sudo firewall-cmd --reload
```

### 7. 웹 애플리케이션 접속

서비스가 실행되면 다음 주소로 접속할 수 있습니다:

```
http://서버IP주소:5701
```

로컬에서 테스트:
```
http://localhost:5701
```

### 8. 문제 해결

#### 서비스가 시작되지 않는 경우

```bash
# 상세 로그 확인
sudo journalctl -u stock-ipo.service -xe

# Python 경로 확인
which python3

# 가상환경 경로 확인
ls -la /opt/stock-ipo/venv/bin/python3
```

#### 권한 문제

```bash
# 파일 권한 확인
ls -la /opt/stock-ipo/

# 실행 권한 부여
chmod +x /opt/stock-ipo/web_app.py
```

#### 포트 충돌

포트 5701이 이미 사용 중인지 확인:

```bash
sudo netstat -tulpn | grep 5701
# 또는
sudo ss -tulpn | grep 5701
```

### 9. 프로덕션 환경 권장사항

개발 서버 대신 Gunicorn을 사용하는 것을 권장합니다:

```bash
# Gunicorn 설치
source /opt/stock-ipo/venv/bin/activate
pip install gunicorn

# 서비스 파일 수정
sudo nano /etc/systemd/system/stock-ipo.service
```

서비스 파일의 ExecStart 부분을 다음과 같이 변경:

```ini
ExecStart=/opt/stock-ipo/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5701 web_app:app
```

그런 다음 서비스 재시작:

```bash
sudo systemctl daemon-reload
sudo systemctl restart stock-ipo.service
```

### 10. Nginx 리버스 프록시 설정 (선택사항)

Nginx를 프록시로 사용하여 더 나은 성능과 보안을 얻을 수 있습니다:

```bash
# Nginx 설치
sudo apt install nginx

# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/stock-ipo
```

설정 내용:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5701;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

설정 활성화:

```bash
sudo ln -s /etc/nginx/sites-available/stock-ipo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 서비스 파일 설명

`stock-ipo.service` 파일의 주요 설정:

- **Type=simple**: 간단한 프로세스 타입
- **User/Group**: 실행 사용자 (보안을 위해 www-data 사용)
- **WorkingDirectory**: 애플리케이션 디렉토리
- **Environment**: 환경 변수 설정
- **ExecStart**: 실행 명령
- **Restart=always**: 실패 시 자동 재시작
- **RestartSec=10**: 재시작 대기 시간 (10초)
- **PrivateTmp=true**: 임시 디렉토리 격리 (보안)
- **NoNewPrivileges=true**: 권한 상승 방지 (보안)

## 보안 참고사항

1. 운영 환경에서는 `FLASK_DEBUG=False`로 설정하세요
2. 방화벽을 설정하여 필요한 포트만 개방하세요
3. 정기적으로 시스템과 의존성을 업데이트하세요
4. HTTPS를 사용하려면 SSL 인증서를 설정하세요 (Let's Encrypt 등)
