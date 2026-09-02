# fsrs_vendor — 벤더링 고지

## 원본

| 항목 | 값 |
|---|---|
| 패키지 | **py-fsrs** (Free Spaced Repetition Scheduler, 공식 Python 구현) |
| 버전 | **6.3.2** |
| 출처 | https://github.com/open-spaced-repetition/py-fsrs |
| 라이선스 | **MIT License** — Copyright (c) 2022 Open Spaced Repetition |
| 벤더링 일자 | 2026-08-20 |
| 벤더링 목적 | 오답 원장 빌더 v3가 `pip install` 없이 순수 표준 라이브러리만으로 FSRS-6 스케줄링을 돌리게 하기 위함 |

MIT 라이선스 전문은 원 저장소 `LICENSE` 파일과 동일하다. 저작권 고지는
아래에 보존한다.

```
MIT License

Copyright (c) 2022 Open Spaced Repetition

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 포함 파일

```
fsrs_vendor/
  __init__.py     ← 새로 작성(원본 대체)
  card.py         ← 수정
  rating.py       ← 원본 그대로
  review_log.py   ← 수정
  scheduler.py    ← 수정
  state.py        ← 원본 그대로
  py.typed        ← 원본 그대로
```

## 수정 내역 (전부 "임포트·문법" 층위. 알고리즘은 무손상)

### 1. `optimizer.py` 제외

원본 `fsrs/optimizer.py`(674줄)는 **복사하지 않았다**. FSRS 파라미터를
사용자 리뷰 로그로 재학습하는 모듈이며 `torch`·`pandas` 등 무거운 선택
의존을 요구한다. 오답 원장은 기본 파라미터만 쓰므로 불필요하다.

이에 맞춰 `__init__.py`에서 다음을 제거했다.

- `if TYPE_CHECKING: from fsrs.optimizer import Optimizer`
- `Optimizer`를 지연 로딩하던 모듈 수준 `__getattr__`
- `__all__`의 `"Optimizer"` 항목

`from fsrs_vendor import Optimizer`는 `ImportError`가 된다(의도된 동작).

### 2. `typing_extensions` 의존 제거 → 표준 라이브러리 폴백

원본은 `card.py` / `review_log.py` / `scheduler.py` 세 곳에서
`from typing_extensions import Self`를 한다. py-fsrs의 **유일한 런타임
서드파티 의존**이었다. 다음 3단 폴백으로 교체했다.

```python
try:
    from typing_extensions import Self      # 설치돼 있으면 그대로 사용
except ImportError:
    try:
        from typing import Self             # Python 3.11+ 표준
    except ImportError:
        from typing import TypeVar
        Self = TypeVar("Self")              # 3.9~3.10 최종 폴백
```

세 모듈 모두 `from __future__ import annotations`(PEP 563)가 켜져 있어
`Self`는 **어노테이션 문자열 안에서만** 등장한다. 즉 런타임에 평가되지
않으므로 `TypeVar` 폴백으로도 동작·수치에 아무 영향이 없다. 어노테이션을
지우지 않고 살려 둔 이유다.

### 3. 절대 임포트 → 상대 임포트

`from fsrs.card import Card` 같은 패키지 절대 임포트를 `from .card import
Card`로 바꿨다. 덕분에
- 폴더 이름이 `fsrs`가 아니어도(=`fsrs_vendor`) 동작하고,
- pip 설치본 `fsrs`가 같은 인터프리터에 있어도 **서로 간섭하지 않는다**
  (`sys.modules["fsrs"]`를 건드리지 않음).

빌더가 `sys.path`를 조작할 필요가 없어진 것도 이 변경 덕이다.

### 4. `match`/`case` → `if`/`elif` (scheduler.py `review_card`)

원본 `Scheduler.review_card`는 구조적 패턴 매칭(`match` 문, **Python
3.10+ 전용 문법**)으로 카드 상태·평점을 분기한다. 3.9에서는 **임포트
자체가 SyntaxError**로 실패한다. 4개 `match` 블록(총 17개 `case`)을
등가 `if`/`elif` 사슬로 치환했다.

치환 규칙은 기계적이다.

| 원본 | 치환 |
|---|---|
| `match card.state:` / `case State.Learning:` | `if card.state == State.Learning:` |
| `match rating:` / `case Rating.Again:` | `if rating == Rating.Again:` |
| `case Rating.Hard \| Rating.Good \| Rating.Easy:` | `elif rating in (Rating.Hard, Rating.Good, Rating.Easy):` |
| `case _:` | `else:` |

`match`의 값 패턴(dotted name)은 `==` 비교로 정의되므로 의미가 정확히
보존된다. 분기 순서·본문·예외 메시지는 그대로 두었다.

> **검증**: 4개 상태 × 4개 평점 × 무작위 간격으로 20,000회 리뷰를 돌려
> pip 설치본 `fsrs` 6.3.2와 `(state, step, stability, difficulty, due)`가
> 전부 일치함을 확인했다. `VALIDATION.md` §8 참조.

### 5. 모듈 docstring 헤더 표기

`fsrs.scheduler` → `fsrs_vendor.scheduler` 등, 문서 문자열의 모듈 경로
표기만 바꿨다. 코드 영향 없음.

## 손대지 않은 것

- `DEFAULT_PARAMETERS`(FSRS-6 기본 21개 가중치), `FSRS_DEFAULT_DECAY`,
  상·하한 경계, `FUZZ_RANGES`
- `_initial_stability` / `_initial_difficulty` / `_next_stability` /
  `_short_term_stability` / `_next_difficulty` / `_next_interval` /
  `get_card_retrievability` — **수식 전부 원본 그대로**
- `Card` / `ReviewLog` / `Rating` / `State`의 필드·직렬화 포맷
  (`to_dict` / `from_dict` / `to_json` / `from_json`)

## 지원 파이썬

**3.9 이상.** 위 수정 2·4로 3.9 임포트 및 실행이 가능해졌다(원본 py-fsrs
6.3.2는 3.10+ 요구). 3.11+에서는 `typing.Self` 표준 경로를 탄다.

## 업스트림 갱신 방법

1. `pip download fsrs==<새버전>` 후 `fsrs/` 추출
2. `optimizer.py` 제외하고 복사
3. 위 수정 2·3·4 재적용 (4번은 업스트림이 `match`를 계속 쓰는 한 필요)
4. `VALIDATION.md` §8의 등가성 테스트 재실행
5. 이 문서의 버전·일자 갱신
