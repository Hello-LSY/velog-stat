#  velog-stat

## 📍 Demo Image

### 배포
https://velog-view.streamlit.app/

## 📍 사용방법

### 0. 사용하기 전에
> ⚠️ Access Token을 모르신다면 해당 기능을 사용하실 수 없습니다.

Velog Hits를 사용하기 위해서는 자신의 **velog Username(=ID)** 와 **Access Token**이 필요합니다.</br>
"조회수 통계"는 로그인 했을 때만 볼 수 있는 기능이기 때문에 Access Token이 필요합니다. Access Token을 통해 본인임을 인증할 수 있습니다.</br>

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
