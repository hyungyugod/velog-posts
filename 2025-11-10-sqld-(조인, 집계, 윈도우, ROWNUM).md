# 📌 1. SQL에서 이름(별칭)과 스코프

## 1-1. 테이블 별칭(alias)과 스코프

- `FROM employee e` 처럼 테이블에 별칭을 주면, **그 쿼리 스코프 안에서는 `employee`라는 원래 이름 대신 `e`만 유효**하다.
- 이유:
  - 별칭은 그 테이블의 **새로운 식별자(identifier)** 로 취급된다.
  - SQL 엔진은 `e`를 “employee 테이블을 가리키는 핸들(handle)”로 사용한다.
  - 같은 쿼리 안에서 `employee.name` 같은 식은 더 이상 허용되지 않고 `e.name`만 사용해야 한다.

- 스코프(scope) 관점:
  - 별칭을 선언하면 그 스코프 안에서 **원래 이름을 가리는(shadowing) 효과**가 있다.
  - 프로그래밍 언어에서 내부 블록의 변수명이 바깥 변수를 가리는 것과 비슷한 개념.

### 적용 범위

- 조인에서만이 아니라
  - 서브쿼리 인라인 뷰:

    ```sql
    SELECT *
    FROM (SELECT * FROM employee) e
    WHERE e.salary > 5000;
    ```

  - CTE (`WITH`):

    ```sql
    WITH high_paid AS (
      SELECT * FROM employee WHERE salary > 5000
    )
    SELECT * FROM high_paid;
    ```

- 이처럼 **FROM/서브쿼리/CTE에서 별칭을 선언하면 그 별칭이 “논리적 테이블 이름”**이 된다.

---

## 1-2. SELECT 절 컬럼 별칭과 ORDER BY

- `SELECT salary AS pay` 처럼 컬럼에 별칭을 준 경우:

  ```sql
  SELECT salary AS pay
  FROM employee
  ORDER BY salary;  -- 대부분의 DB에서 허용
  ORDER BY pay;     -- 당연히 허용
  ```

- 대부분의 DBMS에서는 `ORDER BY`에서 **원래 컬럼 이름과 별칭 둘 다** 사용할 수 있다.
- 그러나 서브쿼리처럼 스코프가 닫히면 **별칭만 유효**:

  ```sql
  SELECT *
  FROM (
    SELECT salary AS pay FROM employee
  ) sub
  ORDER BY salary;  -- 오류
  -- ORDER BY pay;  -- 정상
  ```

- 이유:
  - 서브쿼리 결과는 “하나의 가상 테이블”이고, 그 테이블의 컬럼 이름은 이미 `pay`로 정해져 있다.
  - 원래 이름 `salary`는 그 바깥 스코프에서 더 이상 존재하지 않는다.

---

## 1-3. 왜 이렇게 설계했는가 (철학)

1. **명확성(clarity)**  
   - 여러 테이블에 같은 컬럼 이름(`id`, `name` 등)이 있을 때, 별칭을 통해 “어느 테이블의 컬럼인지”를 명확히 한다.

2. **스코프 일관성(scope consistency)**  
   - 한 번 alias가 선언되면, 해당 스코프에서는 그것이 그 객체를 대표해야 한다.
   - 언어 설계 관점에서, “스코프 안에는 하나의 이름만 유효하다”는 규칙이 파서와 옵티마이저를 단순화한다.

3. **쿼리 최적화 용이성**  
   - 엔진은 별칭을 기준으로 조인 계획, 인덱스 사용 등을 추적한다.
   - “이 쿼리에서 테이블 식별은 alias 하나만 쓴다”라는 규칙이 있으면 내부 구조가 훨씬 단순해진다.

---

# 📌 2. FROM / WHERE / JOIN, 카티션 곱과 실행 순서

## 2-1. SQL의 논리적 실행 순서

SQL은 우리가 작성한 순서가 아니라 **논리적 실행 순서**로 해석된다.

1. `FROM`
2. `ON`
3. `JOIN`
4. `WHERE`
5. `GROUP BY`
6. `HAVING`
7. `SELECT`
8. `ORDER BY`

이 순서를 이해하면:
- 어느 절에서 **별칭/컬럼을 쓸 수 있는지**
- 서브쿼리가 **외부 값을 언제 참조할 수 있는지**
를 자연스럽게 이해할 수 있다.

---

## 2-2. `FROM A, B` 와 카티션 곱

### 카티션 곱(Cartesian Product)

- `FROM A, B` 는 논리적으로 **카티션 곱 A × B** 를 의미한다.
- A에 3행, B에 2행이 있으면, 결과는 3 × 2 = 6행.

- 관계대수로 표현하면:

  - 카티션 곱: A × B
  - 그 후 WHERE로 필터: σ(조건)(A × B)
  - 마지막 SELECT로 필요한 컬럼만 선택: π(컬럼)(σ(조건)(A × B))

### INNER JOIN과의 관계

```sql
SELECT *
FROM A, B
WHERE A.id = B.id;
```

은 논리적으로

```sql
SELECT *
FROM A
JOIN B ON A.id = B.id;
```

와 동일한 결과를 낸다.  
그러나 개념적으로는

1. 먼저 A × B(모든 조합)
2. 그 중에서 A.id = B.id 인 것만 선택

이라는 “곱 후 필터” 구조다.  
즉, **“자동 inner join”이 아니라 “카티션 곱 + WHERE 필터”** 로 이해해야 한다.

옵티마이저가 내부적으로 이것을 효율적인 JOIN으로 다시 짜 줄 뿐이다.

---

## 2-3. 비동등 조인(Non-Equi Join)

- 일반적인 조인: A.key = B.key (동등조인, equijoin)
- 비동등 조인: = 이 아닌 모든 조건을 사용하는 조인

예:

```sql
SELECT e.name, s.grade
FROM emp e
JOIN sal_grade s
  ON e.salary BETWEEN s.low_sal AND s.high_sal;
```

- e.salary가 특정 구간에 포함되는지를 기준으로 조인.
- 논리적으로는 여전히 A × B 후에 σ(조건)을 적용하는 형태이지만,
- 조인 조건이 **동등 관계가 아니라 범위/불등호**라는 점이 다르다.

성능 면에서는 동등조인보다 최적화가 어렵고 대개 느리다(해시 조인 대신 Nested Loop가 많이 사용).

---

# 📌 3. Set vs Multiset, 중복 처리와 디비전

## 3-1. 관계대수의 집합(Set) vs SQL의 멀티셋(Bag)

- **관계대수(Relational Algebra)**  
  - 테이블(관계)은 **집합(set)** 이다.  
  - 같은 튜플이 두 번 있으면 **하나로 취급**된다.
  - 중복이라는 개념이 원천적으로 없다.

- **SQL**  
  - 현실 세계의 데이터를 다루기 때문에 **멀티셋(multiset, bag)** 모델을 사용한다.
  - 같은 행이 여러 번 존재할 수 있다.
  - 기본적으로 **중복을 제거하지 않는다.**
  - 중복을 없애려면 DISTINCT 를 명시해야 한다.

예:

```sql
SELECT deptno FROM emp;          -- 중복 유지
SELECT DISTINCT deptno FROM emp; -- 중복 제거
```

---

## 3-2. 조인과 중복

- 조인은 기존 테이블의 행을 **연결**할 뿐, 값을 가공해서 새로운 엔티티를 “창조”하는 연산이 아니다.
- 같은 조합이 여러 번 발생하면 그 행은 그대로 여러 번 결과에 나타난다.
- 이 역시 멀티셋 철학을 따른다.

“조인을 통해 새 데이터가 생성된다”는 표현은 엄밀히 말하면 틀리고,  
“기존 데이터를 새로운 관계로 **보여준다(view)**” 가 더 정확하다.  
새 테이블을 “만든다”는 느낌을 주려면

```sql
CREATE TABLE new_table AS
SELECT ...
FROM ... JOIN ...;
```

처럼 별도 저장을 해야 한다.

---

## 3-3. 디비전 연산과 중복 제거

- 관계대수의 디비전(division) R ÷ S는  
  “S 에 있는 모든 값을 가진 R의 튜플을 구하라”는 의미.
- 이 연산은 논리적으로 “조건을 만족하느냐”가 중요하지,  
  **같은 튜플이 몇 번 나왔는지(중복)는 중요하지 않다.**
- 그래서 디비전 결과는 **집합**으로 표현되며 중복은 제거된다.

이 대조를 통해,
- **집합 기반 연산**(디비전, 합집합, 교집합, 차집합)은 중복을 없애고
- **멀티셋 기반 연산**(SELECT, JOIN)은 중복을 그대로 유지한다
는 구조를 이해할 수 있다.

---

# 📌 4. Oracle (+) 외부 조인 표기

## 4-1. 역사적 배경

- ANSI 표준의 LEFT/RIGHT/FULL OUTER JOIN 이 등장하기 전,
  Oracle은 자체적으로 외부 조인을 표현하기 위해 (+) 문법을 만들었다.

예:

```sql
SELECT e.ename, d.dname
FROM emp e, dept d
WHERE e.deptno = d.deptno(+);
```

- 의미: emp를 기준으로, dept에 매칭되는 행이 없어도 emp 행은 유지하라.
  즉, ANSI 스타일로 쓰면:

  ```sql
  FROM emp e
  LEFT OUTER JOIN dept d ON e.deptno = d.deptno;
  ```

---

## 4-2. 왜 기준이 아닌 쪽에 (+) 를 붙는가

- (+) 가 붙은 쪽은 “매칭되는 값이 없어도 NULL 행을 플러스해서(+) 붙이는 쪽”이라는 의미.
- 그래서 기준 테이블(항상 남길 쪽)은 아무 기호가 없고,
- 조건을 만족하지 않아도 결과에 추가(+) 될 쪽에 (+)를 단다.

직관적으로:

> “이 테이블은 값이 없어도 NULL을 채워서 결과에 더해(+) 달라”

---

## 4-3. ANSI OUTER JOIN과의 차이

- (+) 표기는 WHERE 절에 조건과 섞여 있어서 복잡한 조인에서는 읽기 어렵고,  
  FULL OUTER JOIN같은 표현도 힘들다.
- ANSI 방식:

  ```sql
  FROM A
  LEFT OUTER JOIN B ON ...
  RIGHT OUTER JOIN C ON ...
  FULL OUTER JOIN D ON ...
  ```

- 구조적으로 **조인과 필터가 분리**되고,  
  DB 종류 간 이식성도 좋기 때문에 현재는 ANSI 방식을 권장한다.
- Oracle은 하위 호환성을 위해 (+) 를 계속 지원할 뿐이다.

---

# 📌 5. NATURAL JOIN, USING, FULL OUTER JOIN

## 5-1. NATURAL JOIN 설계 이유

- 문제의식: 테이블 간에 이름이 같은 컬럼이 여러 개 있을 때,
  사람은 대개 그 컬럼들로 조인하려는 의도를 갖는다.

```sql
SELECT *
FROM emp
NATURAL JOIN dept;
```

- 역할:
  - 두 테이블의 같은 이름을 가진 모든 컬럼을 자동으로 조인 조건에 사용.
  - 결과에서도 그 공통 컬럼은 한 번만 보여 준다.

- 설계 의도:
  - “사람이 공통 컬럼으로 조인하려는 의도를 자동으로 추론해 주자.”

- 단점:
  - 스키마가 바뀌어 공통 컬럼이 추가되면 조인 의미가 예상치 못하게 변할 수 있다.
  - 그래서 실무에서는 잘 쓰지 않는다.

---

## 5-2. USING 절

```sql
SELECT *
FROM emp
JOIN dept USING (deptno);
```

- 기능:
  - ON emp.deptno = dept.deptno 와 같은 조인을 의미하지만
  - 결과 컬럼에서는 deptno를 한 번만 보여준다.

- 특징:
  - 조인 기준을 명시하면서도 결과를 깔끔하게 만드는 중간 지점:
    - ON: 조인 조건 완전 명시, 컬럼은 두 개 노출
    - USING: 조인 조건 컬럼명만 명시, 컬럼은 하나만 노출
    - NATURAL: 조건도, 컬럼 통합도 자동

---

## 5-3. FULL OUTER JOIN

- LEFT OUTER JOIN: 왼쪽 테이블의 모든 행 + 매칭 실패 시 오른쪽에 NULL
- RIGHT OUTER JOIN: 오른쪽 테이블의 모든 행 + 매칭 실패 시 왼쪽에 NULL
- FULL OUTER JOIN: 양쪽 모두의 모든 행을 남기고, 매칭 실패한 쪽을 NULL로 채운다.

수학적으로:

- 내부조인: 관계가 있는 부분만 (교집합 느낌)
- FULL OUTER JOIN: 관계가 있든 없든, 양쪽의 모든 정보를 보여주자  
  즉, A ⋈ B (inner) + A - B + B - A 의 합집합.

철학적으로는:

> “존재하지 않는 관계(매칭 없음) 역시 정보다.  
> NULL을 통해 그 ‘부재’를 표현하자.”

---

# 📌 6. 서브쿼리: 비연관 / 연관, 스칼라 서브쿼리, 인라인 뷰

## 6-1. 비연관 서브쿼리 (Non-correlated Subquery)

```sql
SELECT ename
FROM emp
WHERE deptno IN (
  SELECT deptno
  FROM dept
  WHERE loc = 'SEOUL'
);
```

- 내부 서브쿼리가 외부 쿼리의 컬럼을 전혀 참조하지 않는다.
- 실행 방식:
  1. 서브쿼리를 한 번 실행해서 결과 집합을 만든다.
  2. 그 결과를 외부 쿼리가 조건으로 사용한다.

---

## 6-2. 연관 서브쿼리 (Correlated Subquery)

```sql
SELECT e.ename
FROM emp e
WHERE e.sal > (
  SELECT AVG(sal)
  FROM emp
  WHERE deptno = e.deptno
);
```

- 내부 서브쿼리에서 외부 쿼리의 컬럼 (e.deptno)을 참조한다.
- 실행 방식:
  1. 외부 쿼리가 emp 를 한 행씩 스캔.
  2. 각 행에 대해 e.deptno 값이 달라지므로, 그 값으로 서브쿼리를 다시 실행.
- 즉, 외부 행마다 서브쿼리가 “연결(correlated)” 되어 반복 실행된다.

---

## 6-3. 스칼라 서브쿼리

스칼라 서브쿼리: 하나의 값(1행 1열)만 반환하는 서브쿼리

```sql
SELECT e.ename,
       (SELECT d.loc
        FROM dept d
        WHERE d.deptno = e.deptno) AS dept_loc
FROM emp e;
```

- SELECT, WHERE, HAVING 등 표현식이 들어올 수 있는 곳에서 사용 가능.
- SELECT 단계에서 행이 준비된 후 평가되므로 외부 컬럼을 참조할 수 있다.

---

# 📌 7. 집합 연산자: UNION / UNION ALL / INTERSECT / MINUS(EXCEPT)

| 연산자 | 의미 | 중복 처리 |
|--------|------|-----------|
| UNION | 두 결과의 합집합 | 중복 제거 |
| UNION ALL | 단순 합 | 중복 유지 |
| INTERSECT | 교집합 | 중복 제거 |
| MINUS / EXCEPT | 차집합 | 중복 제거 |

- ALL이 붙으면 중복 유지, 안 붙으면 DISTINCT(중복 제거).
- UNION은 합집합, INTERSECT는 교집합, MINUS는 차집합.

## 7-1. 정렬/해시와 성능

- 중복 제거를 위해 DB는 정렬(sort) 또는 해시(hash)를 사용한다.
- UNION, INTERSECT, MINUS는 정렬이나 해시를 수행해야 해서 느리다.
- UNION ALL은 단순하게 결과를 이어붙이기 때문에 빠르다.

## 7-2. 우선순위

INTERSECT > UNION / UNION ALL / MINUS(EXCEPT)

- INTERSECT(AND), UNION(OR), MINUS(NOT)의 논리적 대응 때문.
- A INTERSECT B UNION C → (A INTERSECT B) UNION C 로 해석된다.

# 📌 8. AVG()와 NULL 처리

## 8-1. AVG()의 기본 동작

- `AVG(컬럼)`은 **해당 컬럼의 평균값**을 구하는 집계 함수이다.
- 이때 **NULL 값은 계산에서 완전히 제외**된다.
  - 분자(합계) 계산에서 제외
  - 분모(개수)에서도 제외

## 8-2. 예시로 보는 계산 방식

예시 테이블:

| 급여(salary) |
|--------------|
| 3000         |
| NULL         |
| 4000         |

`AVG(salary)` 계산 과정은 다음과 같다.

1. NULL을 제외하고 값만 모은다 → {3000, 4000}
2. 분자(합계) 계산: $3000 + 4000 = 7000$
3. 분모(개수) 계산: 유효한 값 2개 → $2$
4. 평균: $7000 / 2 = 3500$

즉, **NULL은 더하기에서도 빠지고, 개수를 셀 때도 빠진다.**

## 8-3. 수식으로 표현

일반적으로 `AVG(x)`는 다음과 같이 생각할 수 있다.

$$
AVG(x) = \frac{\text{SUM( x 가 NULL 이 아닌 값들 )}}{\text{COUNT( x 가 NULL 이 아닌 값들 )}}
$$

- 분자: “알고 있는 값들”의 합
- 분모: “알고 있는 값들”의 개수
- 설계 철학
  - SQL은 NULL을 **0**이 아니라 **“모르는 값(unknown)”** 으로 취급한다.
  - 따라서 “모르는 값”은 더하지도 않고, 그 개수로 나누지도 않는다.
  - 즉, **“확실히 아는 값들만으로 통계적 의미를 유지한다”**는 철학을 따른다.


# 📌 9. Oracle OUTER JOIN의 (+) 문법과 조건 위치

## 9-1. (+) 기호의 의미

- 오라클 전용 문법에서 `(+)`는 **OUTER JOIN(외부조인)** 을 의미한다.
- `(+)`가 붙은 쪽 테이블은
  - 조인 조건에 일치하는 행이 없더라도
  - **NULL로 채워져서 결과에 포함**될 수 있는 테이블이다.
- 즉, `(+)`가 붙지 않은 쪽이 **기준 테이블(보존되는 쪽)** 이다.

예:

```sql
FROM 회원 A, 회원연락처 B
WHERE A.회원ID = B.회원ID(+);
```

- 기준 테이블: `A` (회원)
- `(+)` 테이블: `B` (회원연락처)
- 결과: A의 모든 행은 유지, B에 없으면 B 쪽 컬럼만 NULL로 채워짐

## 9-2. 구분코드(+) = '휴대폰' 예제

```sql
SELECT A.회원ID AS 회원_회원ID,
       A.이름,
       B.회원ID AS 회원연락처_회원ID,
       B.연락처,
       B.구분코드
FROM 회원 A, 회원연락처 B
WHERE A.회원ID = B.회원ID(+)
  AND B.구분코드(+) = '휴대폰';
```

- 의미
  - A를 기준으로 모든 회원을 먼저 유지한다.
  - B에 대해
    - 회원ID가 일치하고
    - `구분코드 = '휴대폰'` 인 행만 매칭을 시도한다.
  - 만약 해당 조건을 만족하는 B 행이 없으면
    - B의 `회원ID`, `연락처`, `구분코드`가 **NULL로 채워져서** A의 행은 그대로 남는다.

→ 실제로는 “각 회원에 대해 **휴대폰 번호가 있으면 붙이고, 없으면 NULL로 둔다**”는 의미가 된다.

## 9-3. ANSI SQL(표준 JOIN)으로 표현

위의 `(+)` 쿼리는 표준 SQL로 다음과 같이 바꿀 수 있다.

```sql
SELECT A.회원ID AS 회원_회원ID,
       A.이름,
       B.회원ID AS 회원연락처_회원ID,
       B.연락처,
       B.구분코드
FROM 회원 A
LEFT OUTER JOIN 회원연락처 B
  ON A.회원ID = B.회원ID
 AND B.구분코드 = '휴대폰';
```

- `LEFT OUTER JOIN` → 왼쪽 테이블(A)의 행을 모두 유지
- `ON` 절에 `B.구분코드 = '휴대폰'` 조건 포함 → 휴대폰이 아니면 B 컬럼들이 NULL로 채워짐

## 9-4. ON 절과 WHERE 절의 차이 (조건 위치에 따른 결과 차이)

### 9-4-1. 조건을 ON 절 안에 둘 때

```sql
SELECT A.회원ID, A.이름, B.연락처, B.구분코드
FROM 회원 A
LEFT OUTER JOIN 회원연락처 B
  ON A.회원ID = B.회원ID
 AND B.구분코드 = '휴대폰';
```

- A 기준으로 모든 행을 유지한다.
- B 조건이 맞지 않으면 B가 NULL로 채워진다.
- **LEFT OUTER JOIN의 의미가 그대로 유지**된다.

### 9-4-2. 같은 조건을 WHERE 절로 빼는 경우

```sql
SELECT A.회원ID, A.이름, B.연락처, B.구분코드
FROM 회원 A
LEFT OUTER JOIN 회원연락처 B
  ON A.회원ID = B.회원ID
WHERE B.구분코드 = '휴대폰';
```

- 조인 자체는 LEFT OUTER JOIN이지만,
- WHERE에서 `B.구분코드 = '휴대폰'` 필터를 걸면
  - B.구분코드가 `'휴대폰'`이 아닌 행
  - B.구분코드가 `NULL`인 행
  전부 제거된다.
- 결과적으로 **외부조인 효과가 사라지고, INNER JOIN 비슷한 결과**가 된다.

→ 핵심:  
- **ON** 절 조건: “어떻게 붙일지(조인 관계 정의)”  
- **WHERE** 절 조건: “붙인 결과 중 무엇을 남길지(필터링)”

조건을 WHERE로 빼면, 조인 결과에서 NULL로 채워졌던 행들이 필터링 단계에서 떨어져 나간다.

## 9-5. (+)가 일부 조건에만 붙었을 때의 문제

다음 쿼리를 보자.

```sql
SELECT A.회원ID, B.연락처
FROM 회원 A, 회원연락처 B
WHERE A.회원ID = B.회원ID(+)
  AND B.구분코드 = '휴대폰';
```

- `A.회원ID = B.회원ID(+)` : 외부조인 의도
- `B.구분코드 = '휴대폰'` : (+)가 없음 → 일반 WHERE 조건

실제 처리 흐름(논리적):

1. `A.회원ID = B.회원ID(+)` 기준으로 A를 모두 유지한 채 조인 시도.
2. 일치하지 않는 B는 NULL로 채워진 상태의 결과가 만들어짐.
3. 그 결과에 대해 `B.구분코드 = '휴대폰'` 필터를 적용.
   - B.구분코드가 `'휴대폰'`이 아닌 행 제거.
   - B.구분코드가 NULL인 행도 제거.

결과적으로
- 외부조인에서 생긴 NULL 행이 **WHERE 조건에서 모두 삭제**된다.
- 따라서 “왼쪽 행 보존”이라는 OUTER JOIN의 특징이 사라지고,  
  “조건을 만족하는 양쪽 테이블의 행만 남는” 구조가 되어 **INNER JOIN과 비슷한 의미**가 된다.
- 하지만 조인 조건에 더해 추가 필터까지 있으므로, 결과 집합은 **순수한 INNER JOIN보다 더 좁을 수도 있다.**

## 9-6. 보기 2번과 3번 선택지 해석

문제:  
“Oracle에서 OUTER JOIN을 사용할 때 (+) 기호의 의미로 옳은 것은?”

- ② “(+)는 기준 테이블이 조인 조건에 일치하지 않으면 NULL을 반환한다.”  
  - 틀린 이유
    - `(+)`는 **붙은 쪽 테이블**이 조인 실패 시 NULL로 채워진다는 의미다.
    - 기준 테이블(반대쪽)은 항상 그대로 출력된다.
- ③ “(+)는 기준 테이블이 조인 조건에 일치하지 않은 데이터도 출력한다.”  
  - 맞는 이유
    - OUTER JOIN의 본질은 **기준 테이블의 모든 행을 유지**하는 것이다.
    - 조인 조건에 일치하지 않더라도 기준 테이블의 행은 결과에 남고,
      상대 테이블 컬럼만 NULL로 채워진다.
    - 이 동작을 잘 표현한 설명이 ③이다.

요약하면,
- `(+)`가 붙은 테이블 → **NULL로 채워질 수 있는 쪽**
- `(+)`가 안 붙은 테이블 → **기준(행이 항상 유지되는 쪽)** 이다.


# 📌 10. INNER JOIN과 OUTER JOIN 결과 비교 (회원 / 회원연락처 예제)

## 10-1. 예제 데이터

**회원(A)**

| 회원ID | 이름   |
|--------|--------|
| A0001  | 홍길동 |
| A0002  | 김영희 |
| A0003  | 이철수 |

**회원연락처(B)**

| 회원ID | 구분코드 | 연락처        |
|--------|----------|--------------|
| A0001  | 휴대폰   | 010-1111-1111 |
| A0002  | 집전화   | 02-1234-5678  |
| A0004  | 휴대폰   | 010-4444-4444 |

## 10-2. 진짜 INNER JOIN을 했을 때

```sql
SELECT A.회원ID, B.연락처
FROM 회원 A
JOIN 회원연락처 B
  ON A.회원ID = B.회원ID;
```

- 조인 조건: 회원ID 일치
- 결과:

| 회원ID | 연락처        |
|--------|--------------|
| A0001  | 010-1111-1111 |
| A0002  | 02-1234-5678  |

A0003은 B에 없고, A0004는 A에 없기 때문에 제외된다.

## 10-3. LEFT OUTER + WHERE B.구분코드 = '휴대폰' 쿼리

```sql
SELECT A.회원ID, B.연락처
FROM 회원 A, 회원연락처 B
WHERE A.회원ID = B.회원ID(+)
  AND B.구분코드 = '휴대폰';
```

논리적 처리 단계:

1. `A.회원ID = B.회원ID(+)`  
   → A를 기준으로 A0001, A0002, A0003을 모두 유지  
   → B가 없거나 안 맞는 경우 B 쪽은 NULL

   임시 결과(조인 직후):

   | A.회원ID | A.이름 | B.회원ID | B.구분코드 | B.연락처        |
   |----------|--------|----------|------------|-----------------|
   | A0001    | 홍길동 | A0001    | 휴대폰     | 010-1111-1111   |
   | A0002    | 김영희 | A0002    | 집전화     | 02-1234-5678    |
   | A0003    | 이철수 | NULL     | NULL       | NULL            |

2. `AND B.구분코드 = '휴대폰'` 필터 적용
   - A0001: 구분코드 = '휴대폰' → 유지
   - A0002: 구분코드 = '집전화' → 제거
   - A0003: 구분코드 = NULL → 조건 불일치, 제거

최종 결과:

| 회원ID | 연락처        |
|--------|--------------|
| A0001  | 010-1111-1111 |

## 10-4. INNER JOIN과의 관계 정리

- 구조적 관점
  - WHERE에 `(+)` 없는 조건이 들어가면 OUTER JOIN의 NULL 행이 모두 제거되어
    **“왼쪽 행 보존”이라는 특성이 사라진다.**
  - 이 점에서 조인 구조는 **INNER JOIN과 유사해진다.**
- 결과 집합 관점
  - INNER JOIN(회원ID 일치만 조건) → A0001, A0002
  - 현재 쿼리(회원ID 일치 + 구분코드='휴대폰') → A0001만
  - 즉, “INNER JOIN과 같은 구조 + 더 강한 추가 필터”라고 볼 수 있다.

요약:

- WHERE에 일반 조건을 넣으면 외부조인에서 생성된 NULL 행들이 제거된다.
- 이 때문에 “OUTER JOIN이 사실상 INNER JOIN 같은 효과로 축소된다”는 표현을 쓰지만,
  실제 결과는 추가 조건 때문에 INNER JOIN보다 더 좁을 수 있다.


# 📌 11. 다중 컬럼 서브쿼리 (Multi-column Subquery)

## 11-1. 기본 문법

두 개 이상의 컬럼을 **묶어서 한 번에 비교**할 때 사용하는 서브쿼리 문법이다.

```sql
SELECT *
FROM EMPLOYEE
WHERE (DEPT, POSITION)
      IN (SELECT DEPT, POSITION
          FROM PROMOTION_TARGET);
```

- `(DEPT, POSITION)` : 두 컬럼을 하나의 “조합(tuple)”처럼 취급
- 서브쿼리: `PROMOTION_TARGET` 테이블에서 (DEPT, POSITION) 조합 목록을 반환

## 11-2. 동작 원리

위 쿼리는 다음과 같은 의미를 가진다.

- EMPLOYEE 테이블에서
  - DEPT와 POSITION의 조합이
  - PROMOTION_TARGET 테이블에 있는 (DEPT, POSITION) 조합 중 하나와 정확히 일치하는 행만 선택한다.

즉, “**부서와 직급이 모두 특정 대상 목록에 포함되는 직원들**”을 찾는 쿼리이다.

## 11-3. 단일 컬럼 IN과의 비교

- 단일 컬럼 IN

  ```sql
  WHERE DEPT IN ('인사팀', '영업팀')
  ```

  → 부서만 보고 판단

- 다중 컬럼 IN

  ```sql
  WHERE (DEPT, POSITION) IN (('인사팀', '대리'),
                             ('영업팀', '사원'))
  ```

  → 다음 둘 중 하나를 만족하는 행만 선택
  - $DEPT = '인사팀' \land POSITION = '대리'$
  - $DEPT = '영업팀' \land POSITION = '사원'$

- 결국 다음과 같은 논리와 같다.

  ```sql
  WHERE (DEPT = '인사팀' AND POSITION = '대리')
     OR (DEPT = '영업팀' AND POSITION = '사원')
  ```

## 11-4. 정리 및 사용 의의

- 다중 컬럼 서브쿼리는
  - 여러 컬럼의 **조합** 자체를 비교해야 할 때 유용하다.
  - 조건을 길게 나열하지 않고, **조합 단위로 깔끔하게 표현**할 수 있다.
- 설계 철학적으로는
  - 관계형 모델에서 “튜플(행)” 개념을 그대로 WHERE 조건에 가져온 것이라,
  - **여러 속성의 묶음을 하나의 비교 단위로 다루는 집합론적 사고**를 반영하는 문법이다.

# 📌 12. ROLLUP, CUBE, GROUPING SETS 의 결과 방식

## 12-1. ROLLUP 결과 정보
ROLLUP은 계층적인 총계값을 구현하는 구문이다.
GROUP BY ROLLUP(REGION, PRODUCT)를 실행하면 아래와 같이 계층적 정보가 출력된다.

| REGION | PRODUCT | SUM(SALES_AMOUNT) |
|---------|----------|------------------|
| East | Laptop | 2200 |
| East | Tablet | 1100 |
| East | NULL | 3300 |
| West | Laptop | 1100 |
| West | Tablet | 300 |
| West | NULL | 1400 |
| NULL | NULL | 4700 |

ROLLUP(REGION, PRODUCT)은 다음과 같은 계층 계속을 생성한다.

```
GROUP BY (REGION, PRODUCT)
GROUP BY (REGION)
GROUP BY ()
```

그리고 아래와 같이 REGION을 병합하면,

```
GROUP BY REGION, (REGION, PRODUCT)
GROUP BY REGION, (REGION)
GROUP BY REGION, ()
```

같은 결과로 반영되며, 결과적으로는 계층값을 추가해 결과를 얻는다.

## 12-2. CUBE 결과 정보
CUBE(A, B)는 입력된 컬럼의 모든 가능한 조합을 생성한다.

결과로 출력되는 것은

1. (A,B) 집계
2. (A) 집계
3. (B) 집계
4. () 전체 집계

과 같은 4가지 조합이다.

### 결과 순서 방식
CUBE, ROLLUP, GROUPING SETS는 결과 순서를 보장하지 않은다.
결과 순서는 바꾸어지더라도 점수가 다르지 않고, 결과는 ORDER BY로 결정된다.

### 결과 표준
| 구문 | 기본 정렬 결과 | 결과 속성 |
|------|----------------|------------------|
| ROLLUP(A,B) | A, B → (A,NULL) → (NULL,NULL) | 계층적 계속적 총계 |
| CUBE(A,B) | (A,B), (A,NULL), (NULL,B), (NULL,NULL) | 모든 결합조합 |
| GROUPING SETS((A,B),(A),()) | 직접 입력 순서 | 직접 지정 |

---

# 📌 13. ROWNUM, TOP-N, OFFSET/FETCH, 및 스트리밍 처리

## 13-1. ROWNUM 의 기본 속성

ROWNUM은 Oracle의 가상 컬럼이며, 결과 생성 순서대로 1부터 증가한다.

SQL 실행 순서에서 ROWNUM은 ORDER BY보다 먼저 실행되며, 결과는 ORDER BY와 무관하게 복결한다.

### ROWNUM 실행 순서
1. FROM - 테이블 검색
2. WHERE - 조건 필터링 (ROWNUM 포함)
3. ROWNUM 부여 (1부터 순차 증가)
4. SELECT - 컬럼 선택
5. ORDER BY - 마지막 정렬

### ORDER BY 보다 먼저 실행되는 이유
ORDER BY는 모든 결과가 전달된 후에 만 실행되며, ROWNUM은 행을 읽어오는 순간에 증가한다.

### 결과 처리 대비
| SQL | 결과 개요 |
|------|----------------|
| SELECT * FROM EMP WHERE ROWNUM <= 3 ORDER BY SAL DESC; | 정렬전의 첫 3개 행이 정렬되어 보임 |
| SELECT * FROM (SELECT * FROM EMP ORDER BY SAL DESC) WHERE ROWNUM <= 3; | 정렬 후 가장 가짜 사용가능 |


## 13-2. ROWNUM 의 제약

ROWNUM은 순차적으로 증가하기 때문에 한 번이 해당되지 않으면 다음 번호는 생성되지 않는다.

| 조건 | 결과 | 이유 |
|------|------|------|
| ROWNUM = 1 | 가능 | 첫번째 행이 들어오자마자 결과가 채워짐 |
| ROWNUM = 2 | 불가 | 1번이 해당되지 않아 2가 발생 안함 |
| ROWNUM > 1 | 불가 | 1번이 미해당이며 모두 해당 안됨 |
| ROWNUM <= 3 | 가능 | 1~3 순차적 해당 |

그러나 `ROWNUM` 가 `ORDER BY`보다 먼저 실행되면 정렬 전의 결과에서 3개를 목록해 보이는 것이다.


## 13-3. FETCH, OFFSET, FIRST/NEXT, ONLY, WITH TIES

### 개요
SQL 표준(ANSI SQL:2008 이후)에서는 `TOP-N`, `페이징(Paging)` 기능을 위해 다음 키워드를 지원한다.

```sql
SELECT 컬럼
FROM 테이블
ORDER BY 컬럼
OFFSET 시작행수 ROWS
FETCH [FIRST | NEXT] 가져올행수 ROWS [ONLY | WITH TIES];
```

### 각 키워드 설명
| 키워드 | 설명 |
|--------|------|
| OFFSET | 앞의 N행을 건너뜀 (페이징 시작 위치 지정) |
| FETCH | 가져올 행 수를 지정 (TOP-N 기능) |
| FIRST/NEXT | FETCH한 수만큼 앞에서부터 가져옴 |
| ONLY | 지정된 행 수만 반환 |
| WITH TIES | 마지막 행과 같은 값(동점)을 포함 |

### 예시
```sql
-- 상위 3행만 출력
SELECT * FROM EMP ORDER BY SAL DESC FETCH FIRST 3 ROWS ONLY;

-- 5행 건너뛰고 다음 3행 출력 (페이징)
SELECT * FROM EMP ORDER BY SAL DESC OFFSET 5 ROWS FETCH NEXT 3 ROWS ONLY;

-- 마지막 동점 포함
SELECT * FROM EMP ORDER BY SAL DESC FETCH FIRST 3 ROWS WITH TIES;
```


## 13-4. ROWNUM vs FETCH/FIRST

| 구분 | Oracle 11g 이하 | Oracle 12c 이상 (표준 SQL) |
|------|------------------|-----------------------------|
| 상위 N개 | `ROWNUM <= N` (서브쿼리 필요) | `FETCH FIRST N ROWS ONLY` |
| 페이징 | 복잡한 ROWNUM 서브쿼리 | `OFFSET … FETCH` 간단하게 |
| 동점 포함 | 불가능 | `WITH TIES` 지원 |
| 실행 순서 | WHERE 단계에서 필터링 | ORDER BY 이후 실행 |


## 13-5. ROWNUM의 내부 작동 원리

1. Oracle은 테이블을 읽으며 각 행에 ROWNUM을 부여한다.
2. 첫 번째 행이 읽히면 $ROWNUM = 1$ 로 평가된다.
3. WHERE 조건을 동시에 검사한다.
4. 조건을 만족하면 결과집합에 포함된다.
5. 다음 행은 $ROWNUM = 2$ 로 증가한다.
6. `ROWNUM`은 **이전 값이 통과해야만 다음 번호가 생성된다.**

따라서 `ROWNUM = 1`은 가능하지만, `ROWNUM = 2`는 불가능하다.

---

## 13-6. ORDER BY보다 먼저 실행되는 이유

ORDER BY는 **전체 행이 모두 수집된 후 마지막 단계**에서 실행된다.
반면 ROWNUM은 WHERE 절에서 **행이 읽히는 즉시** 부여되므로, ORDER BY 이전의 결과를 필터링한다.

예를 들어:

```sql
SELECT STUDENT_ID, NAME, SCORE
FROM STUDENT
WHERE ROWNUM <= 3
ORDER BY SCORE DESC;
```

이 쿼리는 정렬되지 않은 원본 데이터에서 처음 3행을 뽑은 후, 그 3행만 정렬한다.
결과적으로 "점수 상위 3명"이 아니라, **처음 읽힌 3명만 정렬된 형태로 출력**된다.

올바른 방식은 다음과 같다:

```sql
SELECT STUDENT_ID, NAME, SCORE
FROM (
  SELECT STUDENT_ID, NAME, SCORE
  FROM STUDENT
  ORDER BY SCORE DESC
)
WHERE ROWNUM <= 3;
```

---

## 13-7. 핵심 요약

- $ROWNUM$은 행이 생성될 때 바로 부여된다.
- $ORDER\ BY$는 쿼리 마지막 단계에서 실행된다.
- 따라서 `ROWNUM <= 3 ORDER BY ...`는 정렬 전 데이터에서 상위 3행을 선택한 뒤 정렬만 수행한다.
- `ROWNUM = 1`은 가능하지만 `ROWNUM = 2`는 불가능하다.
- Oracle 12c 이후에는 `FETCH FIRST N ROWS ONLY` 구문으로 이 문제를 해결했다.

---

## 13-8. ROWNUM과 스트리밍 평가

Oracle의 ROWNUM은 **스트리밍 평가 방식**이다. 즉, 행이 읽힐 때마다 즉시 평가하고 통과한 행만 다음 단계로 전달한다. 이 구조 덕분에 대용량 데이터를 효율적으로 처리할 수 있지만, 정렬 이전에 번호가 부여되어 ORDER BY와의 조합에는 주의가 필요하다.


---

## 13-9. 한 줄 정리

> ROWNUM은 행이 읽히는 순간 부여되고, ORDER BY는 마지막에 실행된다.  
> 따라서 ROWNUM이 ORDER BY보다 먼저 실행되어 정렬 전의 데이터가 잘리는 결과를 낸다.  
> Oracle 12c 이후에는 FETCH 구문으로 이 한계를 해결하였다.

