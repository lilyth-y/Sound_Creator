"""
main.py
- FastAPI 엔드포인트, 전체 orchestrator
"""
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dialogue_generator import generate_dialogue, parse_dialogue
from tts_engine import synthesize_speech, get_valid_voice_pool
from utils import logger, ensure_dir, merge_mp3_files, get_mp3_files_sorted, change_pitch_ffmpeg
from config import OUTPUT_DIR, CHIRP_KO_VOICES, CHIRP_KO_VOICE_GENDER
from fastapi.staticfiles import StaticFiles
import random

app = FastAPI()

class SpeakerProfile(BaseModel):
    gender: str
    age: str
    personality: str
    voice_id: Optional[str] = None
    tts_engine: Optional[str] = None

class GenerationRequest(BaseModel):
    speaker_a: SpeakerProfile
    speaker_b: SpeakerProfile
    relationship: str
    tags: List[str]
    date: Optional[str] = None
    duration_seconds: Optional[int] = 30

@app.post("/api/generate-audio/", response_class=FileResponse)
async def generate_audio_endpoint(request: GenerationRequest = Body(...)):
    # 1. 대화 스크립트 생성
    script = generate_dialogue(
        request.speaker_a.dict(),
        request.speaker_b.dict(),
        request.tags, 
        request.relationship, 
        duration_seconds=request.duration_seconds or 30
    )
    logger.info(f"[스크립트 생성 완료]\n{script}")

    # 2. 대사 파싱
    dialogue_lines = parse_dialogue(script)
    logger.info(f"[대사 파싱] {len(dialogue_lines)}개 라인")

    # 3. 음성 합성 및 파일 저장
    date = request.date or "today"
    output_dir = os.path.join(OUTPUT_DIR, date)
    ensure_dir(output_dir)
    audio_files = []
    # 화자별 voice_id 고정 (중복 불가)
    a_profile = request.speaker_a.dict()
    b_profile = request.speaker_b.dict()
    a_gender = a_profile.get("gender")
    b_gender = b_profile.get("gender")
    a_voice_id = a_profile.get("voice_id")
    b_voice_id = b_profile.get("voice_id")
    used_voice_ids = set()
    if not a_voice_id or "Chirp" not in a_voice_id:
        a_voice_id = select_chirp_voice(a_gender, used_voice_ids)
    used_voice_ids.add(a_voice_id)
    if not b_voice_id or "Chirp" not in b_voice_id or b_voice_id == a_voice_id:
        b_voice_id = select_chirp_voice(b_gender, used_voice_ids)
    used_voice_ids.add(b_voice_id)
    for idx, (speaker, text) in enumerate(dialogue_lines):
        if speaker == "A":
            profile = a_profile
            voice_id = a_voice_id
        else:
            profile = b_profile
            voice_id = b_voice_id
        # 성별 자동 판별: profile에 없으면 voice_id 기반
        gender = profile.get("gender")
        if not gender or gender.strip() == '' or gender == '자동':
            gender = CHIRP_KO_VOICE_GENDER.get(voice_id, '알수없음')
        age = profile.get("age")
        audio_bytes = synthesize_speech(text, voice_id, gender, age)
        file_path = os.path.join(output_dir, f"dialogue_{idx}.mp3")
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        n_semitones, speaking_rate = get_pitch_and_rate(gender, age)
        # pitch 변환
        if n_semitones != 0:
            pitch_path = os.path.join(output_dir, f"dialogue_{idx}_pitch.mp3")
            change_pitch_ffmpeg(file_path, pitch_path, n_semitones)
            if os.path.exists(pitch_path) and os.path.getsize(pitch_path) > 1000:
                audio_files.append(pitch_path)
            else:
                logger.error(f"[피치 변환 파일 없음/손상] {pitch_path} → 원본으로 대체")
                if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
                    audio_files.append(file_path)
                else:
                    logger.error(f"[TTS 파일 없음/손상] {file_path} → 병합 제외")
        else:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
                audio_files.append(file_path)
            else:
                logger.error(f"[TTS 파일 없음/손상] {file_path} → 병합 제외")
        logger.info(f"[음성 합성] {audio_files[-1] if audio_files else '생성 실패'}")

    # 4. mp3 병합 및 최종 파일 반환
    if not audio_files:
        raise HTTPException(status_code=500, detail="음성 파일 생성 실패")
    final_path = os.path.join(output_dir, "final_dialogue.mp3")
    merge_mp3_files(audio_files, final_path)
    logger.info(f"[최종 병합 파일] {final_path}")
    return FileResponse(path=final_path, media_type='audio/mpeg', filename=os.path.basename(final_path))

@app.get("/api/audio-files/")
def list_audio_files(date: Optional[str] = None):
    """
    프론트엔드에서 개별 mp3/최종 mp3 모두 접근 가능하도록 파일 리스트 반환
    """
    date = date or "today"
    output_dir = os.path.join(OUTPUT_DIR, date)
    files = get_mp3_files_sorted(output_dir)
    return JSONResponse({"files": [os.path.basename(f) for f in files]})

@app.get("/api/voices")
def get_voices():
    """
    GCP Chirp 계열의 voice_id와 사람이 읽기 쉬운 label 리스트 반환
    """
    def make_label(voice_id):
        # 예시: voice_id에서 이름 추출 및 임의 분류(실제 성별/연령/톤 정보는 없으므로 샘플)
        name = voice_id.replace('ko-KR-Chirp3-HD-', '')
        # 간단 샘플: 이름 끝 알파벳이 A~M이면 여성/20대, N~Z면 남성/30대
        last = name[0].upper()
        if last < 'N':
            gender = '여성'
            age = '20대'
            tone = '밝은'
        else:
            gender = '남성'
            age = '30대'
            tone = '차분한'
        return f"{name} ({gender}/{age}/{tone})"
    voices = [
        {"id": vid, "label": make_label(vid)} for vid in CHIRP_KO_VOICES
    ]
    return JSONResponse({"voices": voices})

def select_chirp_voice(gender, used_voice_ids=None):
    pool = [v for v in CHIRP_KO_VOICES if CHIRP_KO_VOICE_GENDER.get(v) == gender]
    if used_voice_ids:
        pool = [v for v in pool if v not in used_voice_ids]
    if not pool:
        pool = [v for v in CHIRP_KO_VOICES if v not in (used_voice_ids or [])]  # fallback
    return random.choice(pool)

def get_pitch_and_rate(gender, age):
    pitch = 0
    rate = 1.0
    if not age:
        return pitch, rate
    if '60' in age or '70' in age or '80' in age or '노' in age:
        if gender and '여' in gender:
            pitch = 0
            rate = 0.78
        elif gender and '남' in gender:
            pitch = 0
            rate = 1.1
        else:
            pitch = 0
            rate = 1.0
    elif '50' in age:
        pitch = -1
        rate = 0.95
    elif '10' in age:
        pitch = 2
        rate = 1.12
    elif '20' in age:
        pitch = 1
        rate = 1.05
    return pitch, rate

# --- 정적 파일 서빙 (프론트엔드) ---
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)