# 📌 1. 완전탐색
- 가능한 모든 경우의 수를 전부 시도해보는 방법
- 경우의 수가 작을 때 사용하면 좋은 선택이 될 수 있다. 

### 📌 1-1. 최소직사각형

완전 탐색이지만 최적화된 선형 탐색에 가깝다.  
한번에 풀면서 최선의 방법을 찾아간다.  
더 큰 걸로 갱신하는 것이므로 `max`를 사용하여 갱신한다.
if문을 사용해도 크게 상관없다.

---

#### ✅ 코드
명함을 가로, 세로 구분 없이 긴 변을 가로로, 짧은 변을 세로로 정렬한다.  
그 후 각 변 중 최대값을 찾아 직사각형의 크기를 결정한다.
```java
public int solution(int[][] sizes) {
    int answer = 0;
    int m = 0; // 둘 중 큰 것 중에 제일 큰거
    int n = 0; // 둘 중 작은 것 중에 제일 큰거
    for (int[] i : sizes){
        int pm = Math.max(i[0], i[1]);
        int pn = Math.min(i[0], i[1]);

        m = Math.max(pm, m);
        n = Math.max(pn, n);
    }
    return m * n;
}
```

---

#### ⚠️ 주의할 점:

`Math.max(pm, m);`와 `Math.max(pn, n);` 구문은 반환값을 저장해야 값이 갱신된다.  
---

### 📌 1-2. 모의고사
- 타입이 명확할 때 `new int[]{}`를 사용하지 않고 `{}`만으로 배열을 초기화할 수 있다.
- 이미 정렬된 데이터를 순서대로 처리했다면, 별도로 정렬할 필요가 없다.

---

#### ✅ 코드
```java
public int[] solution(int[] answers) {
    int[] first = {1, 2, 3, 4, 5}; // 첫 번째 사망의 패턴
    int[] sec = {2, 1, 2, 3, 2, 4, 2, 5}; // 두 번째 사망의 패턴
    int[] trd = {3, 3, 1, 1, 2, 2, 4, 4, 5, 5}; // 세 번째 사망의 패턴

    int[] scores = new int[3]; // 세 사망의 점수 저장

    for (int i = 0; i < answers.length; i++) {
        if (answers[i] == first[i % first.length]) scores[0]++;
        if (answers[i] == sec[i % sec.length]) scores[1]++;
        if (answers[i] == trd[i % trd.length]) scores[2]++;
    }

    int maxScore = Math.max(scores[0], Math.max(scores[1], scores[2]));

    List<Integer> answer = new ArrayList<>();
    for (int i = 0; i < scores.length; i++) {
        if (scores[i] == maxScore) {
            answer.add(i + 1); // 1번, 2번, 3번 사망
        }
    }

    return answer.stream().mapToInt(i -> i).toArray();
}
```

---

#### ⚠️ 주의할 점:

- 배열을 초기화할 때 타입이 명확하다면 `new int[]{}` 없이 `{}`로 다음과 같이 사용할 수 있다.
- 점수를 계산할 때, 배열 패턴의 길이를 최가하지 않기 위해 `%` 연산을 이용한다.
- 최대 점수를 받은 사람을 고르는 것은, 이미 `scores` 배열이 정렬되어 있고 순서대로 순회하기 때문에 별도로 정렬할 필요가 없다.
---
