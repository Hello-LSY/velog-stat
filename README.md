#  velog-stat

![image](https://github.com/user-attachments/assets/6d015a06-976f-47d9-84d3-dd2b98837aa4)

### 배포
https://velog-stat.streamlit.app/

## 📍 사용방법

### 0. 사용하기 전에
> ⚠️ Access Token정보가 필요합니다.

조회수 통계는 로그인 했을 때만 볼 수 있는 기능이기 때문에 Access Token이 필요합니다.</br>

> 💡 Access Token 확인하는 방법

1. 자신의 velog 접속 및 로그인
2. F12 - Application - Storage - Cookies - https://velog.io - access_token 확인

### 1. 로컬 사용법

#### 프로젝트 클론
```
git clone https://github.com/Hello-LSY/velog-stat.git
cd velog-stat
```

#### 가상환경 생성 및 활성화
```
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

#### 패키지 설치
```
pip install -r requirements.txt
```

#### 실행
```
streamlit run velog_stat\app.py
```
