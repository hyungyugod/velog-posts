# 1. 정렬

#### 정렬 알고리즘의 이해 (compare, compareTo)
- compare(a,b) -> a - b
- a.compareTo(b) -> a - b (Comparable 인터페이스를 구현한 객체끼리만(객체 스스로가 비교 로직을 가지고 있어야함.) -> 문자하나하나 유니코드 비교)

| 비교 기준                        | 비교 결과            | 실생활 해석                           |
|----------------------------------|----------------------|----------------------------------------|
| a가 더 작다 (`a - b < 0`)        | a가 먼저 와야 한다   | “작은 번호 먼저”, “키 작은 아이 먼저” |
| a와 b가 같다 (`a - b == 0`)      | 순서 유지            | “둘이 같으면 굳이 자리 안 바꿈”       |
| a가 더 크다 (`a - b > 0`)        | b가 먼저 와야 한다   | “큰 번호는 뒤로”, “키 큰 아이는 뒤로” |

- compare와 Comparator.comparing 비교

| 방식                                | 사용 시점                          | 예시                                  | 지금 문제에 적합한가? |
|-------------------------------------|-------------------------------------|----------------------------------------|------------------------|
| `.sorted((a, b) -> ...)`            | 직접 비교식이 필요할 때            | `(b + a).compareTo(a + b)`             | ✅ 예                  |
| `.sorted(Comparator.comparing(key))` | 단일 기준(key)을 추출할 수 있을 때 | `String::length`, `person -> person.age` | ❌ 불가                |


### 📌 1-1. k 번째 수

주어진 문제는 특정 범위의 배열을 잘라 정렬한 뒤, k번째 수를 찾는 과정을 반복하는 것이다.

---

#### 📌 핵심 요약:

- `commands` 배열의 인덱스는 **1부터 시작**하므로, 이를 처리할 때 인덱스에 -1을 해주어야 한다.
- 각 명령에 대해 `array` 배열에서 해당 범위를 복사하여 정렬 후, k번째 수를 추출한다.

---

#### ✅ 코드:
```java
public int[] solution(int[] array, int[][] commands) {
    int[] answer = new int[commands.length];
    for (int i = 0; i < commands.length; i++){
        // array의 부분 배열을 복사함
        int [] cutted = Arrays.copyOfRange(array, commands[i][0] - 1, commands[i][1]);
        
        // 복사된 배열을 정렬함
        Arrays.sort(cutted);
        
        // 정렬된 배열에서 k번째 값을 answer에 저장함
        answer[i] = cutted[commands[i][2] - 1];
    }
    return answer;
}
```
### 📌 1-2. 가장 큰 수 만들기

정수 배열 `numbers`가 주어졌을 때, 배열의 수를 조합하여 만들 수 있는 **가장 큰 수**를 문자열로 반환하는 문제이다.

---

#### 📌 핵심 요약:

- 숫자를 **문자열로 변환 후 정렬**하여 이어붙이는 방식으로 가장 큰 수를 만든다.
- 정렬 기준은 `a + b`와 `b + a` 중 어떤 것이 더 큰지를 비교하여 결정한다.
- `0`으로 시작하는 숫자 조합을 처리하기 위해, 결과가 `"0"`으로 시작하면 `"0"`을 반환해야 한다.

---

#### ✅ 개선 코드
```java
public String solution(int[] numbers) {
    String result = Arrays.stream(numbers)
            .mapToObj(String::valueOf)
            // 두 문자열을 합쳐서 큰 수가 되도록 정렬
            .sorted((a, b) -> (b + a).compareTo(a + b))
            .collect(Collectors.joining());

    // 모든 값이 0인 경우 "000..."이 되므로 "0"으로 처리
    return result.startsWith("0") ? "0" : result;
}
```

### 📌 1-3. H-Index

H-Index는 과학자의 생산성과 영향력을 나타내는 지표로, **h편 이상의 논문이 각각 h회 이상 인용된 경우**를 기준으로 한다. 논문 수가 늘어나면, 해당 조건을 만족하는 인용 횟수의 기준도 함께 증가하게 된다.

---

#### 📌 핵심 요약:

- **H-Index**는 인용 횟수가 논문 수를 초과하지 않으면서 가장 큰 값인 `h`를 찾는 문제이다.
- 논문 인용 수를 내림차순 정렬한 뒤, 조건을 만족하는 최대 `h`를 구한다.

---

#### ✅ 코드:
```java
public int solution(int[] citations) {
    // 1) 내림차순 정렬
    int[] sorted_array = Arrays.stream(citations)
                               .boxed()
                               .sorted(Comparator.reverseOrder())
                               .mapToInt(i -> i)
                               .toArray();

    int idx_pointer = 0;
    List<Integer> answer = new ArrayList<>();

    // 2) 조건이 깨지면 반복 중단하면서 h값(i+1)을 리스트에 추가
    while (idx_pointer < sorted_array.length) {
        if (sorted_array[idx_pointer] >= idx_pointer + 1) {
            // (i+1)편의 논문이 인용횟수 조건을 만족하면 h 후보로 추가
            // 출판된 수가 논문 인용수보다 많아야함.
            answer.add(idx_pointer + 1); // 논문 인용수 추가
        } else {
            // 내림차순이기 때문에 이후에는 모두 조건 불만족 → 중단
            break;
        }
        idx_pointer++;
    }

    // 3) 빈 리스트면 0, 아니면 최대 h 반환
    return answer.isEmpty()
         ? 0
         : Collections.max(answer);
}
```

---

#### 🔍 동작 설명:

1. **인용 횟수를 내림차순 정렬**하여 인덱스와 비교한다.
2. 각 인덱스 `i`에 대해 `citations[i] >= i+1` 조건을 만족하면 `h = i+1` 후보로 저장한다.
3. 조건이 깨지는 순간 반복을 중단하고, 지금까지 저장된 `h` 후보 중 **최대값**을 H-Index로 반환한다.

---

##### ⚠️ 주의할 점:

- 내림차순 정렬 후 조건이 깨지면 이후 데이터는 모두 조건을 만족할 수 없으므로 **즉시 중단**해야 한다.
- 후보 리스트가 비어 있을 경우 H-Index는 **0으로 처리**한다.

---

