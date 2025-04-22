# 📌 1. 스택/큐 2
### 📌 1-1. 올바른 괄호

문자열에 포함된 괄호 `'('`, `')'`의 짝이 올바르게 구성되어 있는지를 판단하는 문제이다.

---

#### 📌 핵심 요약:

- `'('` 없이 `')'`가 먼저 나오는 경우 → `false`
- 모든 문자를 확인한 뒤에도 `'('`가 남아 있다면 → `false`
- 괄호의 개수는 맞아야 하고, 순서도 맞아야 한다.
- **정렬이나 인덱스 조작이 필요 없으므로 `Deque` 사용이 적절하다.**
- `Deque`를 스택처럼 사용하여 선입후출 구조를 구현한다.
- 사실상 카운트를 통해 더 간단하게 풀 수 있는 문제이나, **자료구조 학습 목적**으로 `Deque`를 활용해 구현하였다.

---

#### ✅ 예시 설명:

##### 입력 문자열: `"()()"`, `"(())"`, `"(()))"` 등

각 문자에 대해 다음과 같은 로직을 따른다:

1. 현재 문자가 `')'`인데 스택이 비어 있다면 → 짝이 없으므로 `false`
2. `'('`이면 스택에 추가
3. `')'`이면 스택에서 `'('` 제거 (짝 맞추기)
4. 반복 종료 후에도 스택이 비어 있지 않다면 → 남은 `'('`이 있다는 뜻이므로 `false`

---

#### 🔎 코드 구현 (Java)

```java
boolean solution(String s) {
    Deque<String> left = new ArrayDeque<>();  // 왼쪽 괄호를 담을 덱

    for (char i : s.toCharArray()) {
        // 스택이 비었는데 오른쪽 괄호가 들어오면 올바르지 않음
        if (left.isEmpty() && i == ')') {
            return false;
        }

        // 왼쪽 괄호일 경우 덱에 추가
        else if (i == '(') {
            left.offer(String.valueOf(i));
        }

        // 오른쪽 괄호일 경우 덱에서 왼쪽 괄호 제거
        else if (i == ')') {
            left.poll();
        }
    }

    // 모두 처리한 후에도 왼쪽 괄호가 남아있으면 false
    if (!left.isEmpty()) {
        return false;
    }

    return true;  // 모든 괄호가 짝지어졌다면 true
}
```

---

##### ⚠️ 주의할 점:

- 단순히 괄호의 개수가 같은지뿐만 아니라 **올바른 순서**로 짝지어졌는지를 확인해야 한다.
- `Deque`는 `Stack`보다 더 유연하며, Java에서는 `ArrayDeque`가 `Stack`보다 성능적으로 더 유리하다.

---

### 📘 1-2. 프로세스 (Queue)

> 실시간 타겟 위치를 추적하며 큐를 활용한 문서 인쇄 시뮬레이션 문제를 다룬다.  
> 큐를 사용하되, 각 원소에 **우선순위와 원래 인덱스 정보를 함께 저장**하여 문제를 해결한다. (배열을 저장할 수 있는 큐와 리스트의 장점 활용)

---

#### 📌 핵심 요약:

- 큐에서 원소를 꺼내 뒤에 더 큰 우선순위가 있으면 다시 넣고, 아니면 출력한다.
- 출력된 순서를 기준으로 원하는 문서가 몇 번째로 출력되는지를 구한다.
- **실시간 포인터 추적** 개념이 문제 해결에 중요하다.
- **같은 우선순위가 여러 개일 수 있으므로 PriorityQueue는 부적절**하며, **배열 정보를 함께 큐에 저장하는 방법이 정석적**이다.

---

#### ✅ 예시 설명:

아래는 `priorities` 배열과 `location` 값이 주어졌을 때, 해당 위치의 문서가 몇 번째로 출력되는지를 구하는 코드이다.

```java
public int solution(int[] priorities, int location) {
    Queue<int[]> queue = new LinkedList<>();

    // 큐에 [우선순위, 인덱스(원래있던 위치)] 형태로 저장
    for (int i = 0; i < priorities.length; i++) {
        queue.offer(new int[]{priorities[i], i});
    }

    int answer = 0;

    while (!queue.isEmpty()) {
        int[] current = queue.poll(); // 맨 앞 요소 꺼냄

        // 뒤에 더 큰 우선순위가 있는지 검사
        boolean hasHigher = false;
        for (int[] q : queue) {
            if (q[0] > current[0]) {
                hasHigher = true;
                break;
            }
        }

        if (hasHigher) {
            queue.offer(current); // 다시 뒤로
        } else {
            answer++; // 인쇄됨
            if (current[1] == location) { // 원래 있던 위치가 찾는 위치와 같다면
                return answer;
            }
        }
    }

    return answer;
}
```

---

#### 💡 추가 정리:

- `PriorityQueue`는 자동 오름차순 정렬이 되어 효율적이지만, **같은 우선순위 문서가 여러 개 있을 경우 인덱스 추적이 어려움**.
- 큐에 배열 또는 객체를 넣어 **우선순위 + 원래 위치 정보**를 함께 관리하는 것이 정석이다.
- Java의 `Queue`는 `LinkedList`로 선언할 수 있으며, 배열 `[priority, index]` 형태로 문서를 구성해 활용 가능하다.
- 실시간으로 타겟 문서의 위치를 추적하는 **포인터 개념**이 핵심 전략이다.

---

#### ⚠️ 주의할 점:

- `PriorityQueue`는 문제의 조건(같은 우선순위 존재, 인덱스 유지 등)과 맞지 않으므로 주의해야 한다.
- 큐에서 원소를 꺼낸 후 무조건 출력하지 않고, **뒤에 더 높은 우선순위가 있는지 확인한 뒤 결정**해야 한다.

---

### 📌 1-3. 다리를 지나는 트럭 (Queue)

트럭들이 일정한 조건(다리의 길이, 하중 제한)에 따라 다리를 건너는 상황을 시뮬레이션하는 문제를 다룬다. 시간의 흐름을 기준으로 트럭의 진입과 퇴출을 효율적으로 관리하기 위해 적절한 자료구조 선택과 전략이 필요하다.

---

#### 📌 개요

- 트럭 수가 많고, 삽입/삭제가 자주 일어나므로 `LinkedList` 사용이 적합하다.
- 트럭이 다리를 지나지 않더라도 시간은 흐르므로 **시간 흐름은 무조건 처리**한다.
- 실제 배열 원소를 제거하는 대신 배열의 나갈 차례인 원소를 찝어주는 **인덱스 포인터 이동 방식**으로 관리하는 것도 고려할 수 있다.
- 트럭의 **퇴출 시간은 "현재 시간 + 다리 길이"**로 계산하여 매번 카운팅하지 않고 마지막에서 검사하는 방식이 효율적이다. (현실에서 괜히 입장시각과 퇴실시각을 관리하는게 아니다.)
- 클래스 사용을 통해 트럭의 속성을 명시적으로 관리함으로써 코드 가독성과 유지보수성이 향상된다.

---

#### 📊 자료구조 선택 가이드

| 상황                                   | 추천 자료구조 | 이유                                      |
|----------------------------------------|----------------|---------------------------------------------|
| 요소 수가 많고, 빠른 삽입/삭제 필요     | `LinkedList`   | 재할당 없이 노드 연결로 안정적인 삽입/삭제 가능 |
| 요소 수가 작거나 중간 탐색이 필요한 경우 | `ArrayDeque`   | 캐시 친화적이며 인덱스 접근이 빠름               |
| 삽입/삭제는 적고 순차 처리만 필요한 경우 | `ArrayDeque`   | 공간 효율이 높고 처리 속도가 우수함              |

---

#### ✅ 코드:
```java
public int solution(int bridge_length, int weight, int[] truck_weights) {
    Queue<Truck> bridge = new LinkedList<>();
    int currentTime = 0;
    int totalWeight = 0;
    int idx = 0; // 현재 나갈 차례 트럭 인덱스

    while (idx < truck_weights.length || !bridge.isEmpty()) { // 조건이 둘 다 만족해야 끝남.
        
        // 트럭이 다리에서 빠져나갈 시간인지 확인 (리스트 가장 앞의 원소를 확인)
        if (!bridge.isEmpty() && bridge.peek().exitTime == currentTime) {
            totalWeight -= bridge.poll().weight; // poll이 호출되면 그즉시 원소가 빠짐
        }

        // 새로운 트럭을 넣을 수 있는지 확인 (배열에서 나갈차례의 원소를 확인)
        if (idx < truck_weights.length && totalWeight + truck_weights[idx] <= weight) {
            totalWeight += truck_weights[idx];
            bridge.offer(new Truck(truck_weights[idx], currentTime + bridge_length)); // 현재 시간 + 다리길이 -> 빠져나갈 시간
            idx++;
        }

        currentTime++; // 모든 일이 벌어진 후 시간이 감 -> while조건이 참이면 시간은 무조건 감으로 위치는 상관없다. 다만 뒤에 있는게 좀 더 현실과 부합하다.

    }

    return currentTime;
}

static class Truck { // solution 클래스 안에 정적 내부 클래스
    int weight;
    int exitTime;

    Truck(int weight, int exitTime) {
        this.weight = weight;
        this.exitTime = exitTime;
    }
}
```

---

#### 📌 핵심 요약:

- 시간은 항상 흐른다 → 시뮬레이션의 기준은 `currentTime++`로 고정
- 다리 위의 트럭은 `Queue`로 관리하며, `exitTime`을 기반으로 퇴출 시점 체크
- 새로운 트럭 진입 시 무게 조건을 확인하고 `Queue`에 삽입
- 트럭 정보를 클래스(`Truck`)로 정의하여 상태 추적이 용이

---

##### ⚠️ 주의할 점:

- 다리 위에서 트럭이 빠지지 않아도 **시간은 무조건 흐르므로** 시간 증가 로직은 항상 실행되어야 한다.
- **다리에서 빠지는 트럭이 우선**되므로, 진입 조건보다 퇴출 조건을 먼저 체크해야 한다.
- 다리에서 트럭을 제거할 때는 무게를 반드시 감소시켜야 하며, `poll()` 순서를 잘 조정해야 한다.

### 📌 1-4. 주식가격

주어진 시점의 주식 가격이 일정 시간 이후까지 떨어지지 않은 기간을 구하는 문제이다.  
주어진 가격 배열을 순회하면서, 스택을 활용해 각 가격이 떨어지는 순간까지의 시간을 계산한다.

---

#### 📌 개요

- 인덱스가 **원본 배열과 스택 대기열의 연결고리** 역할을 한다.
- 이 문제는 전형적인 **스택 활용 문제**로, **스택의 맨 위 요소부터 해결**되어야 나머지 요소도 처리할 수 있다.
- 가격이 떨어지는 순간을 만나면 스택에서 연쇄적으로 `pop`하며 한 번에 처리할 수 있다.
- 각 인덱스를 기준으로 **가격이 떨어지는 첫 시점까지 거리**를 계산하여 결과 배열에 저장한다.

---

#### ✅ 코드
```java
public int[] solution(int[] prices) {
    Stack <Integer> stack = new Stack<>(); // 스택 구현
    int priceLength = prices.length;
    int [] answer = new int[priceLength];

    for (int i = 0; i < priceLength; i++ ){ // 배열 전체를 순회

        while (!stack.isEmpty() && prices[i] < prices[stack.peek()]) { // 이전에 스택에 넣어뒀던게 현재 위치값보다 작다면, peek은 empty 체크와 한 쌍 -> 연쇄작용으로 안작을때까지 pop
            int top = stack.pop(); // pop은 한번만 해야하므로 이렇게 선언하고 해야함.
            answer[top] = i - top; // 옛날 인덱스로부터 현재 인덱스까지 얼마나 멀어져 왔는가.
        }

        stack.push(i); // 앞선 숙제를 다 해결하고 나서야 위에 얹혀짐.
    }

    while (!stack.isEmpty()){
        int top = stack.pop(); 
        answer[top] = priceLength - 1 - top; // 마지막 인덱스와 현재 인덱스간의 거리
    }

    return answer;
}
```

---

#### 📌 핵심 요약:

- 스택에 **가격의 인덱스**를 저장하고, 새로운 가격이 기존보다 낮으면 해당 인덱스를 꺼내면서 소요 시간 계산
- 떨어지지 않은 경우에는 마지막 인덱스까지 거리 계산
- `Stack`은 **이전 문제를 기억하고 해결 시점까지 대기**하는 구조로 이상적

---

##### ⚠️ 주의할 점:

- `while`문 안에서 `pop`은 반드시 **한 번만** 수행해야 하므로 `int top = stack.pop()` 방식으로 처리
- `peek()` 호출 전 반드시 `isEmpty()` 체크가 필요하다
- 스택은 **이전 인덱스를 기억하는 도구**이며, 실제 가격 비교는 `prices[현재] < prices[스택에 저장된 인덱스]` 조건을 사용한다

