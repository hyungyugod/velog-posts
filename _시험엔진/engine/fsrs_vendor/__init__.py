"""
fsrs_vendor — py-fsrs 6.3.2 벤더링본 (MIT, Open Spaced Repetition)
------------------------------------------------------------------

오답 원장 빌더 v3가 외부 의존 없이(순수 표준 라이브러리) FSRS-6 스케줄링을
돌릴 수 있도록 py-fsrs 6.3.2를 그대로 옮겨 놓은 사본이다.

원본과 달라진 점은 `_VENDOR_NOTE.md` 참조. 요약:
  - optimizer.py 제외 (torch/pandas 등 무거운 선택 의존)
  - typing_extensions 의존 제거 (표준 라이브러리 폴백)
  - 절대 임포트(`from fsrs.x`) → 상대 임포트(`from .x`)
  - match/case(3.10+) → if/elif (3.9에서도 동작)

알고리즘(계산식·기본 파라미터)은 한 글자도 손대지 않았다.
"""

from .card import Card
from .rating import Rating
from .review_log import ReviewLog
from .scheduler import Scheduler
from .state import State

__all__ = ["Card", "Rating", "ReviewLog", "Scheduler", "State"]

__vendored_from__ = "py-fsrs"
__vendored_version__ = "6.3.2"
