# 📌 1. 자바스크립트 기본 
### 📌 1-0. 자바스크립트는 '클래스 기반'이 아니라 '프로토타입 기반' 언어이다
- 자바스크립트는 객체에 직접 함수를 “속성”으로 넣을 수 있다.
- 아래서 great는 person 객체의 프로퍼티이다.
- 프로퍼티는 객체 안의 각각의 정보 단위 (key: value 형태)이며 속성(프로퍼티가 한글로 속성)이고 벨류 값은 함수와 같은 객체일 수 있다. 프로퍼티는 객체.키값 이나 객체[키값]으로 호출한다.
```javascript
const person = {
  name: "현규",
  greet: function() {
    console.log(`안녕하세요, 저는 ${this.name}입니다.`);
  }
};
```
- 자바와 달리 함수도 객체이기 때문에 변수에 저장할 수 있다.
```javascript
const sayHello = greet; // 함수 자체를 변수에 저장
sayHello();             // 출력: 안녕
```
- 또한 프로퍼티도 추가할 수 있다.
```javascript
function greet() {
  console.log("안녕");
}

greet.lang = "ko";

console.log(greet.lang); // 'ko'
```
- function으로 만든 함수도 결국 Function 생성자의 인스턴스라는 의미이다.
- 또한 Function도 Object에서 상속받은 객체이며, 함수 실행 기능이 추가된 특수 객체이다.
```javascript
const hello = new Function('console.log("hi");');

hello(); // 👉 hi
```

### 📌 1-0-1. 프로토타입체인
- 프로토타입(prototype): 객체가 **상속받을 기준(틀)**이 되는 또 다른 객체
```javascript
function greet() {
  console.log("안녕");
}

console.log(greet.__proto__ === Function.prototype); // true
console.log(Function.prototype.__proto__ === Object.prototype); // true
```
위의 함수도 사실 아래처럼 프로토타입체인으로 구성되어있다.
```javascript
greet → Function.prototype → Object.prototype → null
```
- 프로토타입 객체를 Object.create로 만드는데 const student = Object.create(person)으로 하면 person을 원형으로 student객체를 생성한다. 이는 역시 person의 sayhi 속성(함수)를 호출할 수 있고 추가로 속성을 할당할 수 있다. 
```javascript
const person = {
  sayHi: function () {
    console.log("안녕!");
  }
};

const student = Object.create(person);
student.name = "현규";
```

### 📌 1-0-2. 프로토타입체인 하드웨어
- 함수, 배열, 객체 전부 힙 메모리 블록에 저장되고, 변수는 그 객체가 저장된 **메모리 주소(레퍼런스)**만 가진다.
- 객체는 정적이지 않고 크기가 유동적인 구조라 스택이 아니라 힙(Heap) 영역에 저장됩니다.
- 자바스크립트의 프로토타입 체인은 실제로는 객체 내부의 숨겨진 슬롯([[Prototype]])이 가리키는(포인터) 메모리 주소 체인이며, 이 구조는 힙 메모리에 저장된 객체들을 따라가면서 동적으로 프로퍼티를 탐색하는 메커니즘으로 동작한다.
- 자바스크립트에서 객체는 기본적으로 “키-값 쌍”을 가진 구조체이다.
```javascript
const person = {
  name: "현규",
  age: 25,
};
```
```arduino
┌──────────┬─────────────┐
│  "name"  │ 주소 → "현규" │
│  "age"   │ 주소 →   25   │
└──────────┴─────────────┘
```
- 구조체: 구조체(struct)**는 여러 개의 서로 다른 데이터 타입을 묶어 하나의 사용자 정의 자료형을 만드는 도구이다.
- 포인터: 다른 변수의 메모리 주소를 저장하는 변수
- 이중 포인터: 포인터를 가리키는 포인터

#### 배열과 포인터
0x1000 → 10   (arr[0])
0x1004 → 20   (arr[1])
0x1008 → 30   (arr[2])
- 정수형이 4바이트여서 주소가 4씩 증가
- int *p = arr; 일때 p는 0x1000을 가리키고, p + 1은 0x1004를 가리킴

### 📌 1-1. 동적언어
- 자바스크립트는 자바와 다르게 컴파일할때 중간에 저장을 안하고 인터프리터를 통해 그때그때 해석을 해서 실행한다.
- 실행파일이라는 것이 따로 없고 직접 소스 코드를 입력하여 실행을 해야한다. 컴파일을 안해도 된다.
- 동적 언어에서는 컴파일 시점에 타입을 검사하지 않기 때문에 실행 중에 타입 오류가 발생할 수 있다. -> 타입을 명확히 할 수 있는 패턴을 사용하거나 일일히 프로그램에서 타입을 검사하는 코드를 짜 넣어야 한다.
- 컴파일과 객체 생성 시점: class Dog {} 이 선언되는 순간 메모리에 올라가고 new Dog() 하는 시점에 바로 객체가 생성돼요.
- 순서대로 실행되기 때문에 정의되기 전에 호출하면 오류가 난다.
- 또 일반적으로 javascript 자체만으로는 실행하기 전에 오류를 알 수 없다. -> vs code 등이 영리하게 도와주는 것이다.

### 📌 1-2. 실행
- 보통 html 파일 내부에서 실행되며 웹브라우저가 해석기 역할을 한다.
- 그룹화된 로그는 들여쓰기가 적용된다.
- 세미콜론으로 명령어 단위를 구분한다.
- alert는 괄호안의 내용을 메세지 박스로 표시하는 명령어이다.
- 요즘은 type="text/javascript 는 굳이 안써도 된다. (4버전까지만 유효하던것)
```html
<script type="text/javascript">
        alert("안녕, 자바스크립트");
</script>
```
- 위 처럼 쓰거나
```html
<script src="my_script.js"></script>
```
로 쓰고 js 파일을 만들어서 
```javascript
alert("안녕 자바스크립트 !")
```
를 라이브 서버로 실행시켜도 작동이 된다.
```javascript
console.log("hello javascript !");
console.log("안녕, 자바스크립트 !");
```
- 위를 방금의 html에 참조하여 실행하면 f12의 콘솔 영역에 해당 내용이 표시된다.
- 혹은 해당 파일이 있는 폴더에 직접 들어가서 cmd에 node console.js를 입력하면 명령프롬프트로도 실행이 가능하다. alert 파일을 이와 같이 실행시키면 함수가 정의가 안되어있다고 나오는데 이는 브라우저에만 window.alert()라는 함수가 내장돼 있기 때문이다.

### 📌 1-3. console.group.js
- 출력 메세지를 그룹으로 묶어서 출력할 수 있다.
- ctrl + alt + N으로 code ruuner를 통해 실행한다.
```javascript
// 첫번째 그룹
console.group("my group1");
console.log("hello javascript");
console.log("안녕, 자바스크립트!");
console.groupEnd();

// 두번째 그룹
console.group("my group2");
console.log("hello javascript");
console.log("안녕, 자바스크립트!");
console.groupEnd();
```

# 📌 2. 변수와 연산자
- let은 지역변수, var는 전역변수를 의미한다.
- const를 통한 상수의 개념이 있는데 한번 선언, 할당하면 바꿀 수 없다.
- 정수와 실수를 모두 number로 퉁친다. 알아서 실수와 정수 분리
- 자바스크립트는 null을 객체로 분류한다. (진짜 객체는 아니지만 실수로 이렇게 설계함)
- 선언 후 할당을 안하면 undefined이고(와 연산시 nan이 출력된다.(not a number)) string, number, boolean을 제외하면 전부 객체이다.
- `${표현식}` 이렇게 역따옴표로 묶으면 변수를 바로 넣어서 문자열 포멧팅을 할 수 있다.
- typeof로 데이터 타입을 검사할 수 있다.
- 정수 나눗셈 했을때 답이 무한 소수로 나오면 반올림했을때 영향이 없을 수로 어느 순간 오차를 발생시킨다.
- ==, !=은 데이터 타입에 상관없이 내용이 동일하면 true로 판정한다.
- ===, !==은 데이터 타입까지 내용이 동일해야 true로 판정한다.
```javascript
/** 1) 변수 선언과 할당 (분리) */
console.group("변수 선언과 할당 (분리)");
let myName;
myName = "Alice";
console.log("myName:", myName);
console.groupEnd();

/** 2) 변수 선언과 할당 (일괄 처리) */
console.group("변수 선언과 할당 (일괄 처리)");
let myAge = 25;
console.log("myAge: %d", myAge);
console.groupEnd();
```
- 아래는 데이터 타입 확인과 표현식으로 문자열 포멧팅이다.
```javascript
/** 1) 데이터 타입 */
let str = "text";
let num = 100;
let bool = false;
let undef;
let nul = null;
let arr = [1, 2, 3];
let obj = { key: "value" };

// console.group("데이터 타입");
console.log(`string: ${str}`);
console.log(`number: ${num}`);
console.log(`boolean: ${bool}`);
console.log(`undefined: ${undef}`);
console.log(`null: ${nul}`);
console.log(`array: ${arr}`);
console.log(`object: ${obj}`);
// console.groupEnd();

/** 2) typeof 연산자 */
// console.group("typeof 연산자");
console.log("typeof str:", typeof str);
console.log("typeof num:", typeof num);
console.log("typeof bool:", typeof bool);
console.log("typeof undef:", typeof undef);
console.log("typeof nul:", typeof nul);
console.log("typeof arr:", typeof arr);
console.log("typeof obj:", typeof obj);
// console.groupEnd();
```

```javascript
// 변수 초기화
let x = 1;
let y = 2;

// 결과값을 다른 변수에 저장 후 출력하는 경우
let a = x === y;
let b = x !== y;
console.log("x === y -> %s", a);
console.log("x !== y -> %s", b);

// 직접 출력하는 경우
console.log(x < y);
console.log(x <= y);
console.log(x > y);
console.log(x >= y);
```

# 📌 3. javascript 코딩테스트
### 📌 3-1. 나머지 구하기
```javascript
function solution(num1, num2) {
    return num1 % num2;
}
```

### 📌 3-2. 두 수의 합
```javascript
function solution(num1, num2) {
    return num1 + num2;
}
```

### 📌 3-3. 두 수의 차
```javascript
function solution(num1, num2) {
    return num1 - num2;
}
```

### 3-4. 두 수의 곱
```javascript
function solution(num1, num2) {
    return num1 * num2;
}
```

### 📌 3-5. 몫 구하기
```javascript
function solution(num1, num2) {
    return Math.floor(num1 / num2);
}
```

### 📌 3-6. 나이출력
```javascript
function solution(age) {
    return 2022 - age + 1;
}
```

### 📌 3-7. n의 배수
```javascript
function solution(num, n) {
    return num % n === 0 ? 1 : 0;
}
```

### 📌 3-8. 양꼬치
```javascript
function solution(n, k) {
    return 12000 * n + (k - parseInt(n/10)) * 2000;
}
```

### 📌 3-9. 개미 군단 
- %를 먼저 함으로서 나눴을때 소숫점이 나오는 상황을 미연에 방지한다.
```javascript
function solution(hp) {
    let a = hp % 5;
    let b = (hp-a) / 5;
    let c = a % 3
    let d = (a-c) / 3
    return b + d + c;
}
```

### 📌 3-10. 종이 자르기
```javascript
function solution(M, N) {
    return M * N - 1;
}
```

