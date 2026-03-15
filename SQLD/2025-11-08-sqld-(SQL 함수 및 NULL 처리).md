# 📌 1. DB 설계 단계와 용어 대응

## 1-1. 개념적·논리적·물리적 모델링 개요

- **개념적 모델링(Conceptual Model)**  
  - 무엇을 저장할지 정의하는 단계 (업무, 비즈니스 관점).  
  - 주요 산출물: ER 다이어그램(개체, 속성, 관계).

- **논리적 모델링(Logical Model)**  
  - 개념적 모델을 실제 데이터베이스 구조(테이블, 컬럼 등)로 옮기는 단계.  
  - DBMS에 독립적인 스키마 구조를 설계.

- **물리적 모델링(Physical Model)**  
  - 논리 스키마를 실제 저장구조, 인덱스, 파일 구조 등으로 구현하는 단계.  
  - DBMS마다 달라지는 구체적 튜닝·저장 방식 설계.

## 1-2. 용어 대응표 (개념/논리/물리)

- 같은 실체를 각 단계에서 부르는 이름이 다를 뿐, 의미는 연결되어 있다.

| 구분 | 개념적 모델링 | 논리적 모델링 | 물리적 모델링 |
| --- | --- | --- | --- |
| 데이터 단위 | 개체(Entity) | 테이블(Table) | 파일(File), 저장 블록 |
| 데이터 속성 | 속성(Attribute) | 컬럼(Column), 필드(Field) | 필드, 데이터 타입 |
| 데이터 인스턴스 | 개체 인스턴스 | 튜플(Tuple), 행(Row) | 레코드(Record) |
| 식별 요소 | 식별자(Identifier) | 기본키(Primary Key) | PK 인덱스, 제약조건 |
| 관계 표현 | 관계(Relationship) | 외래키(FK), 조인(Join) | 포인터, 참조 무결성 구현 |
| 제약 조건 | 비즈니스 규칙 | 무결성 제약조건 | 제약, 트리거 등 구현 |


# 📌 2. 집합 연산자 MINUS와 EXCEPT

## 2-1. 기능 비교

- **공통점**  
  - 둘 다 **차집합 연산자**: 앞쪽 SELECT 결과에서 뒤쪽 SELECT 결과를 뺀 나머지 행만 반환.
  - 중복행은 자동 제거 (사실상 DISTINCT 적용).  
  - 두 SELECT의 컬럼 개수·데이터 타입이 같아야 함.

- **차이점**  

| 항목 | Oracle `MINUS` | SQL Server `EXCEPT` |
| --- | --- | --- |
| 표준 여부 | 비표준(Oracle 고유) | ANSI SQL 표준 |
| 사용 예 | `SELECT ... FROM A MINUS SELECT ... FROM B` | `SELECT ... FROM A EXCEPT SELECT ... FROM B` |
| NULL 처리 | NULL 행도 비교에 포함, 동등한 NULL은 제거 | 동작 개념상 동일 |

## 2-2. 예시

- Oracle
  ```sql
  SELECT empno, ename FROM employees
  MINUS
  SELECT empno, ename FROM retired_employees;
  ```

- SQL Server
  ```sql
  SELECT empno, ename FROM employees
  EXCEPT
  SELECT empno, ename FROM retired_employees;
  ```


# 📌 3. Oracle vs SQL Server: 문자열·NULL·따옴표 설계 철학

## 3-1. 문자열 + NULL 연산 철학

- **Oracle**
  - `'ABC' || NULL` → `'ABC'`  
  - 문자열 연산에서 NULL을 “없는 것(공백 비슷)”으로 취급하는 실용주의적 설계.
  - 과거 업무 시스템에서 문자열 필드의 빈값 처리를 편하게 하기 위한 선택.

- **SQL Server (및 표준 SQL)**  
  - `'ABC' + NULL` → `NULL`  
  - NULL을 “값을 모름(unknown)”으로 해석 → 어떤 연산이든 결과도 NULL이어야 논리 일관성이 유지.  
  - 더 수학적·논리주의적 접근.

## 3-2. 문자열 리터럴과 따옴표

- **Oracle**
  - 문자열 리터럴: 반드시 작은따옴표 `'문자열'`만 사용.  
  - 큰따옴표 `"`는 **식별자(identifier)** 용: `"컬럼명"`, `"테이블명"` 등.  
  - C 언어 계열 파서의 전통 + SQL 표준(문자열은 작은따옴표)을 엄격하게 지킴.

- **SQL Server**
  - 기본 규칙은 Oracle과 동일: `'문자열'`이 문자열, `"식별자"`가 식별자.  
  - 단, 설정(`QUOTED_IDENTIFIER`)에 따라 `"문자열"`도 허용하는 유연성 제공.

## 3-3. 작은따옴표 전통의 역사적 배경

- 초기 언어들(Fortran, Algol, C 등)에서  
  - `'A'`는 문자(단일 char), `"ABC"`는 문자열(배열)로 구분되는 문화가 있었음.  
  - C에서 문자 리터럴은 `'A'`, 문자열 리터럴은 `"Hello"`.  
- SQL은 “문자 vs 문자열” 구분은 없지만, C 기반 파서를 재사용하면서 문자열 리터럴에 `'`를 채택.  
- ANSI SQL 표준(1986)에서 **문자열 리터럴은 작은따옴표로** 명시 → 현재까지 유지.


# 📌 4. 문자형 함수 정리 (Oracle/SQL Server 공통 위주)

## 4-1. 주요 문자 함수 표

| 함수 | 구문 | 설명 | 예시 | 결과 |
| --- | --- | --- | --- | --- |
| `UPPER` | `UPPER('hello')` | 소문자를 대문자로 | `UPPER('hello')` | `HELLO` |
| `LOWER` | `LOWER('SQL')` | 대문자를 소문자로 | `LOWER('SQL')` | `sql` |
| `CONCAT` | `CONCAT('A', 'B')` | 두 문자열 연결 | `CONCAT('A', 'B')` | `AB` |
| `SUBSTR` | `SUBSTR('19940216', 1, 4)` | 일부 문자열 추출 | 예시 | `1994` |
| `ASCII` | `ASCII('A')` | 문자 → ASCII 코드 | 예시 | $65$ |
| `CHR` | `CHR(65)` | ASCII 코드 → 문자 | 예시 | `A` |
| `LENGTH` | `LENGTH('abc123')` | 문자열 길이 | 예시 | $6$ |
| `LTRIM` | `LTRIM('###ABC', '#')` | 왼쪽에서 지정문자 반복 제거 | 예시 | `ABC` |
| `RTRIM` | `RTRIM('ABC###', '#')` | 오른쪽에서 지정문자 반복 제거 | 예시 | `ABC` |
| `TRIM` | `TRIM('#' FROM '#A#B#')` | 양쪽에서 지정문자 반복 제거 | 예시 | `A#B` |
| `REPLACE` | `REPLACE('안녕하세요', '안녕', '반가워')` | 부분 문자열 치환 | 예시 | `반가워하세요` |

## 4-2. `SUBSTR`의 시작 위치 규칙

- **시작 위치는 1부터**  
  - `SUBSTR('ABCDEF', 1, 3)` → `ABC`
- **시작 위치가 음수일 때**  
  - 뒤에서부터 셈. 예: `SUBSTR('ABCDEF', -3, 2)` → `DE`  
  - 문자열 끝을 기준으로 인덱싱.

## 4-3. `TRIM`의 지정 문자 제거 특징

- 기본형: `TRIM([LEADING | TRAILING | BOTH] [지정문자 FROM] 문자열)`  
- 지정 문자를 주지 않으면 공백을 제거.  
- **지정한 문자(또는 공백)가 더 이상 보이지 않을 때까지 반복해서 제거**한다.  
  - 예: `TRIM('#' FROM '###ABC#')` → 왼쪽의 `###`와 오른쪽의 `#`가 모두 사라져 `ABC`가 됨.


# 📌 5. 숫자형 함수 정리

## 5-1. 기본 숫자 함수

| 함수 | 구문 | 설명 | 예시 | 결과 |
| --- | --- | --- | --- | --- |
| `ABS` | `ABS(-5)` | 절댓값 | 예시 | $5$ |
| `SIGN` | `SIGN(-10)` | 부호 ($-1, 0, 1$) 반환 | 예시 | $-1$ |
| `MOD` | `MOD(10, 3)` | 나머지 | 예시 | $1$ |
| `CEIL` | `CEIL(3.1)` | 올림 | 예시 | $4$ |
| `FLOOR` | `FLOOR(3.9)` | 내림 | 예시 | $3$ |
| `POWER` | `POWER(2, 3)` | 거듭제곱 | 예시 | $8$ |

## 5-2. ROUND / TRUNC의 두 번째 인자

- 공통형: `ROUND(숫자, 자릿수)`, `TRUNC(숫자, 자릿수)`

### (1) 양수 자릿수

- `ROUND(45.678, 2)` → $45.68$ (소수 둘째 자리까지 반올림)  
- `TRUNC(45.678, 2)` → $45.67$ (소수 둘째 자리까지만 남기고 버림)

### (2) 음수 자릿수

- **정수부 기준 자릿수**를 의미한다.
  - `ROUND(45.678, -1)` → $50$ (1의 자리에서 반올림 → 10단위)  
  - `TRUNC(45.678, -1)` → $40$ (1의 자리 이하 절삭)

## 5-3. TRUNC 이름의 어원

- 영어 **truncate**에서 왔으며, 라틴어 *truncare* = “잘라내다, 절단하다”에서 유래.  
- 함수 의미와 정확히 대응: **숫자를 특정 자릿수에서 '잘라낸 뒤 버리는' 함수**.


# 📌 6. 날짜형 함수 정리

## 6-1. 현재 날짜·시간 함수

| DBMS | 함수 | 예시 | 결과 |
| --- | --- | --- | --- |
| Oracle | `SYSDATE` | `SELECT SYSDATE FROM DUAL;` | 시스템 현재 날짜·시간 |
| SQL Server | `GETDATE()` | `SELECT GETDATE();` | 시스템 현재 날짜·시간 |

## 6-2. 날짜에서 특정 요소 추출

| 기능 | Oracle | SQL Server | 설명 |
| --- | --- | --- | --- |
| 연도 추출 | `EXTRACT(YEAR FROM SYSDATE)` | `DATEPART(YEAR, GETDATE())` | 연도 숫자 반환 |
| 월 추출 | `EXTRACT(MONTH FROM SYSDATE)` | `DATEPART(MONTH, GETDATE())` | 월 숫자 |
| 일, 시, 분, 초 | `EXTRACT(DAY/HOUR/MINUTE/SECOND FROM ...)` | `DATEPART(DAY/HOUR/MINUTE/SECOND, ...)` | 각각 해당 단위 값 |

- 공통적으로 결과는 숫자형.


# 📌 7. 형변환 함수 정리

## 7-1. Oracle / SQL Server 형변환 매핑

| 목적 | Oracle | SQL Server | 설명 |
| --- | --- | --- | --- |
| 날짜 → 문자 | `TO_CHAR(날짜, 'YYYY-MM-DD')` | `CONVERT(VARCHAR, GETDATE(), 120)` | 포맷 또는 스타일 코드 지정 |
| 문자 → 날짜 | `TO_DATE('20250115', 'YYYYMMDD')` | `CAST('2025-01-15' AS DATE)` | 문자열을 날짜 타입으로 변환 |
| 문자 → 숫자 | `TO_NUMBER('12345')` | `CAST('12345' AS INT)` | 문자열을 숫자로 변환 |
| 숫자 → 문자 | `TO_CHAR(123)` | `CAST(123 AS VARCHAR)` | 숫자를 문자열로 변환 |

## 7-2. Oracle 날짜 포맷 요소 (TO_DATE / TO_CHAR)

- 주요 포맷 기호
  - `YYYY` : 연도 4자리  
  - `MM` : 월 2자리 (01, 10 등)  
  - `DD` : 일 2자리 (01, 20 등)  
  - `HH24` : 24시간제 시 ($0 \sim 23$)  
  - `MI` : 분 ($0 \sim 59$)  
  - `SS` : 초 ($0 \sim 59$)

- 예시
  ```sql
  TO_DATE('20250115', 'YYYYMMDD')
  TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS')
  ```

## 7-3. SQL Server 스타일 코드 예시 (CONVERT)

- `CONVERT(VARCHAR, GETDATE(), 120)` → `YYYY-MM-DD HH:MI:SS`
- `CONVERT(VARCHAR, GETDATE(), 112)` → `YYYYMMDD`


# 📌 8. 암시적 형변환(Implicit Conversion)

## 8-1. 형변환 종류

- **명시적 형변환**: 사용자가 직접 함수 호출  
  - 예: `TO_CHAR`, `TO_DATE`, `CAST`, `CONVERT` 등.
- **암시적 형변환**: DB 엔진이 자동으로 데이터형을 맞추는 경우  
  - 예: `'123' + 1` → 문자열 `'123'`을 숫자 $123$으로 해석.

## 8-2. 암시적 형변환의 기준

- 기본 원칙: **더 일반적이고 정보 손실이 적은 타입 기준으로 맞춘다.**

| 표현식 | 기준 타입 | 동작 예 |
| --- | --- | --- |
| 문자 + 숫자 | 숫자 | `'3' + 2` → $5$ (문자를 숫자로 변환 시도) |
| 날짜 + 숫자 | 날짜 | `SYSDATE + 1` → 하루 이후 날짜 |
| 날짜 + 문자 | 날짜 | `'20250101' + 1` → 문자열을 날짜로 변환 후 +1 |
| NULL 포함 연산 | NULL | $10 + NULL 
ightarrow NULL$ |

- 시험용 문장 요약:  
  - 숫자와 문자가 섞이면 **숫자** 기준.  
  - 날짜와 문자가 섞이면 **날짜** 기준.  
  - 날짜와 숫자가 섞이면 **날짜** 기준.


# 📌 9. NULL 함수 정리 (NVL, ISNULL, NULLIF, COALESCE)

## 9-1. 기본 개념

- `NULL`은 “값이 0”이나 “빈 문자열”이 아니라, **값이 존재하는지조차 모르는 상태(unknown)**.  
- 일반 연산에 참여하면 결과도 대부분 `NULL`.  
  - 예: $5 + NULL 
ightarrow NULL$.

## 9-2. NULL 관련 함수 표

| 함수 | 구문 | 설명 | 예시 | 결과 | 비고 |
| --- | --- | --- | --- | --- | --- |
| `NVL` | `NVL(값1, 값2)` | 값1이 NULL이면 값2 반환 | `NVL(NULL, 'X')` | `'X'` | Oracle 전용 |
| `ISNULL` | `ISNULL(값1, 값2)` | 값1이 NULL이면 값2 반환 | `ISNULL(NULL, 0)` | $0$ | SQL Server 전용 |
| `NULLIF` | `NULLIF(값1, 값2)` | 두 값이 같으면 NULL, 다르면 값1 | `NULLIF(10, 10)` | `NULL` | 표준 |
| `COALESCE` | `COALESCE(값1, 값2, 값3, …)` | 인수 중 첫 번째 NULL이 아닌 값 반환 | `COALESCE(NULL, NULL, 'SQL')` | `'SQL'` | 표준, 다중 인자 |

## 9-3. NVL / COALESCE / ISNULL 어원

- **NVL**
  - `Null VaLue` 또는 `Null VaLue substitute` 의 약자.
  - Oracle이 만든 비표준 함수.  
  - 의미: “NULL 값을 다른 값으로 대체한다.”

- **COALESCE**
  - 영어 `coalesce` ← 라틴어 *coalescere* (함께 + 자라다, 합쳐지다).  
  - 의미: 여러 값이 하나로 “응집되어 하나가 된다” → NULL이 아닌 첫 값을 선택.

- **ISNULL**
  - 말 그대로 “is null?”을 묻고, NULL이면 두 번째 인자를 반환.  
  - SQL Server에서 NVL 역할을 담당.


# 📌 10. CASE / SIMPLE CASE / DECODE

## 10-1. 문법 비교 표

| 구분 | 문법 | 특징 |
| --- | --- | --- |
| Searched CASE | `CASE WHEN 조건식1 THEN 결과1 WHEN 조건식2 THEN 결과2 ELSE 결과3 END` | 조건식 자체를 평가 (범위 조건 등 자유로움). |
| Simple CASE | `CASE 표현식 WHEN 값1 THEN 결과1 WHEN 값2 THEN 결과2 ELSE 결과3 END` | 한 표현식을 여러 값과 비교. |
| DECODE (Oracle) | `DECODE(표현식, 값1, 결과1, 값2, 결과2, … [, 기본값])` | Simple CASE와 유사, Oracle 전용. |

## 10-2. 사용 예

- **Searched CASE**
  ```sql
  CASE
      WHEN score >= 90 THEN 'A'
      WHEN score >= 80 THEN 'B'
      ELSE 'C'
  END
  ```

- **Simple CASE**
  ```sql
  CASE grade
      WHEN 'A' THEN 'Excellent'
      WHEN 'B' THEN 'Good'
      ELSE 'Poor'
  END
  ```

- **DECODE**
  ```sql
  DECODE(grade,
         'A', 'Excellent',
         'B', 'Good',
         'C', 'Average',
         'Poor')
  ```

## 10-3. DECODE 이름의 의미

- `decode` = “코드 값을 의미로 풀어 읽는다”는 뜻.  
- 설계 의도: 코드화된 값(예: 등급 코드, 상태 코드)을 사람이 읽기 쉬운 문자열로 변환.


# 📌 11. NULLIF 이름 의미와 TRIM 내부 동작

## 11-1. NULLIF 이름 해석

- 형태: `NULLIF(값1, 값2)`  
- 동작: 두 값이 같으면 `NULL`, 다르면 값1.

- 이름은 **“NULL if …”** 의 축약형으로 이해하면 된다.
  - 영어 문장: “Return NULL if 값1 equals 값2.”
  - 논리: 두 값이 같다면 그 차이는 의미가 없으므로, 결과를 “의미 없음” 상태인 NULL로 둔다.

- 대표 활용 예
  ```sql
  -- 0으로 나누기 방지
  amount / NULLIF(quantity, 0)
  ```
  - `quantity = 0`이면 분모가 `NULL`이 되어 $0$으로 나누는 오류를 피함.

## 11-2. TRIM의 반복 제거와 내부 알고리즘

- TRIM은 **한 번만 잘 자르는 함수가 아니라, 지정 문자가 더 이상 없을 때까지 양쪽 끝에서 반복적으로 제거**하는 함수.

### (1) 개념적 실행 절차

1. 문자열의 시작 인덱스 $start$, 끝 인덱스 $end$ 설정.
2. 왼쪽에서부터 한 글자씩 보면서
   - 지정 문자(또는 공백)이면 $start$를 $1$ 증가.
   - 다른 문자를 만나면 왼쪽 탐색 중단.
3. 오른쪽에서부터 한 글자씩 보면서
   - 지정 문자(또는 공백)이면 $end$를 $1$ 감소.
   - 다른 문자를 만나면 오른쪽 탐색 중단.
4. 최종적으로 `substring(원본문자열, start, end - start + 1)` 구간을 반환.

- 이 과정은 문자열 길이를 $n$이라 할 때, 보통 시간 복잡도는 $O(n)$ 정도.

### (2) LTRIM / RTRIM과의 관계

- `LTRIM` : 왼쪽 끝만 같은 로직으로 반복 제거.  
- `RTRIM` : 오른쪽 끝만 반복 제거.  
- `TRIM` : 기본값 `BOTH`로 양쪽 모두 처리.

---


# 📌 12. IN / NOT IN 과 NULL의 관계

## 12-1. SQL의 3값 논리 (Three-Valued Logic)

SQL은 **TRUE, FALSE, UNKNOWN** 세 가지 논리값을 가진다.  
`NULL`은 단순히 "비어 있는 값"이 아니라 **"값을 알 수 없음"**을 뜻하며,  
비교 연산에 참여하면 결과가 **UNKNOWN**으로 평가된다.

| 값 | 의미 |
|----|------|
| TRUE | 참 |
| FALSE | 거짓 |
| UNKNOWN | 모름 (NULL 연산 결과) |

---

## 12-2. IN()의 내부 동작 원리

`A IN (B, C, D)`는 내부적으로 아래처럼 평가된다.

```sql
(A = B) OR (A = C) OR (A = D)
```

즉, OR 연산으로 비교한 결과 중 하나라도 TRUE면 전체가 TRUE가 된다.

하지만 비교 항목 중 하나라도 NULL이면 → `(A = NULL)`은 항상 **UNKNOWN**이다.

| 비교 결과 | 의미 |
|------------|------|
| TRUE OR UNKNOWN | TRUE |
| FALSE OR UNKNOWN | UNKNOWN |

→ 따라서 모두 불일치(FALSE)이고 NULL이 포함된 경우, 결과는 UNKNOWN → WHERE 조건에서 제외됨.

---

## 12-3. NOT IN()의 내부 동작

`NOT IN`은 단순히 `IN`의 부정이 아니라, 전체 조건을 감싸는 형태이다.

```sql
A NOT IN (B, C, NULL)
→ NOT (A = B OR A = C OR A = NULL)
```

예를 들어 `A = 30`일 때:
```
(FALSE OR FALSE OR UNKNOWN) → UNKNOWN
NOT UNKNOWN → UNKNOWN
```

즉, 결과는 여전히 **UNKNOWN**이며, WHERE 절에서 거짓(FALSE)처럼 취급되어 결과에 포함되지 않는다.

---

## 12-4. 예시

| 값 | 조건 | 결과 |
|:--|:--|:--|
| 10 | `10 IN (10, 20, NULL)` | TRUE |
| 30 | `30 IN (10, 20, NULL)` | UNKNOWN → 제외 |
| 30 | `30 NOT IN (10, 20, NULL)` | UNKNOWN → 제외 |

즉, `IN`과 `NOT IN` 모두 비교 리스트에 NULL이 들어가면 “전체가 알 수 없음(UNKNOWN)”으로 되어  
**결과 행이 누락**될 수 있다.

---

## 12-5. 해결 방법

NULL이 들어올 수 있는 경우 **`NOT EXISTS`** 또는 **`IS [NOT] NULL`** 조합을 사용한다.

```sql
-- 안전한 대체 구문
SELECT *
FROM emp e
WHERE NOT EXISTS (
    SELECT 1
    FROM dept d
    WHERE e.deptno = d.deptno
);
```

---

## 12-6. 요약

| 항목 | 설명 |
|------|------|
| **SQL 논리 체계** | TRUE, FALSE, UNKNOWN 세 가지 값 |
| **NULL 비교 결과** | 항상 UNKNOWN |
| **IN(NULL)** | 일부 비교가 UNKNOWN으로 변해 결과 불확정 |
| **NOT IN(NULL)** | UNKNOWN 부정 시 여전히 UNKNOWN |
| **대안** | `NOT EXISTS`, `IS NULL`, `IS NOT NULL` 사용 |

