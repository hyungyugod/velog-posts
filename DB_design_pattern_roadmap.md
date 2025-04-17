# 📦 데이터베이스 디자인 패턴 정리 (기능별 분류)

---

## 1. 유연성/확장성 패턴  
> 속성이 자주 바뀌거나 유동적인 도메인에 적응하기 위한 설계

| 패턴 이름 | 설명 | 실습 포인트 |
|-----------|------|--------------|
| **EAV (Entity-Attribute-Value)** | 속성을 테이블 컬럼으로 갖지 않고, 행으로 표현하여 유연한 구조 제공 | 사용자 입력 필드가 다양한 설문 시스템 |
| **Single Table Inheritance** | 상속된 클래스들을 하나의 테이블에 타입 필드로 구분하여 저장 | `Item` 테이블에 Weapon/Armor 같이 저장 |
| **Class Table Inheritance** | 상속 관계를 각 테이블로 분리하고 키로 연결 | OOP 모델링과 1:1 매칭 |

---

## 2. 무결성/정합성 패턴  
> 데이터 신뢰성 확보, 이력 관리 중심

| 패턴 이름 | 설명 | 실습 포인트 |
|-----------|------|--------------|
| **Audit Trail Pattern** | 변경 기록(이력)을 별도 테이블에 저장 | `Users_Audit` 테이블에 변경 전후 로그 기록 |
| **Soft Delete Pattern** | 실제 삭제 대신 is_deleted 컬럼을 활용 | `DELETE` 대신 `UPDATE is_deleted=1` |
| **Check Constraint Pattern** | 컬럼 값의 유효성을 체크 조건으로 제한 | `CHECK (status IN ('ACTIVE','BLOCKED'))` |

---

## 3. 코드 관리/재사용 패턴  
> 코드값, 카테고리 같은 고정값 관리에 유용

| 패턴 이름 | 설명 | 실습 포인트 |
|-----------|------|--------------|
| **Lookup Table Pattern** | 성별, 지역, 상태 등 코드값을 참조 테이블로 관리 | `Gender`, `StatusCode` 등 코드 관리 테이블 |
| **Static Data Pattern** | 변경이 거의 없는 데이터는 INSERT문으로 직접 고정 | `INSERT INTO Country VALUES('KR', 'Korea')` |

---

## 4. 성능 최적화 패턴  
> 대량 데이터 처리와 속도 중심 설계

| 패턴 이름 | 설명 | 실습 포인트 |
|-----------|------|--------------|
| **Partitioning Pattern** | 데이터를 기준(날짜 등)으로 분할하여 저장 | 월별 `sales_2024_01`, `sales_2024_02` |
| **Indexing Pattern** | 자주 쓰는 조건에 인덱스를 생성하여 성능 개선 | `CREATE INDEX idx_email ON Users(email)` |
| **Materialized View Pattern** | 조인/계산된 결과를 캐시처럼 저장 | 고정된 리포트 쿼리 결과를 미리 계산해두기 |

---

## 5. 관계/구조 패턴  
> 데이터 간의 복잡한 관계나 구조적 모델링에 사용

| 패턴 이름 | 설명 | 실습 포인트 |
|-----------|------|--------------|
| **Recursive Tree Pattern** | 자기 자신과 연결된 계층 구조 표현 | 직원 → 상사 → 상사의 상사... |
| **Many-to-Many Join Table** | N:M 관계를 중간 테이블로 모델링 | 학생 ↔ 과목, 사용자 ↔ 역할 |
| **Polymorphic Association** | 하나의 외래키가 여러 테이블을 참조 | 댓글 대상이 게시글/상품/후기 등일 때 |

---

# 📘 학습 로드맵 (진도표)

| 단계 | 주제 | 목표 | 실습 예시 |
|------|------|------|-----------|
| 1단계 | Lookup Table / EAV | 유연한 설계, 코드값 구조 이해 | 설문지, 회원 상태 코드 |
| 2단계 | Soft Delete / Audit Trail | 이력 추적과 안전한 삭제 구현 | 회원 탈퇴, 이력 저장 |
| 3단계 | Table Inheritance | 객체지향 구조 대응 연습 | 게임 아이템 구조 |
| 4단계 | Many-to-Many / Recursive Tree | 관계 모델링 | 팔로우, 댓글 구조 |
| 5단계 | Partitioning / Indexing / View | 대용량 처리와 성능 | 월별 매출 쿼리, 인덱스 실험 |
