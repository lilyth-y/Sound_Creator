"""
tts_elevenlabs.py
ElevenLabs TTS helper module: converts text to WAV (bytes).
"""
# type: ignore는 외부 라이브러리 미설치 시 linter 경고 방지 용도
from elevenlabs import generate, set_api_key  # type: ignore
import os
from typing import Optional

# Load API key from environment
ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise EnvironmentError(
        "ELEVENLABS_API_KEY 환경변수가 설정되어 있지 않습니다. "
        "https://elevenlabs.io/dashboard 에서 발급받은 키를 .env 또는 셸 환경변수에 설정해주세요."
    )

# Configure SDK
set_api_key(ELEVENLABS_API_KEY)


def synthesize_speech_elevenlabs(
    text: str,
    voice_id: str,
    *,
    model: str = "eleven_multilingual_v2",
    stability: float = 0.3,
    similarity_boost: float = 0.85,
    style: float = 0.4,
    speaker_boost: bool = True,
) -> bytes:
    """Generate speech using ElevenLabs.

    Args:
        text: The text to be converted into speech.
        voice_id: Voice ID provided by ElevenLabs.
        model: TTS model to use (default: "eleven_multilingual_v2").
        stability, similarity_boost, style, speaker_boost: Optional voice parameters.

    Returns:
        WAV (PCM 44.1 kHz, 16-bit) audio bytes.
    """
    return generate(
        voice_id=voice_id,
        text=text,
        model=model,
        stability=stability,
        similarity_boost=similarity_boost,
        style=style,
        speaker_boost=speaker_boost,
    )