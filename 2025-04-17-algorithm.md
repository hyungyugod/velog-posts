# 1. 해시
- 해시(Hash)**는 어떤 데이터를 넣으면, 그에 해당하는 **고유한 숫자(또는 인덱스)**를 반환해주는 함수나 구조를 의미함.



#### 📌 해시(Hash)의 가장 좋은 사용법 정리

해시를 잘 쓴다는 것은 단순히 `HashMap`, `HashSet`을 쓰는 것이 아니라,  
**문제를 빠르게 풀 수 있도록 구조화하는 능력**을 의미한다.

---

#### ✅ 해시의 핵심 특성

| 특성            | 설명                                           | 시간복잡도 |
|-----------------|------------------------------------------------|------------|
| 빠른 탐색       | key로 바로 value를 가져올 수 있음              | 평균 O(1)  |
| 중복 방지       | `HashSet`은 중복을 자동으로 제거함             | O(1)       |
| 존재 여부 확인  | `containsKey()`, `contains()`로 즉시 검사 가능 | O(1)       |
| 값 누적/변형    | `Map.merge()`, `getOrDefault()`                | O(1)       |
- 사실 hash set은 hash map으로 씌워진 구조이다. (value 값이 더미객체)
---

### 📌 1-1. 완주하지 못한 선수 (HashMap)

참가자 명단과 완주자 명단이 주어졌을 때, 완주하지 못한 선수를 찾는 문제이다.  
이 문제에서는 **동명이인**이 있을 수 있으므로 이름의 출현 횟수를 정확히 계산해야 한다.

---

#### 📌 문제 해결 전략

- `Map<String, Integer>`를 사용하여 참가자의 이름을 키로, 출현 횟수를 값으로 저장한다.
- 완주자 배열을 순회하면서 참가자 Map에서 이름의 카운트를 하나씩 감소시킨다.
- 카운트가 0이 되면 해당 이름을 Map에서 제거한다.
- 최종적으로 Map에 남은 하나의 키가 **완주하지 못한 선수의 이름**이 된다.

---

#### ✅ 코드 설명
```java
public String solution(String[] participant, String[] completion) {
    Map <String, Integer> partiMap = new HashMap<>();
    
    for (String i : participant){ // 참가자들의 이름을 map에 저장, 동명이인은 카운트함.
        partiMap.put(i, partiMap.getOrDefault(i, 0) + 1);
    }

    for (String i : completion){ // 완주자들의 이름을 map에서 꺼냄, 수가 0이되면 삭제함.
        partiMap.put(i, partiMap.get(i) - 1);
        if (partiMap.get(i) == 0){
            partiMap.remove(i);
        }
    }

    return partiMap.keySet().iterator().next(); // set을 iterater로 만들어서 다음 값(값 원본으로)을 꺼냄.
}
```

---

#### 💡 대안 방식

- 최종적으로 남은 키 값을 꺼내는 방법은 다음과 같은 방식도 가능하다:

```java
map.keySet().stream().findFirst().get();
```

---

#### 📌 핵심 요약:

- **동명이인 처리**를 위해 이름별 등장 횟수를 카운트해야 한다.
- 완주자를 순회하며 Map의 값을 감소시키고, 0이 되면 제거한다.
- 남은 하나의 이름이 완주하지 못한 선수이다.

---

#### ⚠️ 주의할 점:

- `Map.get()` 결과를 바로 감소시키고 나서 `0` 체크 후 `remove()`를 호출하는 순서에 주의해야 한다.
- `iterator().next()` 또는 `stream().findFirst().get()`은 반드시 Map에 값이 하나만 남아있는 상태에서 호출되어야 안전하다.

---

### 📌 1-2. 포켓몬 (HashSet)

포켓몬 종류의 배열이 주어졌을 때, **최대한 다양한 종류의 포켓몬을 선택할 수 있는 수**를 구하는 문제이다.  
선택할 수 있는 포켓몬 수는 배열 길이의 절반(n/2)이며, 이 안에서 **서로 다른 종류의 포켓몬을 최대한 많이 선택**해야 한다.

---

#### 📌 문제 해결 전략

- 전체 포켓몬 수 `N`은 `nums.length`로 계산한다.
- `HashSet`을 사용해 중복 없는 포켓몬 종류의 수를 구한다.
- 선택할 수 있는 최대 포켓몬 수는 `N/2`이므로,  
  포켓몬 종류 수와 `N/2` 중 **작은 값을 반환**하면 된다.

---

#### ✅ 코드 설명
```java
public int solution(int[] nums) {
    int N = nums.length; // 포켓몬의 총 마리수
    Set <Integer> types = new HashSet<>();

    for (int i : nums){ // 배열의 모든 원소를 집합에 넣음.
        types.add(i); 
    }

    return Math.min(N/2, types.size()); // 최대한 많은 종류를 N/2 안에서 선택하기 위해서
}
```

---

#### 📌 핵심 요약:

- 포켓몬 종류 수는 `HashSet`을 이용해 계산한다.
- 선택 가능한 마리 수는 최대 `N/2`이다.
- `Math.min()`을 사용하지 않고 조건문으로 분기해도 되지만, `min()`이 더 간결하다.

---

### 📌 1-3. 전화번호 목록 (HashSet)

전화번호 목록이 주어졌을 때, 이 중 **어떤 번호가 다른 번호의 접두어인지 여부**를 확인하는 문제이다.  
전화번호는 최대 100,000개까지 주어질 수 있어, **단순 이중 반복문으로는 시간 초과**가 발생한다.

---

#### 📌 문제 해결 전략

- 전화번호를 `Set`에 넣으면 `contains()` 메서드를 통해 **접두어 존재 여부를 O(1)**에 확인할 수 있다.
- 각 전화번호에 대해 접두어를 하나씩 잘라가며 검사한다.
- 완전 동일한 번호는 없다고 가정하므로, 마지막 글자 전까지만 접두어로 확인한다.

---

#### ✅ 코드 설명
```java
public boolean solution(String[] phone_book) {
    Set <String> pset = new HashSet<>(Arrays.asList(phone_book)); // Arrays 클래스를 통해 리스트로 바꾼후 set으로 전환

    for (String i : phone_book){
        String prefix = "";
        for (int j = 0; j < i.length()-1; j++){ // 완전 같은 값은 없으므로 그 전까지만 검사
            prefix += i.charAt(j); // 하나씩 잘라서 늘려가면서 contains로 비교
            if (pset.contains(prefix)){
                return false;
            }            
        } 
    }
    return true;
}
```

---

#### 📌 핵심 요약:

- 전화번호 목록을 `HashSet`으로 구성하여 접두사 존재 여부를 빠르게 확인한다.
- 문자열을 하나씩 잘라 접두사를 만들고, 각 접두사를 `contains()`로 검사한다.
- 접두사가 존재하는 경우 `false`를 즉시 반환한다.
- 끝까지 문제없이 탐색을 마치면 `true`를 반환한다.

---

#### ⚠️ 주의할 점:

- 성능을 고려하면 단순 `startsWith()`나 두 중첩 루프는 시간 초과가 발생할 수 있다.
- 전화번호 최대 100,000개, 길이 최대 20으로 가정했을 때  
  접두사 비교 연산은 최대 `100,000 * 20`회 수준으로 효율적이다.
- 접두사 비교는 전체 번호 길이 전까지만 수행해야 하며, 자기 자신과는 비교하지 않아야 한다.

### 📌 1-4. 의상 (hash map)

의상의 종류와 각 의상의 이름이 2차원 배열로 주어질 때,  
**서로 다른 옷 조합의 수를 구하는 문제**이다.  
단, **한 종류의 의상에서 하나만 착용할 수 있고, 아무것도 안 입는 경우는 제외**해야 한다.

---

#### 📌 문제 해결 전략

- 의상의 종류별로 몇 개의 아이템이 있는지 `Map<String, Integer>`로 카운트한다.
- 인수 개수세는 방식처럼, 각 의상 종류마다 `(개수 + 1)`을 곱한다.
  - `+1`은 해당 종류를 **입지 않는 경우**를 고려한 것.
- 모든 곱의 결과에서 `-1`을 빼야 한다.
  - **아무것도 입지 않은 경우**를 제외하기 위함이다.

---

#### ✅ 코드 설명
```java
public int solution(String[][] clothes) {
    Map <String, Integer> counter = new HashMap<>();

    for (String[] i : clothes){
        counter.put(i[1], counter.getOrDefault(i[1], 1) + 1); // 옷의 종류가 나올때마다 개수를 추가, 근데 어짜피 +1해서 곱해야하므로 미리 초기값을 1로 세팅함.
    }
    return counter.values().stream().reduce(1, (a,b) -> a * b) - 1; // reduce로 누적곱을 구해준다. 아예 안입는 경우 -1을 해야함.
}
```

---

#### 📌 핵심 요약:

- 의상 종류별로 (아이템 수 + 1)을 곱해 조합을 계산한다.
- `+1`은 해당 종류를 **입지 않는 경우의 수**를 포함한다.
- 전체 조합 수에서 아무것도 안 입는 경우(`1`)는 제외해야 하므로 `-1`을 수행한다.
- 최종 결과는 `reduce(1, 곱셈)`으로 누적 계산하여 반환한다.

---

#### ⚠️ 주의할 점:

- `counter.getOrDefault(i[1], 1)`로 기본값을 1로 설정하는 이유는  
  최종적으로 +1을 해줄 수 있게 미리 1에서 시작하도록 설정하기 위함이다.
- 옷이 여러 종류가 없는 경우도 있으므로 최소한 한 종류라도 있어야 조합이 의미가 있다.
- `reduce()`를 사용할 경우 초기값 `1`을 주어야 올바른 곱셈 누적이 된다.

### 📌 1-5. 베스트 앨범

음악 스트리밍 서비스에서 베스트 앨범을 만들기 위한 로직 설계 문제이다.  
다음 조건을 만족하는 **고유번호 인덱스 배열**을 출력해야 한다:

- 장르별 총 재생 수를 기준으로 정렬
- 각 장르별로 **재생 수가 가장 높은 2곡**까지 수록 (단, 같은 수라면 고유번호가 낮은 곡 우선)

---

#### 📌 문제 해결 전략

1. **장르별 총 재생 수 계산** (`Map<String, Integer>`)
2. **장르별 곡 정보 저장** (`Map<String, List<Song>>`)
3. 장르를 **총 재생 수 기준으로 정렬**
4. 정렬된 장르마다 곡을 **재생 수 기준으로 정렬**하고 상위 2개 선택
5. 고유번호를 `List<Integer>`에 저장 후 `int[]`로 반환

---

#### ✅ 코드 설명
```java
class Song { // 음악 정보 저장 (인덱스(고유번호), 음악 재생 수)
    int idx;
    int play;

    Song(int idx, int play){
        this.idx = idx;
        this.play = play;
    }
}

public int[] solution(String[] genres, int[] plays) {
    Map <String, Integer> genreTotalMap = new HashMap<>(); // 장르 - 장르별 곡 수 합 //정렬 기준 1
    Map <String, List<Song>> genreSongMap = new HashMap<>(); // 장르 - 음악(인덱스, 재생수)정보 // 정렬기준 2
    List <Integer> answer = new ArrayList<>(); // 정답을 담을 리스트 생성

    // 1. 장르별 총 재생 수와 곡 목록 구성
    for (int i = 0; i < genres.length; i++){
        String genre = genres[i]; // 두번 이상 사용될 변수들은 그냥 미리 선언하고 가면 편하다.
        int play = plays[i];

        genreTotalMap.put(genre, genreTotalMap.getOrDefault(genre, 0) + play); // genreTotalMap에 정보저장
        
        genreSongMap.putIfAbsent(genre, new ArrayList<>()); // 장르와 연결된 리스트 생성 (여기에 곡들을 최대 2개까지 담을 거)
        // 이미 리스트가 존재하면 두고 아니면 만듦
        genreSongMap.get(genre).add(new Song(i, play)); // 리스트에 첫번째 곡을 추가
    }

    // 2. 장르별 재생 수로 장르 정렬
    List<String> sortedGenres = new ArrayList<>(genreTotalMap.keySet()); // keyset은 컬렉션이니까 이렇게 넣어서 리스트로 만듦.
    sortedGenres.sort((a,b) -> genreTotalMap.get(b) - genreTotalMap.get(a)); // 플레이수가 큰 순서대로 장르를 내림차순으로 정렬함.

    // 3. 장르별로 곡 정렬 (재생 수 내림차순 정렬 후 2개까지 선택) - 위에서 정렬한 순서대로 두번째 맵을 순회
    for (String genre : sortedGenres){ // 장르를 순서대로 꺼냄 -> 장르랑 매칭되어있는 노래를 찾기 위하여
        List<Song> tmpSonglList = genreSongMap.get(genre); // 장르별 음악 리스트 이름을 보기 쉽게 재정의함.
        
        tmpSonglList.sort((a,b) -> b.play - a.play); // 재생 수를 기준으로 내림차순 정리 -> 정렬된 채로 저장

        for (int i = 0; i < Math.min(2, tmpSonglList.size()); i++){ // 최대 2개까지만 꺼내서 답에 입력
            answer.add(tmpSonglList.get(i).idx); // song 객체의 idx를 답에 순서대로 넣음.
        }
    }

    return answer.stream().mapToInt(i -> i).toArray();
}
```

---

#### 📌 핵심 요약:

- `genreTotalMap`: 장르별 총 재생 수를 저장하여 **장르 정렬 기준**으로 활용
- `genreSongMap`: 각 장르에 해당하는 곡 리스트를 저장하고 **내부 정렬 기준**으로 활용
- 각 장르별로 최대 **2곡만 선택**하여 정답 리스트에 추가
- 최종 결과는 `List<Integer>` → `int[]`로 변환하여 반환

---

#### ⚠️ 주의할 점:

- `genreSongMap.putIfAbsent()`를 통해 장르별 리스트가 없으면 생성하는 방식이 깔끔하고 안전하다.
- 곡 정렬 시 재생 수가 같다면 `idx` 비교가 필요할 수도 있으므로 주의 (현재 문제 조건에서는 재생 수만 고려)
- `Math.min(2, size)`를 사용하여 곡이 2곡 미만일 때도 안정적으로 작동하도록 처리한다.

























