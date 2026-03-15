# 📌 1. 자바스크립트 코딩테스트
### 📌 1-1. 분수의 덧셈
- 배열 선언 방식이 파이썬과 같아 편리하다.
- 유클리드 호제법 증명은 a와 b를 나누는 어떤 d로 한다.
```javascript
function solution(numer1, denom1, numer2, denom2) {
    let n = numer1 * denom2 + denom1 * numer2;
    let d = denom1 * denom2;
    let g = gcd(n, d);
    
    return [(n/g), (d/g)]; 
}

function gcd (a, b) {
    if (b === 0) return a; 
    
    return gcd (b, a % b);
}
```

- 유클리드 호제법 삼항 연산자 버전
```javascript
function gcd(a, b) {
  return b === 0 ? a : gcd(b, a % b);
}
```

### 📌 1-2. 공배수
```javascript
function solution(number, n, m) {
    return number % m === 0 && number % n === 0 ? 1 : 0;
}
```

### 📌 1-3. 배열에서 문자열 대소문자 변환하기
- answer.push(): 값을 넣고 새 배열의 길이를 반환해준다.
```javascript
function solution(strArr) {
    let answer = [];
    for (let i = 0; i < strArr.length; i++){
        if (i % 2 == 0){
            answer.push(strArr[i].toLowerCase());
        }

        else {
            answer.push(strArr[i].toUpperCase());
        }
    }
    return answer;
}
```

### 📌 1-4. 소문자로 바꾸기
```javascript
function solution(myString) {
    return myString.toLowerCase();
}
```

### 📌 1-5. 원하는 문자열 찾기
- 대소문자 구분 없이
```javascript
function solution(myString, pat) {
    return myString.toLowerCase().includes(pat.toLowerCase()) ? 1 : 0;
}
```

### 📌 1-6. 길이에 따른 연산 
- java의 stream 생각해서 하면 이건 진짜 편한거 같다.
- java는 아닌데 javascript만 0을 생략하면 b에 0이 들어가는 절차가 없어져서 빠르게 실행된다.
```javascript 
function solution(num_list) {
    if (num_list.length >= 11){
        return num_list.reduce((a, b) => (a + b));
    }

    else return num_list.reduce((a, b) => (a * b), 1);
}
```

### 📌 1-7. 조건에 맞게 수열 변환하기
```javascript
function solution(arr) {
    let answer = []
    for (i of arr){
        if (i >= 50 && i % 2 === 0)  answer.push(i / 2);
        else if (i < 50 && i % 2 !== 0 ) answer.push(i * 2);
        else answer.push(i);
    }
    return answer;
}
```

### 📌 1-8. n보다 커질 때까지 더하기
```js
function solution(numbers, n) {
    let answer = 0;
    let i = 0;
    while (answer <= n) {
        answer += numbers[i];
        i++;
    }
    return answer;
}
```

### 📌 1-9. 할 일 목록
- filter나 map을 사용할 때 (v, i)로 주면 값과 인덱스를 같이 뽑아준다. 
- 심지어 배열에 담아준다.
```js
function solution(todo_list, finished) {
    return todo_list.filter((v, i) => !finished[i]);
}
```

### 📌 1-10. 5명씩
```js
function solution(names) {
    return names.filter((v, i) => i % 5 === 0);
}
```

### 📌 1-11. 순서 바꾸기
```js
function solution(num_list, n) {
    return [...num_list.slice(n, num_list.length), ...num_list.slice(0, n)];
}
```

# 📌 2. 배열에 관하여
- 자바와 달리 배열도 특수한 객체이다.
```javascript
const arr = [10, 20, 30];
```
- 위와 같은 배열도 사실 아래와 같이 정의되어있다.
```javascript
const arr = {
    "0": 10,
    "1": 20,
    "2": 30,
    length: 3,
    __proto__: Array.prototype
};
```
- 즉 배열의 숫자 인덱스는 사실 문자열 키이다.
- 객체 내부의 속성으로 다들 관리된다.
- 다른 객체와 마찬가지로 키값이 호출되면 해싱해서 해당 값의 주소를 빠르게 찾아낸다.

| 키(key)   | 해시(hash) | 메모리 주소(address) | 값(value)  |
| -------- | -------- | --------------- | --------- |
| `"name"` | `0xA1F2` | `0xB003`        | `"Alice"` |
| `"age"`  | `0xA4C8` | `0xB020`        | `25`      |
- "name"이라는 문자열을 → 해시 함수로 변환

- 만약 new Array(); 라고 하면 내부적으로 아래처럼 프로토타입 체인을 만든다.
```js
let arr = Object.create(Array.prototype);
arr.length = 0;
return arr;
```

### 📌 2-1. 배열의 덧셈
- 배열의 toString()은 → 내부적으로 join(",")처럼 동작
- 자바스크립트에서는 **"객체 vs 원시값이 섞이는 상황"**에서 → 자동으로 toString()이나 valueOf()가 호출, 객체나 객체도 마찬가지
- 객체에 Symbol.toPrimitive가 있으면 → 그거를 호출한다.
- 그래서 배열끼리 그냥 더하면 
```js
console.log([1, 2] + [3, 4]);  // "1,23,4"
```
- 이렇게 된다.
- 실제로 더하려면 전개연산자나 concat을 사용한다.
```js
const a = [1, 2];
const b = [3, 4];
```
```js
const result = [...a, ...b];  // [1, 2, 3, 4]
```

### 📌 2-2. 구조분해 문법
- 구조 분해 할당은 **배열이 이터러블(iterable)**하기 때문에 가능한 것이며, 순서대로 .next()를 하면서 값을 하나씩 꺼내는 것처럼 작동한다.
- 내부적으로는 단순히 인덱스를 하나씩 꺼내서 재할당하는 식으로 작동한다.
```js
// 1. 배열을 임시 참조
let temp = arr;

// 2. 인덱스 순서대로 값 꺼내기
let a = temp[0];
let b = temp[1];
let c = temp[2];
```


