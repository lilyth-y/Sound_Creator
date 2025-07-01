# Sound_Creater: AI 한국어 대화 음성 합성기

## 프로젝트 소개

- **AI가 자동으로 자연스러운 2인 대화 스크립트를 생성**하고,
- **Google Cloud TTS(Chirp 계열)로 각 화자의 목소리를 합성**,
- **성별/연령/voice_id pool 기반으로 목소리 자동 분배**,
- **SSML 미지원 예외처리, pitch/speaking_rate 조정, mp3 병합** 등
- **웹 UI(프론트엔드)에서 손쉽게 대화 오디오를 생성/다운로드**할 수 있는 FastAPI 기반 시스템입니다.

---

## 주요 기능

- **태그/관계 기반 대화 스크립트 생성** (OpenAI GPT 등 LLM 활용)
- **화자별 성별/연령/성격/voice_id pool 자동 분배**
- **GCP Chirp 계열 TTS만 사용 (Standard/Natural/Wavenet 등 미사용)**
- **SSML 미지원 voice 예외처리 및 태그 자동 제거**
- **pitch/speaking_rate 조정(연령/성별별)** 및 ffmpeg로 사후 pitch 변환
- **mp3 병합/정규화/오디오 파일 반환**
- **프론트엔드 연동: 목소리 선택, 태그 입력, 오디오 다운로드 UI**

---

## 기술 스택

- **백엔드**: Python, FastAPI, Google Cloud TTS(Chirp)
- **프론트엔드**: HTML/CSS/JS (단순 UI, React/Vue 미사용)
- **오디오 처리**: ffmpeg, pydub
- **AI/LLM**: OpenAI GPT-4/3.5 (대화 스크립트 생성)

---

## 실행 방법

1. **Python 3.11 가상환경 생성 및 패키지 설치**
2. **GCP 서비스 계정 키, .env, GOOGLE_APPLICATION_CREDENTIALS 환경변수 설정**
3. **FastAPI 서버 실행**
4. **웹 브라우저에서 프론트엔드 접속 및 테스트**

---

## 주요 구조

- `main.py` : FastAPI 서버, API 엔드포인트, 오디오 병합 등
- `tts_engine.py` : GCP TTS 호출, pitch/speaking_rate 조정, SSML 예외처리
- `config.py` : voice_id pool, 성별/연령/톤 매핑 등
- `utils.py` : ffmpeg pitch 변환, 파일 병합 등
- `frontend/` : index.html, script.js, style.css (웹 UI)

---

## 참고/특이사항

- **Chirp 계열 voice_id별 성별/톤/연령 pool은 직접 청취 후 수동 매핑**
- **SSML, pitch 파라미터 미지원 voice 예외처리 자동화**
- **동일 화자=동일 목소리, 성별/연령 pool에서 중복 없이 분배**
- **실패/손상 mp3 자동 제외, 병합 시 예외처리 강화**

---

자세한 사용법/설정은 `how_to_use.md` 참고.
