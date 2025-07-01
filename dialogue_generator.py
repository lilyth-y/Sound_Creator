"""
dialogue_generator.py
- 프롬프트/스크립트 생성, 대사 파싱
"""
from typing import List, Tuple
import os
from utils import logger

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    logger.warning("openai 패키지가 설치되어 있지 않습니다.")

# 실제 프롬프트/스크립트 생성
def generate_dialogue(speaker_a: dict, speaker_b: dict, tags: List[str], relationship: str, duration_seconds: int = 30) -> str:
    """
    OpenAI API를 이용해 자연스러운 대화 스크립트를 생성한다.
    """
    if OpenAI is None:
        logger.warning("openai 패키지가 없어 예시 스크립트 반환")
        return "A: <speak>안녕, 잘 지냈어?</speak>\nB: <speak>응, 오랜만이야!</speak>"
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""
    두 명의 한국인 화자(A, B)가 등장하는 자연스러운 대화문을 만들어주세요.
    - 각 대사는 반드시 <speak>로 감싸고, 감정/쉼표/추임새 등 SSML 태그를 적극 활용
    - 각 줄은 'A:' 또는 'B:'로 시작
    - 대화 길이: 약 {duration_seconds}초 분량, 8~12턴
    - 화자 A: {speaker_a}
    - 화자 B: {speaker_b}
    - 관계: {relationship}
    - 상황/태그: {', '.join(tags)}
    - 설명 없이 대화만 출력
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a world-class Korean dialogue writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=1500
        )
        script = response.choices[0].message.content.strip()
        logger.info(f"[스크립트 생성] 완료")
        return script
    except Exception as e:
        logger.error(f"[스크립트 생성 실패] {e}")
        return "A: <speak>안녕, 잘 지냈어?</speak>\nB: <speak>응, 오랜만이야!</speak>"

# 대사 파싱
def parse_dialogue(script: str) -> List[Tuple[str, str]]:
    """
    스크립트에서 (화자, 대사) 튜플 리스트로 파싱
    """
    lines = script.strip().split("\n")
    result = []
    for line in lines:
        if ":" in line:
            speaker, text = line.split(":", 1)
            result.append((speaker.strip(), text.strip()))
    logger.info(f"[대사 파싱] {len(result)}개 라인")
    return result 