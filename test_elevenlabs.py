import sys
print("sys.executable:", sys.executable)
print("sys.path:", sys.path)

from dotenv import load_dotenv
load_dotenv()
print("dotenv loaded")

from main import test_elevenlabs_voices
print("imported test_elevenlabs_voices")

try:
    test_elevenlabs_voices()
    print("test_elevenlabs_voices() 실행 완료")
except Exception as e:
    import traceback
    print("[예외 발생]", e)
    traceback.print_exc()