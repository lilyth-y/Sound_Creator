# type: ignore는 외부 라이브러리 미설치 시 linter 경고 방지용
from pydub import AudioSegment  # type: ignore
import os

# ElevenLabs TTS 모듈
from tts_elevenlabs import synthesize_speech_elevenlabs as tts

# ---------- 설정 ----------
# Google Cloud 서비스 계정 JSON 키 경로가 환경변수 GOOGLE_APPLICATION_CREDENTIALS 에
# 이미 설정되어 있다고 가정합니다.

# 화자별 음성 ID (ElevenLabs 한국어 남성/여성 예시)
# 실제 사용 시 ElevenLabs 대시보드에서 원하는 Voice ID로 교체하세요.
FATHER_VOICE_ID = "Yko7PKHZNXotIFUBG7I9"   # 예: 중후한 남성
DAUGHTER_VOICE_ID = "XrExE9yKIg1WjnnlVkGX" # 예: 밝은 여성

# 대화 스크립트 (일상 대화 예시)
CONVERSATION_LINES = [
    ("father", "혜린아, 학교 다녀왔니?"),
    ("daughter", "다녀왔어요, 아빠! 오늘 학교에서 과학 실험을 했어요."),
    ("father", "오, 재미있었겠다! 무슨 실험을 했는데?"),
    ("daughter", "전구에 전기를 연결해서 불을 켜 봤어요. 친구들이랑 신기해했어요."),
    ("father", "그랬구나. 배고프지? 간식 먹자."),
    ("daughter", "좋아요! 고마워요, 아빠.")
]

OUTPUT_DIR = "output_wav"
FINAL_FILENAME = "father_daughter_dialogue.wav"
SILENCE_MS = 800  # 문장 사이 정적 (ms)

# ---------- 유틸 ----------

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# ---------- TTS ----------

# ElevenLabs TTS 호출 래퍼 (tts_elevenlabs.py 참조)

def synthesize(text: str, voice_id: str) -> bytes:
    """ElevenLabs TTS 로 텍스트를 WAV bytes 로 변환"""
    return tts(text=text, voice_id=voice_id)

# ---------- 메인 로직 ----------

def main():
    ensure_dir(OUTPUT_DIR)
    segments = []
    silence = AudioSegment.silent(duration=SILENCE_MS)

    for idx, (speaker, text) in enumerate(CONVERSATION_LINES):
        voice_id = FATHER_VOICE_ID if speaker == "father" else DAUGHTER_VOICE_ID
        wav_bytes = synthesize(text, voice_id)
        line_path = os.path.join(OUTPUT_DIR, f"line_{idx}.wav")
        with open(line_path, "wb") as f:
            f.write(wav_bytes)
        # pydub 로 Segment 로드
        segment = AudioSegment.from_file(line_path, format="wav")
        segments.append(segment)
        print(f"[TTS] Saved {line_path} ({len(wav_bytes)} bytes)")

    # 병합
    combined = AudioSegment.empty()
    for seg in segments:
        combined += seg + silence

    final_path = os.path.join(OUTPUT_DIR, FINAL_FILENAME)
    combined.export(final_path, format="wav")
    print(f"[완료] 최종 WAV 저장: {final_path} (길이: {combined.duration_seconds:.1f}s)")

if __name__ == "__main__":
    main()