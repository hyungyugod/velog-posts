# 📌 0. 대화
### 📌 0-1. 데이터 타입에 대하여
- 자바스크립트가 데이터 타입을 구분하는 방식은 자바스크립트 엔진이 소스코드를 처리할때 특정 구문을 보고 앞에 데이터 타입을 명시하는 태그를 붙여서 이진수로 변환하는 방식이다. 태그를 붙이는 과정은 추상 구문 트리를 통해 데이터 타입을 분류하는 것이고 이 후 바이트 코드를 생성한 다음 런타임으로 넘어간다.
- typeof 같은 함수는 이 태그를 확인하는 함수이다.

### 📌 0-2. null과 undefined의 차이
- null은 보통 변수가 비어있고 나중에 값이 들어올 것이라는 것을 의도적으로 표현할때 사용한다.
- 나머지 경우는 undefined이다.

### 📌 0-3. 렉시컬 스코프에 관하여
- 렉시컬 스코프란 변수 인식 범위를 함수가 호출된 위치가 아닌 정의된 위치에 기반하여 정한다는 것이다.
- 클로저 가능 (클로저란 외부 함수의 변수는 내부함수가 인식할 수 있지만 내부 함수의 변수는 외부함수가 인식하지 못한다는 뜻이다.)

# 1. 함수의 이해
### 📌 1-1. 파라미터의 기본값
- 함수에 매개변수를 넣지 않으면 값을 undefined으로 설정한다는 내부 규칙이 있다.
- 함수가 호출되면 내부적으로 arguments라는 객체가 생기고, a는 arguments[0], b는 arguments[1] 이런 식으로 매핑된다. arguments에 존재하지 않는 값은 자동으로 **undefined**가 된다.

### 📌 1-2. 함수 문법관련
- function이라고 앞에 쓰는 예약어 자체는 인터프리터가 뒤를 함수로 해석하기 위한 문법구조이고 function 예약어를 통해 정의된 함수는 내부적으로 Function 객체로 작동한다.
```javascript
function hello(name) {
  return "Hi, " + name;
}
// 아래 처럼 해석
const hello = new Function("name", "return 'Hi, ' + name;");
```

### 📌 1-3. 익명함수
- 식별자가 없는 함수 (기능만 정의되어 있음) 즉 키값은 없고 벨류값만 있는 것을 의미한다.

### 📌# 함수 표현식과 함수 선언문의 차이
- 함수 선언문은 호이스팅되어 실행되지만 함수 표현식은 그렇지 않아 변수가 호출 -> 선언의 순서일 경우 나중에 값이 변수에 저장되므로 실행되지 않는다.

- 함수 표현식
```javascript
const greet = function(name) {
  return "Hi " + name;
};
```
- 함수 선언문
```javascript
function greet(name) {
  return "Hi " + name;
}
```

### 📌# 호이스팅(Hoisting)
- 어원은 끌어올리다는 뜻
- 인터프리터는 처음에 먼저 파싱을 하면서 한번 훑고 빠르게 정보들을 메모리에 올려둔다. 
- 이 과정에서 변수와 함수 정보를 메모리에 올려두는데 이 과정이 바로 호이스팅이다.


### 📌 1-4. 콜백함수
- 함수의 괄호 표기법은 그 함수를 시행하라는 뜻이다. 함수 시행은 해당 식별자를 가진 함수의 주소를 찾아가 기능을 실현한다.
- 콜백함수에서 매개변수는 함수형이라는 데이터 타입이 생략된 함수형 매개변수이자 함수가 정의된 주소이다. 
- 나중에 실행할 작업을 예약하고 넘어가는 비동기 처리방식에 많이 사용한다.

### 📌 1-5. 화살표 함수
- 자바와 람다식과 비슷하긴 하나 사용 범위의 차이가 있다. 
- 자바의 람다식은 반드시 "함수형 인터페이스"를 구현해야 한다.
- 함수형 인터페이스란 추상 메서드가 딱 하나만 존재하는 인터페이스를 의미한다.
- 아래는 콜백지옥을 화살표 함수로 개선한 코드이다.
```javascript
function step1(data, callback) {
  const result = data + 1;
  console.log("1단계 결과:", result);
  callback(result);
}

function step2(data, callback) {
  const result = data * 2;
  console.log("2단계 결과:", result);
  callback(result);
}

function step3(data, callback) {
  const result = data - 3;
  console.log("3단계 결과:", result);
  callback(result);
}

// 콜백지옥
step1(5, function (result1) {
    step2(result1, function (result2) {
    step3(result2, function (result4) {
        console.log("최종 결과:", result4);
    });
    });
});

// 화살표함수
step1(5, result1 => {
    step2(result1, result2 => {
    step3(result2, result4 => {
        console.log("최종 결과:", result4);
    });
    });
});
```

# 📌 2. 자바스크립트 코딩테스트

### 📌 2-1. 각도기
```javascript
function solution(angle) {
    if (0 < angle && angle < 90) return 1;
    else if (angle === 90) return 2;
    else if (angle === 180 ) return 4;
    else return 3;
}
```

### 📌 2-2. 숫자비교하기
```javascript
function solution(num1, num2) {
    return num1 === num2 ? 1 : -1;
}
```

### 📌 2-3. 옷가게 할인받기
- 정수 리턴 조건 확인하기
```javascript
function solution(price) {
    if (price >= 500000) return parseInt(price * 0.8);
    else if (price >= 300000) return parseInt(price * 0.9);
    else if (price >= 100000) return parseInt(price * 0.95);
    else return price;
}
```

### 📌 2-4. 피자 나눠먹기 (1)
```javascript
function solution(n) {
    return parseInt((n - 1) / 7) + 1;
}
```

### 📌 2-5. 피자 나눠먹기 (3)
```javascript
function solution(slice, n) {
    return parseInt((n - 1) / slice) + 1;
}
```

### 📌 2-6. 치킨쿠폰
```javascript
function solution(chicken) {
    let answer = 0;
    
    while (parseInt(chicken / 10) !== 0){
        div = parseInt(chicken / 10);
        mod = chicken % 10;
        answer += div;
        chicken = div + mod;
    }
    
    return answer;
}
```

### 📌 2-7. 구슬을 나누는 경우의 수
- 원래하던 조합 계산 활용
```javascript
function solution(balls, share) {
    let d = Math.min(balls - share, share);
    let n = Math.max(balls - share, share);
    let counter = d;
    let real_n = 1;
    let real_d = 1;
    
    for (let i = 0; i < counter; i++){
        real_n *= balls;
        real_d *= d;
        
        balls -= 1;
        d -= 1;       
    }
    
    return real_n / real_d;
}
```

### 📌 2-8. 제곱수 판별하기
```javascript
function solution(n) {
    return Math.sqrt(n) % 1 === 0 ? 1 : 2;
}
```

### 📌 2-9. 직각삼각형 출력하기
```javascript
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let input = [];

rl.on('line', function (line) {
    input = line.split(' ');
}).on('close', function () {
    let n = input[0];
    for (let i = 0; i < n; i++) {
        console.log("*".repeat(i + 1));
    }
});
```

### 📌 2-10. 짝수의 합
```javascript
function solution(n) {
    let answer = 0;
    
    for (let i = 2; i < n + 1; i += 2){
        answer += i;
    }
    return answer;
}
```

### 📌 2-11. 팩토리얼
- 같은 경우 꼭 포함해서 하기
```javascript
function solution(n) {
    let counter = 1;
    let i = 1;

    while (counter <= n) {
        counter *= i;
        i++;
    }

    return i - 2;
}
```

### 📌 2-12. 순서쌍의 개수
```javascript 
function solution(n) {
    let answer = 0;
    let sq = Math.sqrt(n);
    
    for (let i = 0; i < sq; i++){
        if (n % i ===0){
            answer += 1;
        }
    }
    
    answer *= 2;
    
    if (sq % 1 === 0) {
        answer++;
    }
    
    return answer;
}
```

### 📌 2-13. 피자 나눠 먹기
```javascript
function solution(n) {
    let answer = 0;
    
    for (let i = 1; i <= n; i++){
        if (6 * i % n === 0){
            answer = i;
            break;
        }
                            
    }
    
    return answer;
}
```
### 📌 2-14. 합성수 찾기
- n + 1까지 생성해야 n이 배열에 포함됨.
```javascript
function solution(n) {
    return n - findPrimeCount (n) - 1;
}



function findPrimeCount (n) {
    let arr = Array(n + 1).fill(0);
    let answer = 0;

    for (let i = 2; i < n; i++){
        if (arr[i] === 0) {
            for (let j = i*i; j < n; j += i){
                arr[j] = 1;
            }
            answer += 1;
        }
    }
    
    return answer;
}
```