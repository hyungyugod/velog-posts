# 📌 1. 자바스크립트 코딩테스트
### 📌 1-1. 배열 만들기 3
```js
function solution(arr, intervals) {
    return [...arr.slice(intervals[0][0], intervals[0][1] + 1), ...arr.slice(intervals[1][0], intervals[1][1] + 1)];
}
```

### 📌 1-2. 가까운 1 찾기
```js
function solution(arr, idx) {
    let a = arr.slice(idx, arr.length);
    return a.includes(1) ? a.indexOf(1) + idx : -1;
}
```

### 📌 1-3. 아이스 아메리카노
```js
function solution(money) {
    return [parseInt(money / 5500), money % 5500];
}
```

### 📌 1-4. 점의 위치 구하기
```js
function solution(dot) {
    if (dot[0] > 0 && dot[1] > 0) return 1;
    else if (dot[0] < 0 && dot[1] > 0) return 2;
    else if (dot[0] < 0 && dot[1] < 0) return 3;    
    else return 4;
}
```

### 📌 1-5. 배열 자르기
```js
function solution(numbers, num1, num2) {
    return numbers.slice(num1, num2 + 1);
}
```

### 📌 1-6. 배열 회전시키기
```js
function solution(numbers, direction) {
    let nl = numbers.length - 1;
    if (direction === "right") return [numbers[nl], ...numbers.slice(0, nl)];
    else return [...numbers.slice(1, nl + 1), numbers[0]];
}
```

### 📌 1-7. 카운트 다운
```js
function solution(start_num, end_num) {
    let answer = [];
    for (let i = start_num; i > end_num - 1; i--) {
        answer.push(i);
    }
    return answer;
}
```

### 📌 1-8. 배열 만들기 1
```js
function solution(n, k) {
    var answer = [];
    for (let i = k; i < n + 1; i += k){
        answer.push(i);
    }
    return answer;
}
```

### 📌 1-9. 접두사인지 확인하기
```js
function solution(my_string, is_prefix) { 
    return my_string.startsWith(is_prefix) ? 1:0;
}
```

# 📌 2. JSON(JavaScript Object Notation), Object Literal
- 데이터를 저장하거나 교환하기 위한 텍스트 형식
- 자바스크립트 객체: 데이터를 다루기 위한 실제 객체 구조
- 자바스크립트에서 **객체(Object)**를 표현하는 방식(Object Literal)과 매우 비슷해서 이렇게 이름이 붙음.
- "리터럴(literal)"이란 프로그래밍에서 그 자체로 값을 의미하는 코드 조각을 의미한다.
- Json은 키와 문자열은 항상 큰따옴표(") 사용하고 함수, 주석, 변수 등은 사용할 수 없으며 순수 데이터만 저장한다. 또한 텍스트이니까 직접 실행할 수 없다. 
- 즉 JSON의 type 형태는 기본적으로 string이다.
- 자바스크립트 객체: 큰따옴표 없이 키로 사용 가능하고 함수, 주석, 변수 등 자바스크립트 문법 사용 가능하며 동적으로 값을 변경하거나 호출 가능
- 하여 객체 리터럴(Object Literal)에 익명 함수나 함수가 포함되어 있다면 그 객체는 JSON으로 변환할 수 없다. 하지만 JSON.stringify()로 변환은 되는데 그 과정에서 해당 속성은 삭제된다.
- JSON.parse()를 통해 json을 자바스크립트 객체로 변환할 수 있다.
- JSON.stringify()를 통해 자바스크립트 객체를 json으로 변경할 수 있다.
- "string + ify" → 문자열로 변환하다, 문자열화하다"
- 관습적으로는 json object라고들 논문에서 많이 쓰는데 정확한 의미는 아니다.
- object literal은 자바스크립트 엔진이 키값을 자동으로 파싱해주므로 굳이 문자열임을 따옴표로 명시하지 않아도 된다. 다만 띄어쓰기나 특수문자가 있는 경우에는 문자열로 둘러싸야만 한다.

### 📌 2-1. Object Literal의 탐색
- Object Literal을 탐색할때는 for in을 사용한다.
```js
const student = {
    studno: 10101,
    grade: 1,
    name: "학생1",
    phoneno: "010-1231-2342"
};

for (const key in student) {
    console.log(`${key}: ${student[key]}`);
}
```
- object literal이 인덱스로 탐색 가능해보이는 경우는 배열로 감쌌기때문에 배열의 object literal에서 문자열로된 숫자 키값이 인덱스로 할당되기 때문이다.
```js
const students = {
  name: ['철수', '민수', '호영'],
  age: [16, 17, 19],
  height: [172.4, 168.2, 170.5]
}

for (let i = 0; i < students.name.length; i++) {
  console.log(`이름: ${students.name[i]}, 나이: ${students.age[i]}, 키: ${students.height[i]}`);
}
```

### 📌 2-2. Object Literal 구조분해
- 구조분해 할때는 키값을 정확히 명시해 주어야한다. 
- 배열에서 구조분해가 가능한 이유는, 배열이 객체이며, 자동 부여된 숫자 인덱스를 키로 갖고, 구조분해는 그 순서(위치)를 따라가기 때문이다.
```js
// 구조분해를 수행한 나머지를 별도로 분리하기
const dummy = { a1: 100, a2: 200, a3: 300, a4: 400 };
const {a1, a2, ...rest_b} = dummy;

// 구조분해를 활용하여 기존 데이터와 추가적인 값을 병합한 새로운 객체 생성
// --> `...` 뒤에 오는 변수명은 반드시 원본 객체 이름이어야 한다.
const origin = {name: 'javascript', age: 25};
const newdata1 = {...origin, gender: 'M'};
console.log(newdata1);

// 구조분해를 통한 새로운 데이터 생성시 원본과 동일한 이름의 속성이 있다면 원본 데이터를 수정한다.
const newdata2 = {...origin,
                  age: 30, gender: 'F'};
console.log(newdata2);
```

### 📌 2-3. map과 js object의 차이
- map은키 타입에 정말 아무거나 와도 된다.
- map 그 자체로 iterable하다 즉 js object 처럼 for in 같은 특수한 문법을 사용하지 않아도 된다.

### 📌 2-4. java 메모리와 javascript 메모리
#### heap과 stack 메모리
- "스택에는 힙에 있는 데이터를 가리키는 참조(reference)가 저장되고, 실제 데이터는 힙에 있음. 실행 중에 이 참조를 이용해 힙에 접근해서 사용한다."
- 하여 일반적으로 전역변수는 힙에 객체의 속성이나 객체 내부의 인스턴스 변수 형태로 저장되고 지역 변수는 잠깐 사용하는 것이므로 스택에 저장된다.
- Object.prototype은 자바스크립트 엔진이 실행될 때, 힙(Heap) 메모리에 자동으로 생성된다.

| 항목             | **Stack (스택)**        | **Heap (힙)**                     |
| -------------- | --------------------- | -------------------------------- |
| 📌 **역할**      | 함수 호출, 지역 변수 저장       | 객체나 동적 메모리 저장                    |
| 🔄 **할당 방식**   | 자동 (함수 호출 시 자동 생성/소멸) | 수동 또는 동적 (new, malloc 등으로 직접 할당) |
| 🧹 **해제 방식**   | 자동 (함수 끝나면 소멸)        | 개발자 또는 가비지 컬렉터가 해제               |
| 📏 **메모리 크기**  | 작고 빠름                 | 크고 유연함                           |
| 📈 **속도**      | 매우 빠름 (LIFO 구조)       | 상대적으로 느림 (복잡한 접근)                |
| 🔒 **스레드 안전성** | 스레드별로 분리되어 있어 안전      | 스레드 간 공유되므로 동기화 필요               |
| 🧠 **저장 대상**   | 원시값, 지역 변수, 함수 스택 프레임 | 객체, 배열, 참조형 데이터                  |
| 💥 **오류 예시**   | Stack Overflow        | Memory Leak                      |


#### java 메모리
- 참조가 내부적으로 포인터 문법으로 구현되어있다.

| 메모리 영역             | 주 용도                      |
| ------------------ | ------------------------- |
| 🟦 **Heap**        | 객체(instance), 인스턴스 변수 저장  |
| 🟨 **Stack**       | 지역 변수, 매개변수, 메서드 호출 정보 저장 |
| 🟥 **Method Area** | 클래스 정의 정보, static 변수 저장   |

- 배열의 경우 아래와 같이 발전하였다. c언어 코드는 int 타입의 메모리 공간을 8칸 할당하라는 뜻이다.
```c
int *C = malloc(8);
```
```java
int[] arr = new int[3];
```
- 이때 arr는 참조 변수 (포인터처럼 작동) → 스택에 저장한다. 그렇다면 아래와 같다.

| 구성 요소         | 저장 위치                                 | 설명                                    |
| ------------- | ------------------------------------- | ------------------------------------- |
| `arr` (참조 변수) | 🟨 **Stack**, 또는 🟥 **Heap (필드일 경우)** | `arr`는 단지 "힙에 있는 배열 객체의 주소"를 저장하는 변수  |
| `new int[3]`  | 🟦 **Heap**                           | 배열 객체(실제 데이터 저장 공간 + 길이 정보 등)는 힙에 생성됨 |


#### javascript 메모리
- const는 참조값이 고정된 구조라 자유롭게 내부 값은 바꿀 수 있다.

| 메모리 영역         | 설명                                                 |
| -------------- | -------------------------------------------------- |
| **Stack (스택)** | 원시값(primitive value), 함수 호출 정보, 지역 변수 저장           |
| **Heap (힙)**   | 객체(Object), 배열(Array), 함수(Function) 등 **참조형 값** 저장 |

- 배열에 관하여 

Java 배열:
→ new로 생성됨, 고정된 타입과 크기, 힙 메모리에 연속적으로 저장됨

JavaScript 배열:
→ 사실상 "특수한 객체", 타입도 크기도 자유롭고, 내부 구조는 유연함

# 📌 3. 여러가지 global, window객체의 메서드들
### 📌 3-1. setTimeout
- 특정함수를 받아 콜백함수로 작동하도록 한다. 1/1000초 이후에 작동한다.
```js
function foo() {
    for (let i = 1; i < 10; i++) {
        console.log(i);
    }
}

setTimeout(foo, 3000);
console.log("구구단을 외자");
```
- 일반적으로는 함수를 변수를 통해 넘기지 않고 내부에서 직접 선언하여 넘긴다.
```js
setTimeout(() => {
    for (let i = 1; i < 10; i++) {
        console.log(i);
    }
}, 3000);
console.log("구구단을 외자");
```

### 📌 3-2. setInterval 
- 특정 초마다 해당 함수를 반복시킴
- clearInterval로 반복돌고 있는 함수를 다시 가리켜 주면서 반복을 종료시킬 수 있음.
```js
let count1 = 0;
const timerId1 = setInterval(() => {
    count1++
    console.log(count1);

    if (count1 === 5) clearInterval(timerId1);
}, 3000);
```

### 📌 3-3. js에서 정규표현식
- js에서 정규표현식은 // 사이에 넣는다.
- 정규표현식 객체에 내장되어 있는 test 메서드를 통해 주어진 문자열이 정규표현식에 해당하는지 검사할 수 있다.
- 정규표현식에서 *는 **"앞에 있는 문자나 그룹을 0번 이상 반복"**이라는 뜻이다.
- 이에 반해 +는 1번 이상 반복이다.
- *과 +는 비어있는 문자열을 허용하느냐 마냐의 차이이다.
```js
let username = "성현규";
const pattern1 = /^[ㄱ-ㅎ가-힣]*$/;
if (pattern1.test(username)) console.log('제대로 입력하셨습니다 !');
```

### 📌 3-4. 날짜처리 메서드들
```js
/** 요일의 이름을 저장하고 있는 배열의 생성 */
const days = ['일', '월', '화', '수', '목', '금', '토'];

/** 객체의 생성 */
const date1 = new Date();
console.log(date1.toLocaleString());

/** 년,월,일,시간,분,초를 리턴받기 */
const yy = date1.getFullYear();          // 월은 0이 1월, 11이 12월을 의미한다.
const mm = date1.getMonth() + 1;
const dd = date1.getDate();

// 0=일요일~6=토요일의 값이 리턴된다.
const i = date1.getDay();
const day = days[i];

const hh = date1.getHours();
const mi = date1.getMinutes();
const ss = date1.getSeconds();

var result = yy + '-' + mm + '-' + dd + ' ' + day + '요일 ' + hh + ':' + mi + ':' + ss;
console.log(result);

/** 특정 날짜를 의미하는 객체 생성 */
// 시간이 없으므로 자정으로 설정된다.
var date2 = new Date(2021, 9, 5);
console.log(date2.toLocaleString());

/** 특정 시점을 의미하는 객체 생성 */
var date3 = new Date(2021, 9, 5, 21, 19, 31);
console.log(date3.toLocaleString());

/** 이미 생성된 날짜 객체의 성분 변경 */
date3.setYear(2010);
date3.setMonth(1);    // 0부터 시작하므로 2월을 위해서는 1로 설정한다.
date3.setDate(14);
date3.setHours(12);
date3.setMinutes(16);
date3.setSeconds(30);
console.log(date3.toLocaleString());
```


