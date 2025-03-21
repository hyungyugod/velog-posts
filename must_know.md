# 0-1. Integer, Math, Util 클래스
### 0-1-1. Integer 클래스 → 기본형 int를 객체로 다루기 위한 클래스 (Wrapper Class: 기본형을 객체로)
- Integer.parseInt(String s): 문자열을 int로 변환
- Integer.valueOf(String s): 문자열을 Integer 객체로 변환
- Integer.toString(int i): 정수를 문자열로 변환
- Integer.compare(int a, int b): 두 정수를 비교 (a - b와 같은 효과), 크기를 판별해서 1, 0, -1 반환
- Integer.bitCount(int i): i의 이진수에서 1의 개수 반환
- Integer.toBinaryString(int i): 정수를 2진수 문자열로 변환

### 0-1-2. Math 클래스 → 수학 연산(절댓값, 거듭제곱, 반올림 등)을 수행하는 클래스
- Math.abs(int a): 절댓값 반환
- Math.max(int a, int b): 두 값 중 큰 값 반환
- Math.min(int a, int b): 두 값 중 작은 값 반환
- Math.pow(double a, double b): a의 b제곱 반환 (a^b)
- Math.sqrt(double a): 제곱근 반환 (√a)
- Math.round(double a): 반올림
- Math.ceil(double a): 올림
- Math.floor(double a): 내림

### 0-1-3. Util 클래스 -> java.util 패키지는 Java에서 가장 많이 사용되는 유틸리티 클래스를 제공하며, 데이터 구조, 날짜 처리, 난수 생성, 입력 처리 등에 필수적임.
- ArrayList, LinkedList: 동적 배열 및 연결 리스트
- HashSet, TreeSet:	중복을 허용하지 않는 집합 자료구조
- HashMap, TreeMap: 키-값 저장을 위한 Map 자료구조
- Collections: 컬렉션 관련 정렬, 검색, 동기화 지원
- Arrays: 배열 관련 유틸리티 (정렬, 검색 등)
- Random: 난수 생성
- Scanner: 사용자 입력 처리
- Date, Calendar, LocalDateTime: 날짜 및 시간 처리
- Timer, TimerTask: 스케줄링 작업 수행
- Formatter: 문자열 포맷팅

#### 1) Collections 클래스
- 리스트를 다루는 유틸리티이다.
- Collections.sort(list): 오름차순 정렬
- Collections.sort(list, Collections.reverseOrder()): 내림차순 정렬
- Collections.max(): 리스트에서 최댓값
- Collections.min(): 리스트에서 최솟값

#### 2) Arrays 클래스
- 배열을 다루는 유틸리트 클래스이다.
- Arrays.sort(): 배열 정렬
- Arrays.asList(): 배열을 리스트로 전환 (안에 원소를 넣으면 그걸 리스트로 감싸는 것것)
- Arrays.copyOf(): 원하는 배열을 원하는 길이만큼 복사한다.
- Arrays.copyOfRange(num_list, 0, n);
- Arrays.toString(): 배열을 문자열로 반환 (안을 바꾸려면 for돌면서 일일히 바꿔야함.)
- Arrays.stream(): 배열을 stream으로 바꾼다.
- Arrays.compare(date1, date2): date1 = {2023, 12, 31};이런 배열 2개를 비교해서 앞에게 더 크면 1, 같으면 0, 작으면 -1 반환

#### 0-1-4. java에서의 len()
- len(list): list.size() (ArrayList 등 컬렉션)
- len(array): array.length (배열)
- len(string): string.length() (문자열)

#### 0-1-5. ArrayList에서 자주 사용하는 매서드들
- List<String> list = new ArrayList<>(): 빈 리스트 생성
- List<Integer> numbers = new ArrayList<>(): 정수 리스트 생성
- add(E e): 리스트 끝에 요소 추가
- add(int index, E e): 특정 위치에 요소 삽입
- remove(Object o): 특정 값 삭제
- remove(int index): 특정 인덱스 요소 삭제
- contains(Object o): 특정 값 포함 여부 확인
- size(): 리스트 크기 확인
- get(int index): 특정 위치 요소 가져오기
- set(int index, E e): 특정 위치 요소 변경
- isEmpty(): 리스트가 비어 있는지 확인
- clear(): 리스트 초기화
- sort(Comparator c): 리스트 정렬
- toArray(): 리스트를 배열로 변환 -> answer.toArray(new String[0]), toArray(new Integer[0]) 사용
- for-each: 리스트 요소 순회 (for (E e : list) {})
- 
# 2. 문자열에서 자주 사용하는 매서드들
- length(): 문자열의 길이(문자 개수)를 반환
- charAt(i): 특정 위치(i)의 문자 반환
- substring(a, b): 슬라이싱
- equals(): 문자열 내용이 같은지 비교 (대소문자 구분 O)
- compareTo(): 설명: 문자열을 사전순으로 비교 (같으면 0, 앞이 작으면 음수, 크면 양수)
- indexOf(): 특정 문자 또는 문자열이 처음 등장하는 위치 반환
- contains(): 문자열 포함 여부 확인
- startsWith(): 문자열이 특정 접두사로 시작하는지 확인
- endsWith(): 문자열이 특정 접미사로 끝나는지 확인
- replace(): 특정 문자열을 다른 문자열로 변경
- trim(): 문자열 양쪽 공백 제거
- split(): 특정 구분자로 문자열 나누기 (배열 반환)
- + 연산자: 문자열 간단하게 연결
- StringBuilder.append(): 성능이 좋은 문자열 연결 (String보다 빠름)
- matches("[0-9]+"): 정규식을 활용하여 숫자로만 이루어진 문자열인지 확인
- String.valueOf(): char를 String으로 변환
- String.join("", arr): 문자열 배열안의 요소를 ""로 합친 문자열을 반환

### 3. 정규표현식 활용
- 아래 함수에 정규표현식을 쌍따옴표로 감싸서 수행한다.
- matches(): 문자열이 특정 패턴과 일치하는지 확인
- replaceAll(): 특정 패턴을 다른 문자열로 변환
- split(): 특정 패턴으로 문자열 나누기
- \\d+: 숫자(0~9)만 포함
- \\w+:	영어, 숫자 포함 (단어)
- [a-zA-Z]+: 영어 대소문자만
- [^a-zA-Z]: 영어가 아닌 문자 찾기
- https?://\\S+: 	HTTP/HTTPS 링크 찾기
- \\d{2,4}:	2~4자리 숫자 찾기
- \\b\\w{3}\\b:	정확히 3글자 단어 찾기

### 4. StringBuilder result = new StringBuilder();에 대하여
#### new StringBuilder();
- 새로운 StringBuilder 객체를 생성. (String과 같은 또 다른 객체이다.)
- 내부적으로 길이 16인 char[] 버퍼 할당. (버퍼란 임시 메모리를 뜻하며 여기선 문자열을 저장하는 내부 배열을 의미)
- ()안에 숫자를 넣어서 버퍼의 사이즈를 재할당할 수 있다.

#### 매서드들
- append(String s):	문자열 추가 -> sb.append("Java")
- insert(int index, String s): 특정 위치에 삽입 -> sb.insert(2, "Hello")
- replace(int start, int end, String s): 부분 문자열 교체 -> sb.replace(1, 4, "ABC")
- delete(int start, int end): 특정 범위 문자 삭제 -> sb.delete(2, 5)
- deleteCharAt(int index): 특정 위치 문자 삭제 -> sb.deleteCharAt(3)
- reverse(): 문자열 뒤집기 -> sb.reverse()
- length():	문자열 길이 반환 -> sb.length()
- charAt(int index): 특정 위치 문자 반환 -> sb.charAt(0)
- setCharAt(int index, char ch): 특정 문자 변경 -> sb.setCharAt(2, 'X')
- substring(int start, int end): 부분 문자열 반환 -> sb.substring(1, 4)
- toString():	String 변환 -> sb.toString()

### 5. BigInterger
- add(BigInteger val): 덧셈	
- subtract(BigInteger val): 뺄셈	
- multiply(BigInteger val): 곱셈	
- divide(BigInteger val): 나눗셈 (몫)	
- mod(BigInteger val): 나머지 연산	
- pow(int exponent): 거듭제곱	
- gcd(BigInteger val): 최대공약수(GCD)	
- isProbablePrime(int certainty): 소수 판별	
- compareTo(BigInteger val): 값 비교 (-1, 0, 1 반환)	
- equals(Object x): 값이 같은지 비교
- abs(): 절댓값 반환
- negate(): 부호 반전 (음수/양수 변환)
- toString(): 문자열 변환
- valueOf(long val): long 값을 BigInteger로 변환	

### 6. 유클리드 호제법
- 이를 통하여 최대공약수를 구하고 두수곱 / 최대 공약수로 최소공배수를 구한다.
```java
public static int gcd(int a, int b) {
        if (b == 0) return a;  // 종료 조건
        return gcd(b, a % b);   // 유클리드 호제법
    }
```

### 7. stream
- 스트림(Stream) = 데이터의 흐름을 처리하는 추상적 개념의 객체이며 데이터를 직접 저장하는 것이 아니라, 데이터를 처리하는 역할이다.
- List, Set 같은 컬렉션에서 .stream()을 호출하면 Stream<T> 객체가 생성된다. 1회 사용 후 닫히며, 다시 사용하려면 새 스트림을 생성해야 함.
- Stream<T>: 객체 스트림 -> Stream<String>, Stream<Integer>
- IntStream: 기본형 int 스트림 -> IntStream.of(1, 2, 3)
- LongStream: 기본형 long 스트림 -> LongStream.of(100L, 200L)
- DoubleStream: 기본형 double 스트림
-  Stream<String> stream = Stream.of("Apple", "Banana", "Cherry"): 여러 요소로 스트림 생성
- 배열을 스트림으로 변환: Stream<String> stream = Arrays.stream(fruits):

- 그냥 중간에  Arrays.stream(fruits)이렇게 변환하고 다시 .toArray로 배열로 바꿔도됨.

- 컬렉션을 스트림으로 변환: List<String> fruitList = Arrays.asList("Apple", "Banana", "Cherry");
- 객체 스트림에서 기본형 스트림으로 변환: stream.mapToInt(Integer::intValue);
- 기본형 스트림을 객체 스트림으로 변환: Stream<Integer> stream = intStream.boxed();

#### 공통 매서드
- filter(Predicate<T>): 특정 조건을 만족하는 요소만 선택 -> stream.filter(s -> s.startsWith("A")), intStream.filter(i -> i % 2 == 0)
- map(Function<T, R>): 요소 변환 (데이터 가공) -> stream.map(String::toUpperCase), intStream.map(i -> i * 2)
- **sorted(): 요소 정렬 -> stream.sorted(), intStream.sorted()**
- distinct(): 중복 제거 -> stream.distinct(), intStream.distinct()
- limit(long maxSize): 지정된 개수만큼 제한 -> stream.limit(3), intStream.limit(3)
- count(): 요소 개수 반환 -> stream.count(), intStream.count()
- anyMatch: Arrays.stream(num_list).anyMatch(num -> num == n);

#### stream<T> 전용 매서드
- mapToInt(ToIntFunction<T>): Stream<T> → IntStream 변환, stream.mapToInt(String::length)
- mapToLong(ToLongFunction<T>): Stream<T> → LongStream 변환, stream.mapToLong(s -> s.length())
- mapToDouble(ToDoubleFunction<T>): Stream<T> → DoubleStream 변환 -> stream.mapToDouble(s -> s.length() * 1.5)
- **collect(Collectors.toList()): 스트림을 리스트로 변환 -> stream.collect(Collectors.toList())**
- reduce(BinaryOperator<T>): 스트림의 요소를 하나로 줄이기 -> stream.reduce((s1, s2) -> s1 + s2)
- toArray(): 스트림을 배열로 변환 -> stream.toArray(String[]::new)

#### IntStram 전용 매서드
- sum(): 합계 계산 -> intStream.sum()
- average(): 평균 계산 -> intStream.average().orElse(0.0)
- max(): 최댓값 반환 -> intStream.max().orElse(-1)
- min(): 최솟값 반환 -> intStream.min().orElse(-1)

- mapToObj(IntFunction<R>): IntStream → Stream<T> 변환 -> intStream.mapToObj(String::valueOf)
- mapToLong(IntToLongFunction): IntStream → LongStream 변환 -> intStream.mapToLong(i -> i * 10L)
- mapToDouble(IntToDoubleFunction): IntStream → DoubleStream 변환 -> intStream.mapToDouble(i -> i * 1.5)
- boxed(): IntStream → Stream<Integer> 변환 -> intStream.boxed()
- range(int start, int end): start ~ end-1 범위 생성 -> IntStream.range(1, 10)
- rangeClosed(int start, int end): start ~ end 범위 생성 -> IntStream.rangeClosed(1, 10)


- **integer리스트를 int리스트로 만들기 - answer.stream().mapToInt(Integer::intValue).toArray()**
- **배열에서 stream생성 = Arrays.stream(배열)**
- **컬렉션에서 stream생성 = 컬렉션.stream()** -> 더 쉽다.
- 정수 리스트 -> 배열 x , 정수 리스트 -> 정수 스트림-> 배열
- 문자열 배열 -> 문자열 가능, Arrays.toString(array)으로
- 문자열 리스트 -> 배열: answer.toArray(new String[0]);
- Integer 배열 -> int 배열 x, Integer 배열 -> 정수스트림 -> int 배열 
- Arrays.stream(integerArray).mapToInt(Integer::intValue).toArray();
- **정수 배열 정렬해서 다른데 갖다 쓰려하면 stream으로 한번 다녀가야함.**
-  String의 chars() 메서드는 문자열을 IntStream(정수 스트림)으로 변환하는 역할을 한다.

### 8. 에라토스테네스의 체 (소수판별)
```java
public static boolean[] sieve(int n) {
    boolean[] isPrime = new boolean[n + 1]; // 0부터 해야 깔끔하기 때문
    Arrays.fill(isPrime, true);
    isPrime[0] = isPrime[1] = false;
    
    for (int i = 2; i * i <= n; i++) {
        if (isPrime[i]) {
            for (int j = i * i; j <= n; j += i) { // i보다 작은것과 i를 곱한 것은 앞에서 미리 처리했기 때문
                isPrime[j] = false;
            }
        }
    }
    return isPrime;
}
```
