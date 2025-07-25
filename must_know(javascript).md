# 1. Math

| 함수              | 설명                  | 예시                      |
| --------------- | ------------------- | ----------------------- |
| `Math.round(x)` | **반올림**             | `Math.round(4.5)` → `5` |
| `Math.floor(x)` | **내림** (버림)         | `Math.floor(4.9)` → `4` |
| `Math.ceil(x)`  | **올림**              | `Math.ceil(4.1)` → `5`  |
| `Math.trunc(x)` | **소수점 제거** (정수 부분만) | `Math.trunc(4.7)` → `4` |
| 함수               | 설명      | 예시                     |
| ---------------- | ------- | ---------------------- |
| `Math.pow(x, y)` | x의 y제곱  | `Math.pow(2, 3)` → `8` |
| `Math.sqrt(x)`   | x의 제곱근  | `Math.sqrt(9)` → `3`   |
| `Math.cbrt(x)`   | x의 세제곱근 | `Math.cbrt(27)` → `3`  |
| 함수             | 설명                       | 예시                      |
| -------------- | ------------------------ | ----------------------- |
| `Math.abs(x)`  | 절댓값                      | `Math.abs(-5)` → `5`    |
| `Math.sign(x)` | 부호: 음수면 -1, 양수면 1, 0이면 0 | `Math.sign(-10)` → `-1` |
| 함수                    | 설명      | 예시                        |
| --------------------- | ------- | ------------------------- |
| `Math.max(a, b, ...)` | 가장 큰 값  | `Math.max(1, 9, 5)` → `9` |
| `Math.min(a, b, ...)` | 가장 작은 값 | `Math.min(1, 9, 5)` → `1` |
- spread 연산자 ... 배열:  배열을 하나하나 펼쳐서 전달하는 연산자이다.

# 2. window or global(전역 객체의 속성들)
- parseInt(): 문자열을 정수로 변환한다. 문자열의 진법을 두번째 매개변수로 제공하면 확실하게 바꿀 수 있다.
- structuredClone(): 깊은 복사
- setTimeout(함수, 지연시간(ms)); : ms는 1/1000 시간이다.
- setInterval(함수, 반복간격(ms)); : 일정 시간마다 행위를 반복한다.
- ClearInterval: setInterval을 중단시킨다.


# 3. 문자열 함수

| 메서드 이름                  | 설명                                              |
| ----------------------- | ----------------------------------------------- |
| `length`                | 문자열의 길이를 반환한다.                                  |
| `indexOf()`             | 특정 문자열이 처음 등장하는 인덱스를 반환한다.                      |
| `lastIndexOf()`         | 특정 문자열이 마지막으로 등장하는 인덱스를 반환한다.                   |
| `includes()`            | 특정 문자열이 포함되어 있는지 true/false로 반환한다.              |
| `startsWith()`          | 문자열이 특정 문자열로 시작하는지 확인한다.                        |
| `endsWith()`            | 문자열이 특정 문자열로 끝나는지 확인한다.                         |
| `slice(start, end)`     | 지정한 범위의 문자열을 잘라서 반환한다. 음수 인덱스를 지원한다.                       |
| `substring(start, end)` | 지정한 시작과 끝 인덱스를 기준으로 부분 문자열을 반환한다 (음수 사용 불가).    |
| `substr(start, length)` | 시작 위치부터 지정한 길이만큼 문자열을 잘라 반환한다 (구식, 사용 권장되지 않음). |
| `replace()`             | 첫 번째로 일치하는 문자열만 바꾼다.                            |
| `replaceAll()`          | 일치하는 모든 문자열을 바꾼다.                               |
| `toUpperCase()`         | 문자열을 모두 대문자로 변환한다.                              |
| `toLowerCase()`         | 문자열을 모두 소문자로 변환한다.                              |
| `trim()`                | 문자열의 앞뒤 공백을 모두 제거한다.                            |
| `trimStart()`           | 문자열 앞쪽 공백만 제거한다.                                |
| `trimEnd()`             | 문자열 뒤쪽 공백만 제거한다.                                |
| `concat()`              | 여러 문자열을 하나로 이어 붙인다.                             |
| `+`                     | 문자열을 이어 붙이는 연산자.                                |
| `split(구분자)`            | 문자열을 구분자를 기준으로 나누어 배열로 반환한다.                    |
| `join(구분자)`             | 배열을 구분자를 이용해 문자열로 합친다.                          |
| `repeat(n)`             | 문자열을 n번 반복하여 이어 붙인 새 문자열을 반환한다.                 |
| 백틱(`` ` ` ``) + `${}`   | 문자열 안에 변수나 표현식을 삽입할 수 있는 템플릿 리터럴 방식.            |
| `charAt(index)`         | 특정 인덱스 위치의 문자를 반환한다.                            |
| `charCodeAt(index)`     | 특정 인덱스 위치의 문자의 유니코드 값을 반환한다.                    |

# 4. 배열 함수

### 값 추가/제거 관련 메서드

| 메서드                         | 동작        | 설명                   | 예시                             |
| --------------------------- | --------- | -------------------- | ------------------------------ |
| `push()`                    | 뒤에 추가     | 배열 끝에 값 추가           | `arr.push(4)` → `[1,2,3,4]`    |
| `pop()`                     | 뒤에서 제거    | 마지막 요소 제거            | `arr.pop()` → `[1,2]`          |
| `unshift()`                 | 앞에 추가     | 맨 앞에 값 추가            | `arr.unshift(0)` → `[0,1,2,3]` |
| `shift()`                   | 앞에서 제거    | 첫 번째 요소 제거           | `arr.shift()` → `[2,3]`        |
| `splice(start, count, ...)` | 중간에 추가/삭제 | 특정 위치에서 요소를 제거하거나 추가, 삭제(count)를 0으로 하면 그 뒤에 원소를 추가함. | `arr.splice(1, 2)`             |

### 값 탐색/확인 관련 메서드

| 메서드                  | 설명                | 예시                          |
| -------------------- | ----------------- | --------------------------- |
| `includes(value)`    | 특정 값이 존재하는지 확인    | `arr.includes(3)` → `true`  |
| `indexOf(value)`     | 값의 첫 번째 위치 반환     | `arr.indexOf(2)` → `1`      |
| `lastIndexOf(value)` | 뒤에서부터 위치 찾기       | `arr.lastIndexOf(2)`        |
| `find(fn)`           | 조건을 만족하는 첫 값 반환   | `arr.find(x => x > 5)`      |
| `findIndex(fn)`      | 조건을 만족하는 첫 인덱스 반환 | `arr.findIndex(x => x > 5)` |

### 배열 복사 및 결합 관련 메서드

| 메서드                 | 설명              | 예시                                   |
| ------------------- | --------------- | ------------------------------------ |
| `slice(start, end)` | 배열 복사 (end는 제외) | `arr.slice(1, 3)`                    |
| `concat()`          | 두 배열을 합침        | `arr1.concat(arr2)`                  |
| `flat()`            | 중첩 배열을 평탄화      | `[[1,2],[3,4]].flat()` → `[1,2,3,4]` |

### 배열 가공/변형 관련 메서드

| 메서드               | 설명                 | 예시                                   |
| ----------------- | ------------------ | ------------------------------------ |
| `map(fn)`         | 각 요소를 가공하여 새 배열 생성 | `arr.map(x => x * 2)`                |
| `filter(fn)`      | 조건에 맞는 요소만 추출하여 새 배열 생성 (v, i)로 추출가능, 세번째 인자는 원본 배열을 반환      | `arr.filter(x => x > 10)`            |
| `reduce(fn, 초기값)` | 값을 누적해 하나로 만듦      | `arr.reduce((acc, x) => acc + x, 0)` |
| `sort()`          | 정렬 (문자열 기준)        | `arr.sort()`                         |
| `reverse()`       | 배열을 역순으로           | `arr.reverse()`                      |
| `join(sep)`       | 문자열로 결합            | `arr.join('-')` → `"1-2-3"`          |

### 배열 반복/순회 관련 메서드

| 메서드           | 설명               | 예시                                 |
| ------------- | ---------------- | ---------------------------------- |
| `forEach(fn)` | 각 요소에 대해 함수 실행   | `arr.forEach(x => console.log(x))` |
| `every(fn)`   | 모든 요소가 조건을 만족하는지 (boolean 반환)  | `arr.every(x => x > 0)`            |
| `some(fn)`    | 하나라도 조건 만족하는지 (boolean 반환) -> return이 true면 더 이상 검사할 필요가 없으므로 종료   | `arr.some(x => x < 0)`             |

### 배열 생성 관련 메서드 (보너스)

| 메서드                  | 설명          | 예시                                            |
| -------------------- | ----------- | --------------------------------------------- |
| `Array.isArray(obj)` | 배열인지 확인     | `Array.isArray([1,2,3]) → true`               |
| `Array.from()`       | 유사 배열 (문자열) → 배열로 | `Array.from("hello") → ['h','e','l','l','o']` |
| `Array(n).fill(v)`   | 특정 값으로 초기화  | `Array(3).fill(0)` → `[0,0,0]`                |

# 5. 이벤트 키워드

1) 마우스 관련 이벤트

| 이벤트       | 이벤트 핸들러       | 설명                    |
| --------- | ------------- | --------------------- |
| click     | `onclick`     | 대상을 클릭했을 경우           |
| dblclick  | `ondblclick`  | 대상을 더블클릭했을 경우         |
| mousedown | `onmousedown` | 마우스 버튼을 누르고 있는 동안     |
| mouseup   | `onmouseup`   | 마우스 버튼을 누르고 있다가 땐 경우  |
| mousemove | `onmousemove` | 마우스를 움직였을 경우          |
| mouseout  | `onmouseout`  | 대상에서 마우스 포인터가 벗어났을 경우 |
| mouseover | `onmouseover` | 대상에 마우스 포인터가 위치했을 경우  |
| dragdrop  | `ondragdrop`  | 대상을 클릭한 상태에서 이동했을 경우  |

2) 키보드 관련 이벤트
   
| 이벤트      | 이벤트 핸들러      | 설명                            |
| -------- | ------------ | ----------------------------- |
| keydown  | `onkeydown`  | 키가 눌러져 있는 동안 반복 실행된다.         |
| keyup    | `onkeyup`    | 키를 눌렀다가 놓았을 경우                |
| keypress | `onkeypress` | 화면에 출력되는 키가 눌릴 경우 (한글 동작 안 함) |

3) 폼(form) 요소 관련 이벤트

| 이벤트    | 이벤트 핸들러    | 설명                                             |
| ------ | ---------- | ---------------------------------------------- |
| submit | `onsubmit` | 입력 양식을 서버로 보냈을 경우 (submit 버튼을 누른 경우)           |
| change | `onchange` | 대상에 입력되어 있는 값이 바뀌었을 경우 (입력상자, 체크박스, 라디오, 드롭다운) |
| blur   | `onblur`   | 대상에서 포커스가 빠져나간 경우                              |
| focus  | `onfocus`  | 대상에 포커스가 들어왔을 경우                               |
| reset  | `onreset`  | 대상을 재시작(초기화) 시켰을 경우 (주로 form)                  |
| select | `onselect` | 입력 양식의 한 필드를 선택했을 경우                           |

4) 브라우저 관련 이벤트

| 이벤트    | 이벤트 핸들러    | 설명                        |
| ------ | ---------- | ------------------------- |
| abort  | `onabort`  | 이미지를 읽다가 중단했을 경우          |
| error  | `onerror`  | 에러가 발생했을 경우               |
| load   | `onload`   | 대상을 열었을 경우 (주로 페이지 로딩 직후) |
| move   | `onmove`   | 윈도우나 프레임을 움직였을 경우         |
| resize | `onresize` | 윈도우나 프레임의 크기가 변경됐을 경우     |
| unload | `onunload` | 대상을 종료했을 경우               |

5) 트랜지션 관련 이벤트

| 이벤트              | 이벤트 핸들러              | 설명            |
| ---------------- | -------------------- | ------------- |
| transitionrun    | `ontransitionrun`    | 트랜지션이 동작하는 동안 |
| transitionstart  | `ontransitionstart`  | 트랜지션이 시작된 경우  |
| transitioncancel | `ontransitioncancel` | 트랜지션이 취소된 경우  |
| transitionend    | `ontransitionend`    | 트랜지션이 종료된 경우  |
