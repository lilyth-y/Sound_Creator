"""
config.py
- 환경설정, 상수, voice pool 등 공통 설정 관리
"""

import os

# GCP TTS 관련 환경변수
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "serviceAccountKey.json")

# Voice pool (초기값, 실제는 자동화/동적 로딩)
CHIRP_KO_VOICES = [
    'ko-KR-Chirp3-HD-Achernar', 'ko-KR-Chirp3-HD-Achird', 'ko-KR-Chirp3-HD-Algenib',
    'ko-KR-Chirp3-HD-Algieba', 'ko-KR-Chirp3-HD-Alnilam', 'ko-KR-Chirp3-HD-Aoede',
    'ko-KR-Chirp3-HD-Autonoe', 'ko-KR-Chirp3-HD-Callirrhoe', 'ko-KR-Chirp3-HD-Charon',
    'ko-KR-Chirp3-HD-Despina', 'ko-KR-Chirp3-HD-Enceladus', 'ko-KR-Chirp3-HD-Erinome',
    'ko-KR-Chirp3-HD-Fenrir', 'ko-KR-Chirp3-HD-Gacrux', 'ko-KR-Chirp3-HD-Iapetus',
    'ko-KR-Chirp3-HD-Kore', 'ko-KR-Chirp3-HD-Laomedeia', 'ko-KR-Chirp3-HD-Leda',
    'ko-KR-Chirp3-HD-Orus', 'ko-KR-Chirp3-HD-Puck', 'ko-KR-Chirp3-HD-Pulcherrima',
    'ko-KR-Chirp3-HD-Rasalgethi', 'ko-KR-Chirp3-HD-Sadachbia', 'ko-KR-Chirp3-HD-Sadaltager',
    'ko-KR-Chirp3-HD-Schedar', 'ko-KR-Chirp3-HD-Sulafat', 'ko-KR-Chirp3-HD-Umbriel',
    'ko-KR-Chirp3-HD-Vindemiatrix', 'ko-KR-Chirp3-HD-Zephyr', 'ko-KR-Chirp3-HD-Zubenelgenubi',
]

# voice_id별 성별 정보 (Chirp 계열만, 표 기준으로 정확히 반영)
CHIRP_KO_VOICE_GENDER = {
    'ko-KR-Chirp3-HD-Aoede': '여성',
    'ko-KR-Chirp3-HD-Charon': '남성',
    'ko-KR-Chirp3-HD-Fenrir': '남성',
    'ko-KR-Chirp3-HD-Kore': '여성',
    'ko-KR-Chirp3-HD-Leda': '여성',
    'ko-KR-Chirp3-HD-Orus': '남성',
    'ko-KR-Chirp3-HD-Puck': '남성',
    'ko-KR-Chirp3-HD-Zephyr': '여성',
    'ko-KR-Chirp3-HD-Achernar': '여성',
    'ko-KR-Chirp3-HD-Achird': '남성',
    'ko-KR-Chirp3-HD-Algenib': '남성',
    'ko-KR-Chirp3-HD-Algieba': '남성',
    'ko-KR-Chirp3-HD-Alnilam': '남성',
    'ko-KR-Chirp3-HD-Autonoe': '여성',
    'ko-KR-Chirp3-HD-Callirrhoe': '여성',
    'ko-KR-Chirp3-HD-Despina': '여성',
    'ko-KR-Chirp3-HD-Enceladus': '남성',
    'ko-KR-Chirp3-HD-Erinome': '여성',
    'ko-KR-Chirp3-HD-Gacrux': '여성',
    'ko-KR-Chirp3-HD-Iapetus': '남성',
    'ko-KR-Chirp3-HD-Laomedeia': '여성',
    'ko-KR-Chirp3-HD-Pulcherrima': '여성',
    'ko-KR-Chirp3-HD-Rasalgethi': '남성',
    'ko-KR-Chirp3-HD-Sadachbia': '남성',
    'ko-KR-Chirp3-HD-Sadaltager': '남성',
    'ko-KR-Chirp3-HD-Schedar': '남성',
    'ko-KR-Chirp3-HD-Sulafat': '여성',
    'ko-KR-Chirp3-HD-Umbriel': '남성',
    'ko-KR-Chirp3-HD-Vindemiatrix': '여성',
    'ko-KR-Chirp3-HD-Zubenelgenubi': '남성',
}

# 기타 상수
OUTPUT_DIR = "output" 