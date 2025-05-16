# 📌 0. 대화
### 📌 0-1. 자바스크립트 비동기 처리와 스레드
- 자바스크립트의 엔진은 한번에 하나의 작업만 처리하는 싱글 스레드이다.
- 동기적인 것은 blocking하다는 것을 의미하고 비동기적인 것은 non-blocking하다고 표현한다. 현재 작업을 어떻게 멈출 것이냐는 문제이다.

### 📌# forEach polyfill
- 폴리필(polyfill)은 **환경(브라우저나 런타임)에 기본으로 제공되지 않는 최신 기능을 “채워 넣어 주는 코드”**를 뜻한다.
- 폴리필(polyfill)은 “해당 기능이 없는 환경에 그 기능을 추가”해 주는 코드이므로 표준(spec)에서 정의된 기능과 똑같이 동작해야 한다.
- 이때 기존 함수의 polyfill을 찾아보면 해당 함수의 내부 구현을 알아볼 수 있다.
- var T, k; : 변수 2개를 동시에 선언
- forEach 폴리필 안에서 등장하는 this는 메서드를 호출한 대상 객체를 가리킨다.
- obj.sayHi()처럼 . 연산자로 호출할 때, 함수 내부의 this는 자동으로 obj를 가리킨다.
- new 키워드로 호출하면, this는 새로 생성된 객체를 가리킨다.
- 콜 스택: 현재 실행 중인 함수들이 쌓이는 곳(LIFO 구조)
- 태스크 큐: setTimeout, I/O, 이벤트 리스너 등 비동기 콜백을 대기시키는 곳
- forEach는 동기 메서드이므로, 콜백이 호출되면 즉시 콜 스택에 쌓여 실행되고, 실행이 끝나면 바로 팝(pop)된다.
- 태스크 큐는 setTimeout, fetch 등 비동기 API의 콜백을 대기시키는 곳이므로, forEach와는 무관하다.

### 📌## 이벤트 루프
- 이벤트 루프는 이런 비동기 작업의 콜백을 “나중에 실행”하도록 스케줄링해 주어, 메인 스레드가 다른 코드를 계속 실행하게 해준다.
- 콜 스택이 비었을 때, 우선 마이크로태스크 → 그 다음 매크로태스크를 콜 스택으로 옮겨 실행
- 이벤트 루프는 항상 가동되고 있고 비동기 api가 없으면 쉰다.
- 이벤트 루프가 쉬는 동안 렌더링 파이프 라인에서 css등 스타일을 검사하고 가비지 컬렉션을 실행한다.

```js
// 0) 이 전체 블록은 ‘forEach’가 없는 환경에서만 실행됩니다.
if (!Array.prototype.forEach) {
    // 1) 배열 전용 메서드를 정의합니다.
    Array.prototype.forEach = function(callback, thisArg) {
        var T, k;

        // 2) this 값 검사: 올바르게 쓰지 않으면 실행을 멈추고 에러를 던져요.
        //    예: null.forEach(...) 처럼 호출할 때를 막습니다.
        if (this === null) {
            throw new TypeError('this is null or not defined');
        }

        // 3) 유사배열(문자열, arguments 객체 등)도 처리할 수 있도록
        //    원시값이면 Object()로 “객체화” 합니다.
        var O = Object(this);

        // 4) length 프로퍼티(배열 길이)를 32비트 부호 없는 정수로 변환
        //    >>>0 은 “비트 연산을 통해 숫자로” 만드는 트릭입니다.
        var len = O.length >>> 0;

        // 5) callback이 함수가 아니면 에러!
        if (typeof callback !== "function") {
            throw new TypeError(callback + ' is not a function');
        }

        // 6) thisArg 인자가 넘어왔다면, 콜백 내부에서 참조할 this로 사용
        if (arguments.length > 1) {
            T = thisArg;
        }

        // 7) 반복용 인덱스 초기화
        k = 0;

        // 8) k가 배열 길이보다 작을 동안 계속 반복
        while (k < len) {
            var kValue;

        // 9) “희소 배열”도 고려: 실제 값이 있는 인덱스만 처리
        //    예: [1, , 3] 에서 빈 칸(인덱스 1)은 건너뛰어요.
            if (k in O) {
                // 10) 실제 요소값을 꺼내서
                kValue = O[k];
                //     callback을 **동기적으로**(즉시) 호출합니다.
                //     call(T, value, index, array) 형태로 this와 인자를 지정
                callback.call(T, kValue, k, O);
        }

        // 11) 다음 인덱스로 이동
        k++;
        }

        // 12) 반환값을 명시하지 않으면 undefined가 돌아갑니다.
        //     forEach는 항상 undefined를 반환하도록 사양이 정해져 있어요.
    };
}
```

# 1. html-js
- html tag를 js에서는 element라고 한다.
- body태그 맨 아래에 js를 삽입하는 이유는 ux 향상을 위해서다. 먼저 화면을 보여주고 기능을 정의하는 식이다.
- id 가 여러 개이면 디자인과 기능이 충돌할 수 있어서 사용하면 안된다.

### 📌 1-1. html을 객체로
- BOM (Browser Object Model): 웹 브라우저를 통해 실행될 때 Javascript가 갖게되는 기본 객체 구조.
모든 객체는 window 객체의 하위 객체로서 존재한다.
- DOM (Document Object Model): 문서 구조를 프로그래밍 언어로 다룰 수 있게 추상화한 인터페이스, BOM의
하위 요소중 하나이다.
- 아래처럼 표현, 각 노드들이 부모자식 관계로 이어져 있다.
- 트리 관계를 브라우저로 해석하여 객체로 변환한다. (배열과 비슷한 특수객체 -> 인덱스 탐색 가능)
- 정확히는 HTMLCollection, Element(단일 객체), NodeList 객체
```less
Document
 ├─ html
 │   ├─ head
 │   │   └─ title (텍스트: "나의 첫 페이지")
 │   └─ body
 │       ├─ h1 (텍스트: "안녕하세요!")
 │       └─ p  (텍스트: "DOM을 배워봅시다.")
```

| 구분            | Element          | HTMLCollection                     | NodeList                                      |
| ------------- | ---------------- | ---------------------------------- | --------------------------------------------- |
| 반환 예시 메서드     | `getElementById` | `getElementsByTagName`, `children` | `querySelectorAll` (정적)<br>`childNodes` (라이브) |
| 라이브 여부        | —                | ✅ 라이브                              | 정적 ❌ / 라이브 ✅                                  |
| 반복 지원         | 단일 객체            | `for`, `for…of`                    | `forEach`, `for…of`                           |
| 인덱스·length 접근 | —                | ✅                                  | ✅                                             |

- 라이브는 실시간으로 dom 트리 변화를 반영하는지의 여부이다.

#### 태그 이름으로 객체 가져오기
```js
const 객체 = document.getElementsByTagName("태그이름");
```

#### id 값으로 가져오기
```js
const 객체 = document.getElementById("ID이름");
```

#### css 클래스 이름으로 가져오기
```js
const 객체 = document.getElementsByClassName("CLASS이름");
```

#### css 선택자로 가져오기
- 위는 단일 아래는 복수
```js
const 객체 = document.querySelector("CSS선택자");
const 객체 = document.querySelectorAll("CSS선택자");
```

### 📌 1-2. 이벤트

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

#### 이벤트 리스너
- 이벤트 이름을 문자열로 제공하고 2번째 인자로 함수를 제공하면 이벤트가 발생했을때 해당 함수를 콜백해준다.
- 이때 객체는 html 태그를 객체화 한 것이다.

```js
객체.addEventListener('이벤트이름', 콜백함수);
```

- addEventListener 내부적으로는 리스너 등록 → 경로 계산 → 단계별 호출 이라는 추상화된 흐름으로 설계됨.
- EventTarget 인터페이스: HTMLElement, Document, Window 등은 모두 이 인터페이스를 상속받는다.
- 사양상 EventTarget은 내부 슬롯 [[EventListenerList]]를 가진다.
- 아래 객체는 addEventListener가 내부 슬롯에 저장할 때 사용하는 리스너 객체이다.
```js
{
    callback: f1, // 이벤트가 발생했을때 진행할 함수 참조
    capture: false,
    once:    false,
    passive: false
}
```
```lua
EventTarget (예: element)
└─ [[EventListenerList]] ──┐
   ├─ "click"  → [listenerA, listenerB, …]
   ├─ "keydown"→ [listenerC, …]
   └─ …
```


#### 이벤트 핸들러
- html 태그 내부에 속성 형태로 이벤트를 핸들링하는 방법이다.
- 잘 안쓰는 추세지만 react에서는 이것을 주로 사용한다.
```html
<태그이름 on이벤트이름="...JS코드영역..."></태그이름>
```

### 📌 1-3. 스크롤

```html
<!DOCTYPE html>
<html lang="ko" translate="no">
<head>
    <meta charset="UTF-8">
    <meta name="google" content="nottranslate" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>scroll</title>
    <style>
        .box{
            height: 2000px;
            background: linear-gradient(0deg, #000 0, #fff 100%);
        }
    </style>
</head>
<body>
    <div id="container"><div class="box1"></div></div>
    
    <script>
        window.addEventListener('scroll', e => {
            const scrollTop = window.scrollY; // 스크롤이 위에서부터 도달한 거리
            const windowHeight = window.screen.availHeight; // 스크린으로 볼 수 있는 높이
            const documentHeight = document.body.scrollHeight; // 문서 전체 높이

            if (scrollTop + windowHeight >= documentHeight) {
                const container = document.querySelector('#container');
                container.innerHTML += '<div class="box1"></div>'; // container 안에 html
            }
        })
    </script>
</body>
</html>
```