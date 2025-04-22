# 1. 힙 (heap)
### 1-1. 힙에 대하여 
- 힙은 자바에서 PriorityQueue<Integer> minHeap = new PriorityQueue<>(); 즉 우선순위 큐로 구현된다.
| 구분             | 최소 힙 (Min‑Heap)                                 | 최대 힙 (Max‑Heap)                                          |
|----------------|---------------------------------------------------|-----------------------------------------------------------|
| 생성 코드        | `new PriorityQueue<>()`                           | `new PriorityQueue<>(Comparator.reverseOrder())`          |
| 우선순위 기준     | `Comparable`의 `compareTo(a, b) < 0`일 때 a 우선     | `Comparator.reverseOrder()`로 `compare(a, b) > 0`일 때 a 우선 |
| 조회 메서드      | `peek()`/`poll()` → **최솟값**                      | `peek()`/`poll()` → **최댓값**                             |
| null 처리       | 삽입 시 NPE 발생                                     | 삽입 시 NPE 발생                                           |
| 초기 용량 설정    | `new PriorityQueue<>(capacity)` 가능               | 동일                                                      |
| 스레드 안전       | ❌ (외부 동기화 필요)                                | ❌ (외부 동기화 필요)                                       |
| 반복 순서        | 비보장                                              | 비보장                                                     |

### 1-2. 트리(Tree) 구조 기본 개념

- **트리(Tree)**  
  계층적 구조를 표현하는 비선형(Non‑linear) 자료구조.  
  여러 개의 노드(Node)가 “부모‑자식(Parent‑Child)” 관계로 연결되어 있고, 최상단의 노드를 **루트(Root)** 라 부름.

- **노드(Node)**  
  트리의 각 요소. 값(value)과 0개 이상의 자식(Child) 노드를 가질 수 있음.  
  - **루트 노드**: 부모가 없는 최상위 노드  
  - **단말 노드(Leaf)**: 자식이 하나도 없는 노드

- **부모‑자식 관계(Parent‑Child)**  
  한 노드가 다른 노드를 직접 가리키면,  
  - 가리키는 노드 → **부모(Parent)**  
  - 가리켜지는 노드 → **자식(Child)**

- **레벨(Level)**  
  루트부터 내려온 깊이(depth)를 기준으로 0번부터 부여.  
  - 루트 레벨 = 0  
  - 루트의 자식 레벨 = 1, 그 자식의 자식 레벨 = 2 …

- **완전 이진 트리(Complete Binary Tree)**  
  모든 레벨이 왼쪽부터 빈틈 없이 채워진 이진 트리.  
  - 마지막 레벨만 왼쪽부터 채워지고, 중간에 공백이 없음  
  - 힙(Heap)의 저장 구조로 최적

- **힙(Heap)**  
  완전 이진 트리에 **부모‑자식 간 우선순위(Heap Property)** 를 추가한 구조  
  - **최대 힙(Max‑Heap)**: 부모 ≥ 자식 -> 루트 노드가 최댓값
  - **최소 힙(Min‑Heap)**: 부모 ≤ 자식 -> 루트 노드가 최솟값

---

### 1-3. 배열(Array)과의 매핑

완전 이진 트리를 배열로 표현하면, 포인터 없이 인덱스 계산만으로 부모·자식 관계를 찾을 수 있다.

| 관계               | 1‑based 인덱스 (첫번째가 1) | 0‑based 인덱스 (첫번째가 0)  |
|------------------|--------------------|--------------------------|
| 부모 노드       | ⌊i/2⌋              | ⌊(i−1)/2⌋               |
| 왼쪽 자식 노드  | 2·i                | 2·i + 1                  |
| 오른쪽 자식 노드| 2·i + 1            | 2·i + 2                  |

```text
예) 배열(1‑based) = [_, 50, 30, 40, 10, 20]
    인덱스 1: 루트(50)
      ├─ 인덱스 2: 왼쪽 자식(30)
      │    ├─ 인덱스 4: 왼쪽 자식(10)
      │    └─ 인덱스 5: 오른쪽 자식(20)
      └─ 인덱스 3: 오른쪽 자식(40)
```

### 📌 1-5. 더 맵게

> 최소 힙을 사용하여 스코빌 지수가 낮은 음식 2개를 반복적으로 섞으며, 목표 지수 이상으로 만드는 문제이다.

---

#### 📌 핵심 요약:

- 최소값을 효율적으로 관리하기 위해 **`PriorityQueue` (최소 힙)**을 사용한다.
- 가장 스코빌 지수가 낮은 음식 2개를 뽑아 섞은 후 다시 힙에 넣는다.
- 이 과정을 통해 **모든 음식의 스코빌 지수가 `K` 이상이 될 때까지 반복**한다.
- 목표 달성이 불가능할 경우 `-1`을 반환한다.
- while안에 if가 있으면 그 조건을 while문 조건식으로 뺄 수 있는지 고민하자

---

#### ✅ 코드:
```java
public int solution(int[] scoville, int K) {
    int answer = 0;
    PriorityQueue heap = new PriorityQueue<>(); // 기본으로 최소힙으로 구현
    int cntTarget = 0; // 대상이 되는 수

    if (K == 0){ // k가 0이면 무조건 되므로 0 리턴하고 끝
        return 0;
    }

    for (int i : scoville){ // 배열의 모든 값을 우선순위 큐에 넣음. 
        if (i < K){
            cntTarget++;
        }
        heap.offer(i); 
    }

    if (cntTarget == 0){ // 올릴게 하나도 없어도 0 리턴
        return 0;
    }

    while (heap.size() > 1 && (int) heap.peek() < K) { // 가장 작은 값이 peek보다 작아야 진행의미가 있음.
        int p1 = (int) heap.poll();
        int p2 = (int) heap.poll();

        heap.offer(p1 + p2 * 2); // 음식을 섞어서 다시 힙에 넣음.
        answer++;
    }

    return (int) heap.peek() >= K ? answer : -1; // 원래 하나 남았을 경우를 if와 else로 했던 것을 삼항 연산자로 정리 
}
```

---

##### ⚠️ 주의할 점:

- `PriorityQueue`는 Java에서 기본적으로 **오름차순(최소 힙)** 으로 정렬된다.
- 음식이 하나만 남았고, 그 값이 `K`보다 작으면 더 이상 섞을 수 없어 `-1`을 반환해야 한다.
- `K`가 0인 경우, 모든 음식이 이미 조건을 만족하므로 **초기값 검사**로 `0`을 반환한다.
- 반복 조건에서 **`heap.size() > 1`**을 반드시 먼저 체크하여 `poll()` 시 예외가 발생하지 않도록 해야 한다.

### 📌 1-6. 디스크 컨트롤러

요청된 작업들을 효율적으로 처리하기 위해 디스크 컨트롤러 문제에서는 **우선순위 큐(PriorityQueue)** 를 사용하여, 작업들을 특정 기준으로 정렬하고 처리하는 방식이 활용된다.  
특히 **소요시간이 짧은 작업을 먼저 처리하는 방식**(SJF: Shortest Job First)과 **요청 시각에 따른 우선순위 관리**가 중요하다.

---

#### 📌 핵심 요약:

- **우선순위 큐에서 배열 사용 시 comparator 지정**이 필수이다. 
- **작업 배열은 힙에 넣기 전에 요청 시점 기준으로 정렬**하고, **현재 시각까지 요청된 작업들만 큐에 삽입**해야 한다.
- 정렬 시 `a - b` 보다는 `Integer.compare(a, b)`를 사용하는 것이 오버플로우 방지 측면에서 더 안전하다.
- **요청된 작업 수를 정확히 파악하고** 현재 가능한 작업만을 처리하는 흐름 설계가 필요하다.

---

#### ✅ 코드:
```java
public int solution(int[][] jobs) {
    // 요청 시간 기준 정렬
    Arrays.sort(jobs, Comparator.comparingInt(a -> a[0]));

    // 소요시간 짧은 순 → 요청시각 빠른 순
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> {
        if (a[1] != b[1]) return a[1] - b[1]; // 소요시간 짧은 순 (오름차순)
        return a[0] - b[0]; // 요청시각 빠른 순 (오름차순)
    });

    int current = 0; // 현재 시각
    int idx = 0; // 배열에서 하나씩 넣는 인덱스
    int total = 0; // 전체 반환시간 (완료시각 - 요청시각)
    int completed = 0; // 작업 완료된 개수

    while (completed < jobs.length) {
        // 현재 시점까지 요청된 작업들을 큐에 넣기
        while (idx < jobs.length && jobs[idx][0] <= current) {
            pq.offer(jobs[idx]);
            idx++;
        }

        if (pq.isEmpty()) {
            current = jobs[idx][0]; // "지금 할 일이 없다면, 다음 작업의 요청 시각으로 곧바로 이동하자!"
        } else {
            int[] job = pq.poll();
            current += job[1];
            total += (current - job[0]);
            completed++;
        }
    }

    return total / jobs.length; // 전체의 평균
}
```

---

#### 🔍 코드 흐름 요약:

1. **jobs 배열을 요청 시간 기준으로 정렬**
   - `Arrays.sort(jobs, Comparator.comparingInt(a -> a[0]))`
2. **소요 시간이 짧은 작업 우선**
   - `PriorityQueue`에서 `a[1]`을 기준으로 정렬
3. **현재 시점 기준으로 큐에 작업 추가**
   - `jobs[idx][0] <= current` 조건 확인
4. **작업이 없을 경우 다음 작업 시간으로 점프**
   - `current = jobs[idx][0]`
5. **작업 처리 후 시간 갱신 및 통계 업데이트**

---

##### ⚠️ 주의할 점:

- **우선순위 큐의 comparator를 설정할 때**, `a - b` 방식은 오버플로우 위험이 있으므로 `Integer.compare(a, b)`가 더 안전하다.
- **작업 배열의 최대 크기나 값의 범위를 반드시 문제에서 확인**해야 한다.
- **현재 가능한 작업만 처리**해야 하며, 아직 요청되지 않은 작업은 큐에 넣지 않는다.
- **작업 요청 시간과 소요 시간을 명확히 구분**하고 각 작업이 완료된 시점과의 차이로 평균 시간을 계산한다.

---


### 📌 1-7. 이중 우선순위 큐

이중 우선순위 큐는 **최솟값과 최댓값을 동시에 효율적으로 관리**해야 하는 자료구조 문제이다. Java의 `PriorityQueue`는 기본적으로 최소 힙 구조로 작동하기 때문에 **최댓값을 구하기 위해서는 O(n)의 시간복잡도가 필요**하다.

> `pq.remove(Collections.max(pq));`와 같이 사용하면 최댓값을 삭제할 수 있으나 비효율적이다.

---

#### ✅ 개선된 풀이: 최소 힙 + 최대 힙 동시 사용

```java
public int[] solution(String[] operations) {
    Queue<Integer> minpq = new PriorityQueue<>();
    Queue<Integer> maxpq = new PriorityQueue<>(Collections.reverseOrder());

    for (String operation : operations) {
        if (operation.startsWith("I ")) {
            int n = Integer.parseInt(operation.substring(2));
            minpq.offer(n);
            maxpq.offer(n);
        } else if (!minpq.isEmpty() && operation.equals("D -1")) {
            maxpq.remove(minpq.poll());
        } else if (!maxpq.isEmpty() && operation.equals("D 1")) {
            minpq.remove(maxpq.poll());
        }
    }

    if (minpq.isEmpty() && maxpq.isEmpty()) {
        return new int[]{0, 0};
    }

    return new int[]{maxpq.poll(), minpq.poll()};
}
```

#### 📌 핵심 요약:

- 최소 힙(`minpq`)과 최대 힙(`maxpq`)을 **동시에 사용하여 삽입, 삭제 시 동기화**한다.
- 삽입 시 두 힙 모두에 데이터를 추가한다.
- 삭제 시 한쪽에서 삭제한 값을 다른 힙에서도 제거한다.

##### ⚠️ 주의할 점:

- 두 힙 간의 데이터가 정확히 일치하도록 유지되어야 한다.
- 삽입과 삭제 연산이 많아질수록 **성능 향상 효과가 두드러진다.**

---

#### 📎 정리

| 항목 | 단일 최소 힙 사용 | 최소 힙 + 최대 힙 병행 |
|------|-------------------|------------------------|
| 최댓값 삭제 | `O(n)` | `O(log n)` |
| 구현 난이도 | 낮음 | 높음 |
| 성능 | 낮음 | 높음 |
| 사용 상황 | 간단한 테스트 | 고성능 요구 |