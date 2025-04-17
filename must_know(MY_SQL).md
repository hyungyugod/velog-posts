# 0. SQL 논리 흐름
- 1: FROM - 기본 테이블 선택
- 2: JOIN - JOIN 연결
- 3: ON - JOIN 조건 평가
- 4: WHERE - 행 필터링
- 5: GROUP BY - 그룹핑
- 6: HAVING - 그룹 결과 필터링
- 7: SELECT - 최종 출력 컬럼 선택
- 8: ORDER BY - 정렬
- 9: LIMIT - 출력 개수 제한

# 1. 문자열 함수
- UPPER(str): 문자열을 모두 대문자로 변환 - UPPER('hello') → 'HELLO'
- LOWER(str): 문자열을 모두 소문자로 변환 - LOWER('HELLO') → 'hello'
- CHAR_LENGTH(str): 문자열의 문자 수 반환 - CHAR_LENGTH('가나다') → 3
- CONCAT(str1, str2, ...): 문자열을 이어붙임 - CONCAT('Hello', '', 'World') → 'HelloWorld'
- SUBSTRING(str, pos, len): 문자열에서 일부를 추출 (1부터 시작) - SUBSTRING('abcdef', 2, 3) → 'bcd'
- LEFT(str, n): 왼쪽에서 n글자 추출 - LEFT('abcdef', 3) → 'abc'
- RIGHT(str, n): 오른쪽에서 n글자 추출 - RIGHT('abcdef', 2) → 'ef'
- TRIM(str): 문자열 양쪽의 공백 제거 - TRIM(' hello ') → 'hello'
- REPLACE(str, from, to): 문자열 일부를 다른 문자로 변경 - REPLACE('banana', 'na', 'ny') → 'bannya'
- INSTR(str, substr): 문자열에서 substr이 처음 등장하는 위치 반환 (1부터 시작) - INSTR('apple', 'l') → 4
- LPAD(str, len, pad_str): 왼쪽을 pad_str로 채워 총 길이를 len으로 맞춤 - LPAD('world', 10, '*') → '*****world'
- RPAD(str, len, pad_str): 오른쪽을 pad_str로 채워 총 길이를 len으로 맞춤 - RPAD('world', 10, '*') → 'world*****'
- FORMAT(number, decimal_plc): 천 단위 콤마와 소수점 자리수 지정 - FORMAT(12345, 2) → '12,345.00'

# 2. 날짜 관련
- DATE(): 날짜만 추출한다.
- YEAR(): 연도만 추출한다.
- MONTH(): 월만 추출한다.
- DAY(): 일(day)만 추출한다.
- HOUR(): 시(hour)만 추출한다.
- MINUTE(): 분(minute)만 추출한다.
- SECOND(): 초(second)만 추출한다.
- DATE_FORMAT(): 원하는 형식으로 날짜 및 시간을 포맷한다.
- DAYNAME(): 요일 이름을 반환한다. (예: Monday)
- DAYOFWEEK(): 요일 번호를 반환한다. (1=일요일, 7=토요일)
- DATE_ADD(): 날짜/시간을 더한다.
- DATE_SUB(): 날짜/시간을 뺀다.
- TIMESTAMPDIFF(): 두 날짜/시간의 차이를 구한다.
- DATEDIFF(): 양 끝을 뺀 '차이'(일수-일수) 만 계산 즉, 양쪽 날짜 수 포함 계산하려면 +1 해야 한다.

### 2-1. 날짜 포멧 관련 참고표
- %Y: 연도 (4자리) - 예시: 2025 (2025-04-06 14:30:00)
- %y: 연도 (2자리) - 예시: 25 (2025-04-06 14:30:00)
- %m: 월 (2자리) - 예시: 04 (2025-04-06 14:30:00)
- %c: 월 (숫자) - 예시: 4 (2025-04-06 14:30:00)
- %d: 일 (2자리) - 예시: 06 (2025-04-06 14:30:00)
- %e: 일 (숫자) - 예시: 6 (2025-04-06 14:30:00)
- %H: 시 (24시간) - 예시: 14 (2025-04-06 14:30:00)
- %i: 분 - 예시: 30 (2025-04-06 14:30:00)
- %s: 초 - 예시: 00 (2025-04-06 14:30:00)

# 3. 기타 함수
- FIND_IN_SET('가죽시트', OPTIONS): 옵션에 특정 목록이 포함되어 있는지
- IF(expr, t, f): expr이 참이면 t, 거짓이면 f 반환 - IF(grade=4, '졸업반', '재학생') → '졸업반'
- IFNULL(expr1, expr2): expr1이 NULL이면 expr2 반환, 아니면 expr1 반환 - IFNULL(email, '없음') → 이메일이 NULL이면 '없음'
- NULLIF(expr1, expr2): 두 값이 같으면 NULL 반환, 다르면 expr1 반환 - NULLIF(grade, 1) → grade가 1이면 NULL
- CASE WHEN ... THEN ... ELSE ... END: 복수 조건을 처리하는 일반적인 조건 분기 구문 - CASE WHEN gender = '남' THEN 'M' END

# 4. 숫자관련 함수
- ABS(x): 절댓값 반환 - ABS(-5) → 5
- POWER(x, y): x의 y제곱 계산 - POWER(2, 3) → 8
- ROUND(x, d): 소수점 d자리까지 반올림 - ROUND(3.1415, 2) → 3.14
- CEIL(x) / CEILING(x): 올림값 반환 (소수점 위로) - CEIL(3.2) → 4
- FLOOR(x): 내림값 반환 (소수점 아래로) - FLOOR(3.8) → 3
- TRUNCATE(x, d): 소수점 d자리까지 자름 - TRUNCATE(3.1415, 2) → 3.14
- MOD(x, y): x를 y로 나눈 나머지 - MOD(10, 3) → 1
- SIGN(x): x가 양수면 1, 0이면 0, 음수면 -1 반환 - SIGN(10) → 1
- RAND(): 0 이상 1 미만의 난수 반환 - RAND() → 예: 0.5728
- DECIMAL(전체 자리수, 소숫점 아래 자리수): 소숫점으로 변환

# 5. 윈도우 함수
**- 집계함수처럼 단일 행 함수가 아니라 모든 행을 돌면서 해당 연산을 수행한다.**
- ROW_NUMBER() : 행마다 고유 번호 부여 - 페이징, 그룹별 1등 - ROW_NUMBER() OVER (PARTITION BY FOOD_TYPE ORDER BY FAVORITES DESC)
- RANK() : 공동 순위 허용, 순위 건너뜀 - 순위 매기기 - RANK() OVER (PARTITION BY FOOD_TYPE ORDER BY FAVORITES DESC)
- DENSE_RANK() : 공동 순위 허용, 순위 건너뛰지 않음 - 공동 순위가 있을 때 - DENSE_RANK() OVER (PARTITION BY FOOD_TYPE ORDER BY FAVORITES DESC)
- SUM(x) OVER (윈도우) : 누적 합계 구하기 - 매출 누적, 기간별 집계 - SUM(SALES) OVER (PARTITION BY YEAR ORDER BY MONTH)
- AVG(x) OVER (윈도우) : 누적 평균 구하기 - 기간별 평균 집계 - AVG(SALES) OVER (PARTITION BY YEAR ORDER BY MONTH)
- COUNT(x) OVER (윈도우) : 누적 개수 구하기 - 행 수 누적, 카운트 - COUNT(*) OVER (PARTITION BY YEAR ORDER BY MONTH)
- LAG(x, offset, default) OVER (윈도우) : 이전 행의 값 참조 - 전일 대비 매출 증감, 증감 분석 - LAG(SALES, 1, 0) OVER (PARTITION BY YEAR ORDER BY MONTH)
- LEAD(x, offset, default) OVER (윈도우) : 다음 행의 값 참조 - 미래 값 예측, 다음 단계 참조 - LEAD(SALES, 1, 0) OVER (PARTITION BY YEAR ORDER BY MONTH)
- FIRST_VALUE(x) OVER (윈도우) : 그룹 내 첫 번째 값 반환 - 그룹별 최고/최저 값 참조 - FIRST_VALUE(SALES) OVER (PARTITION BY YEAR ORDER BY MONTH)
- LAST_VALUE(x) OVER (윈도우) : 그룹 내 마지막 값 반환 - 그룹별 누적합 또는 최종 값 참조 - LAST_VALUE(SALES) OVER (PARTITION BY YEAR ORDER BY MONTH ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
