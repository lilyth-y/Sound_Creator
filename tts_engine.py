"""
tts_engine.py
- GCP TTS, voice pool 관리, TTS 변환, fallback 등
"""
from typing import Dict
from google.cloud import texttospeech
from config import CHIRP_KO_VOICES
from utils import logger, ensure_dir
import re
import os

# Voice pool 자동화 예시 (실제는 mp3 테스트 등으로 동적 필터링 가능)
def get_valid_voice_pool() -> list:
    # TODO: mp3 테스트 기반 자동 필터링 구현 가능
    return CHIRP_KO_VOICES

# SSML 태그 제거
def strip_ssml(text: str) -> str:
    text = re.sub(r'<speak>|</speak>', '', text, flags=re.IGNORECASE)
    return re.sub(r'<.*?>', '', text).strip()

def get_tts_params(gender, age):
    pitch = 0.0
    rate = 1.0
    # 연령대별 조정
    if age:
        if '10' in age:
            pitch = 4.0
            rate = 1.18
        elif '20' in age:
            pitch = 2.0
            rate = 1.12
        elif '30' in age:
            pitch = 1.0
            rate = 1.05
        elif '40' in age:
            pitch = 0.0
            rate = 1.0
        elif '50' in age:
            pitch = -1.0
            rate = 0.96
        elif '60' in age or '70' in age or '80' in age or '노' in age:
            pitch = -2.0
            rate = 0.92
    # 성별별 조정
    if gender and '여' in gender:
        pitch += 1.0
    elif gender and '남' in gender:
        pitch -= 1.0
    return pitch, rate

# GCP TTS 변환
def synthesize_speech(text: str, voice_id: str, gender: str, age: str) -> bytes:
    """
    GCP TTS로 텍스트/SSML을 음성(mp3)으로 변환
    """
    logger.info(f"[TTS 요청] text={text!r}, voice_id={voice_id}, gender={gender}, age={age}")
    client = texttospeech.TextToSpeechClient()
    # SSML 자동 감지
    if text.strip().startswith("<speak>"):
        synthesis_input = texttospeech.SynthesisInput(ssml=text)
    else:
        synthesis_input = texttospeech.SynthesisInput(text=text)
    pitch, rate = get_tts_params(gender, age)
    voice = texttospeech.VoiceSelectionParams(language_code="ko-KR", name=voice_id)
    # Chirp 계열은 pitch 파라미터를 절대 전달하지 않음
    if "Chirp" in voice_id:
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=rate
        )
    else:
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=rate,
            pitch=pitch
        )
    try:
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        logger.info(f"[TTS 성공] voice_id={voice_id}, bytes={len(response.audio_content)}")
        return response.audio_content
    except Exception as e:
        logger.warning(f"[TTS 실패] {e}. SSML 미지원 등 예외처리 시도")
        # SSML 미지원 등 예외: SSML 태그 제거 후 재시도
        plain_text = strip_ssml(text)
        if not plain_text or len(plain_text) < 2:
            logger.warning(f"[TTS 폴백] SSML 제거 후 텍스트가 너무 짧음. 빈 음성 반환")
            return b''
        try:
            synthesis_input = texttospeech.SynthesisInput(text=plain_text)
            # pitch 없이 재시도
            if "Chirp" in voice_id:
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=rate
                )
            else:
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=rate,
                    pitch=pitch
                )
            response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            logger.info(f"[TTS 폴백 성공] voice_id={voice_id}, bytes={len(response.audio_content)}")
            return response.audio_content
        except Exception as e2:
            logger.error(f"[TTS 폴백도 실패] {e2}")
            return b'' 