"""
utils.py
- 공통 유틸리티 함수 (로깅, 파일관리, 오디오 병합/후처리 등)
"""
import os
import logging
from datetime import datetime
from pydub import AudioSegment, effects
import subprocess

def setup_logger(name: str = "tts_logger"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

# mp3 파일 병합 (간단한 정적 병합)
def merge_mp3_files(file_list, output_path, silence_ms=800):
    if not file_list:
        logger.warning("[병합] 병합할 파일이 없습니다.")
        return None
    combined = AudioSegment.empty()
    pause = AudioSegment.silent(duration=silence_ms)
    for f in file_list:
        if not os.path.exists(f) or os.path.getsize(f) < 1000:
            logger.error(f"[병합 제외] 파일 없음/손상: {f}")
            continue
        try:
            seg = AudioSegment.from_mp3(f)
            seg = effects.normalize(seg)
            combined += seg + pause
        except Exception as e:
            logger.error(f"[병합 실패] {f}: {e}")
            continue
    if len(combined) == 0:
        logger.error("[병합] 유효한 mp3가 없습니다.")
        return None
    combined.export(output_path, format="mp3")
    logger.info(f"[병합] {output_path} 저장 완료")
    return output_path

# mp3 파일 리스트 반환 (정렬)
def get_mp3_files_sorted(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.mp3')]
    files.sort()
    return files

# ffmpeg로 mp3 pitch 조정 (n_semitones: +12=1옥타브↑, -12=1옥타브↓)
def change_pitch_ffmpeg(input_path, output_path, n_semitones):
    try:
        rate = 2 ** (n_semitones / 12)
        command = [
            "ffmpeg", "-y", "-i", input_path,
            "-af", f"asetrate=44100*{rate:.5f},aresample=44100",
            output_path
        ]
        subprocess.run(command, check=True, capture_output=True)
        logger.info(f"[피치 변환] {input_path} → {output_path} ({n_semitones}반음)")
    except Exception as e:
        logger.error(f"[피치 변환 실패] {input_path}: {e}") 