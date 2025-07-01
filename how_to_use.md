# Sound Creator 사용법

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 및 설정](#설치-및-설정)
3. [서버 실행](#서버-실행)
4. [사용법](#사용법)
5. [API 엔드포인트](#api-엔드포인트)
6. [문제 해결](#문제-해결)

## 🖥 시스템 요구사항

### 필수 소프트웨어
- **Python 3.11** (3.12 이하 권장 - pydub 호환성 문제)
- **FFmpeg** (오디오 처리용)
- **Git** (선택사항)

### API 키 설정
- **OpenAI API Key** (GPT-4 대화 생성용)
- **Google Cloud Platform API Key** (TTS 음성 합성용)
- **ElevenLabs API Key** (선택사항 - 고품질 TTS용)

##  설치 및 설정

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd Sound_Creater
```

### 2. 가상환경 생성 및 활성화

#### Windows (PowerShell)
```powershell
# 기존 가상환경 삭제 (있다면)
Remove-Item -Recurse -Force .\venv_py311

# Python 3.11로 새 가상환경 생성
python -m venv venv_py311

# 가상환경 활성화
.\venv_py311\Scripts\Activate.ps1
```

#### macOS/Linux
```bash
# 기존 가상환경 삭제 (있다면)
rm -rf venv_py311

# Python 3.11로 새 가상환경 생성
python3.11 -m venv venv_py311

# 가상환경 활성화
source venv_py311/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
# OpenAI API Key (필수)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google Cloud Platform (필수)
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json

# ElevenLabs API Key (선택사항)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

### 5. FFmpeg 설치

#### Windows
```powershell
# winget 사용 (권장)
winget install Gyan.FFmpeg

# 또는 수동 설치 후 PATH에 추가
```

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

##  서버 실행

### 개발 모드로 실행
```bash
# 가상환경이 활성화된 상태에서
uvicorn main:app --reload
```

### 프로덕션 모드로 실행
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 접속
브라우저에서 `http://127.0.0.1:8000` 또는 `http://localhost:8000` 접속

## 📖 사용법

### 웹 인터페이스 사용

1. **브라우저에서 접속**: `http://localhost:8000`
2. **화자 설정**:
   - 화자 A, B의 성별, 나이, 성격 입력
   - 목소리 선택 (자동 선택 옵션 사용 가능)
3. **대화 설정**:
   - 화자 간 관계 입력
   - 대화 상황 태그 선택
   - 대화 길이 설정 (선택사항)
4. **생성**: "음성 생성" 버튼 클릭
5. **다운로드**: 생성된 MP3 파일 다운로드

### API 직접 사용

#### 단일 대화 생성
```bash
curl -X POST "http://localhost:8000/api/generate-audio/" \
  -H "Content-Type: application/json" \
  -d '{
    "speaker_a": {
      "gender": "남성",
      "age": "30대",
      "personality": "활발하고 긍정적인 성격",
      "voice_id": "ko-KR-Standard-B"
    },
    "speaker_b": {
      "gender": "여성", 
      "age": "30대",
      "personality": "신중하고 현실적인 성격",
      "voice_id": "ko-KR-Wavenet-A"
    },
    "relationship": "10년지기 친구",
    "tags": ["#퇴사선언", "#세계여행", "#친구와의 대화"],
    "duration_seconds": 60
  }'
```

#### 배치 생성 (여러 날짜)
```bash
curl -X POST "http://localhost:8000/api/generate-audio-batch/" \
  -H "Content-Type: application/json" \
  -d '{
    "dates": ["2025-01-01", "2025-01-02", "2025-01-03"],
    "speaker_a": { ... },
    "speaker_b": { ... },
    "relationship": "친구",
    "tags": ["일상대화"]
  }'
```

##  API 엔드포인트

### 주요 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 웹 인터페이스 |
| `/api/generate-audio/` | POST | 단일 대화 음성 생성 |
| `/api/generate-audio-batch/` | POST | 배치 대화 음성 생성 |
| `/api/voices` | GET | 사용 가능한 목소리 목록 |
| `/api/elevenlabs-voices` | GET | ElevenLabs 목소리 목록 |
| `/api/generate-dialogue` | POST | 대화 스크립트만 생성 |
| `/api/tts` | POST | 기본 TTS |
| `/api/tts-advanced` | POST | 고급 TTS |
| `/api/tts-elevenlabs` | POST | ElevenLabs TTS |

### 사용 가능한 목소리

#### GCP TTS 목소리
- `ko-KR-Standard-A` ~ `ko-KR-Standard-D`
- `ko-KR-Wavenet-A` ~ `ko-KR-Wavenet-D` 
- `ko-KR-Neural2-A` ~ `ko-KR-Neural2-C`

#### ElevenLabs 목소리 (선택사항)
- 한국어 지원 노인/중년/젊은 화자 목소리

## 🛠 문제 해결

### 일반적인 오류

#### 1. `ModuleNotFoundError: No module named 'pyaudioop'`
**원인**: Python 3.13에서 audioop 모듈이 제거됨
**해결**: Python 3.11 또는 3.12 사용

#### 2. `FFmpeg not found`
**원인**: FFmpeg가 설치되지 않았거나 PATH에 없음
**해결**: FFmpeg 설치 후 시스템 재시작

#### 3. `OPENAI_API_KEY not found`
**원인**: 환경변수가 설정되지 않음
**해결**: `.env` 파일에 API 키 추가

#### 4. `GOOGLE_APPLICATION_CREDENTIALS not found`
**원인**: Google Cloud 인증 파일 경로가 잘못됨
**해결**: 올바른 JSON 인증 파일 경로 설정

### 디버깅 팁

1. **로그 확인**: 터미널에서 오류 메시지 확인
2. **가상환경 확인**: `(venv_py311)` 프롬프트 확인
3. **Python 버전 확인**: `python --version`
4. **패키지 설치 확인**: `pip list`

### 성능 최적화

1. **GPU 사용**: CUDA 지원 환경에서 더 빠른 처리
2. **메모리 관리**: 대용량 배치 처리 시 메모리 모니터링
3. **캐싱**: 동일한 요청에 대한 결과 캐싱

##  프로젝트 구조

```
Sound_Creater/
├── main.py                 # 메인 서버 파일
├── requirements.txt        # Python 의존성
├── .env                   # 환경변수 (생성 필요)
├── frontend/              # 웹 인터페이스
│   ├── index.html
│   ├── script.js
│   └── style.css
├── output/                # 생성된 음성 파일
│   └── YYYY-MM-DD/
└── venv_py311/           # 가상환경
```

##  지원

문제가 발생하면 다음을 확인해주세요:
1. Python 버전이 3.11인지 확인
2. 모든 의존성이 설치되었는지 확인
3. API 키가 올바르게 설정되었는지 확인
4. FFmpeg가 설치되어 있는지 확인

추가 도움이 필요하면 이슈를 등록해주세요. 
