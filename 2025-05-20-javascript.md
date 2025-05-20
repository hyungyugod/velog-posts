# 📌 1. html 탐색과 생성

| 구분                | **Element**                                                             | **HTMLCollection**                                                                                                           | **NodeList**                                                                                   |
| ----------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **반환 예시 메서드**     | - `getElementById`<br>- `querySelector`<br>- `querySelectorAll` (단일 선택) | - `getElementsByTagName`<br>- `getElementsByClassName`<br>- `children`<br>- `forms`, `images`, `links` 등<br>- `document.all` | - `querySelectorAll`<br>- `childNodes`<br>- `getElementsByName`<br>- (예전: `document.contents`) |
| **라이브 여부**        | —                                                                       | ✅ 라이브(실시간 반영)                                                                                                                | 정적 ❌ / 라이브 ✅ (`childNodes`만 라이브)                                                               |
| **반복 지원**         | 단일 객체                                                                   | `for`, `for…of`                                                                                                              | `forEach`, `for…of`                                                                            |
| **인덱스·length 접근** | —                                                                       | ✅ 가능                                                                                                                         | ✅ 가능                                                                                           |


### 📌 1-1. 부모와 조상요소 찾기
- e.currentTarget.parentElement: 이벤트 객체에 표시된 현재 이벤트가 발생한 노드의 상위 노드
- e.currentTarget.closest('.list-group'): 현재 이벤트가 발생한 노드에서 list-group 클래스에 속한 가장 가까운 조상
```html
<body>
    <ul class="list-group">
        <li class="list-group-item">
            <a href="#" class="find-parent" data-color="#ff6600">parent</a>
            <a href="#" class="find-parents" data-color="#ff6600">parents</a>
        </li>
        <li class="list-group-item">
            <a href="#" class="find-parent" data-color="#0066ff">parent</a>
            <a href="#" class="find-parents" data-color="#0066ff">parents</a>
        </li>
        <li class="list-group-item">
            <a href="#" class="find-parent" data-color="#00aa00">parent</a>
            <a href="#" class="find-parents" data-color="#00aa00">parents</a>
        </li>
    </ul>
    
    <script>
        document.querySelectorAll('.find-parent').forEach(v => {
            v.addEventListener('click', e => {
                e.preventDefault();
                e.currentTarget.parentElement.style.backgroundColor = e.currentTarget.dataset.color;
           });
        });

        document.querySelectorAll('.find-parents').forEach(v => {
            v.addEventListener('click', e => {
                e.preventDefault();
                e.currentTarget.closest('.list-group').style.backgroundColor = e.currentTarget.dataset.color;
            })
        })
    </script>
</body>
```

### 📌 1-2. 자식 요소 찾기
- childnodes는 코드 줄바꿈을 위한 줄바꿈도 텍스트로 인식하므로 불편함. (forEach 사용 가능)
- children은 불필요한 요소만 제거하고 하위 element만 조회한다. (forEach 사용 불가능)
- Array.from()은 두번째 인자로 map 함수를 바로 줄 수 있다. 이때 배열의 요소는 boolean이 된다.
- 스프레드 문법으로 배열 변환해도 상관없다.
- 색상 문자열로 주는 것 잊지 말기
- 버튼은 기본적으로 아무 동작도 하지 않으므로 preventDefault를 할 필요가 없다.
```html
<body>
    <ul id="list">
        <li id="one">One</li>
        <li id="two" class="blue">
            Two
            <ul>
                <li id="a">A</li>
                <li id="b" class="blue">B</li>
                <li id="c" class="red">C</li>
                <li id="d">D</li>
            </ul>
        </li>
        <li id="three">Three</li>
        <li id="four" class="blue">Four</li>
    </ul>
    
    <button type="button" id="btn1">상위 ul의 자식들</button>
    <button type="button" id="btn2">Two의 하위 ul의 자식들</button>
    
    <script>
        document.querySelector('#btn1').addEventListener('click', () => {
            const ch = document.querySelector('#list').children;
            [...ch].forEach(v => v.style.backgroundColor = '#06f');
        });

        document.querySelector('#btn2').addEventListener('click', () => {
            const ch = document.querySelector('#two > ul').children;
            Array.from(ch).forEach(v => v.style.fontWeight = '900');
        });
    </script>
</body>
```

### 📌 1-3. 자손요소 탐색
- html을 객체로 변환해 가져오면 거기에 다시 getElementBy나 querySelector를 이용하여 탐색할 수 있다.
- post1만 콕 찝어서 가져온다음에 post1의 하위 요소만 선택하여 나열함.
- document는 html 문서 전체를 의미한다.
```html
<body>
    <ul id="post1">
        <li><span class="thumb">1</span></li>
        <li><span class="thumb">2</span></li>
        <li><span class="thumb">3</span></li>
        <li><span class="thumb">4</span></li>
    </ul>
    
    <ul id="post2">
        <li><span class="thumb">1</span></li>
        <li><span class="thumb">2</span></li>
        <li><span class="thumb">3</span></li>
        <li><span class="thumb">4</span></li>
    </ul>
    
    <button id="btn1" type="button">자손요소</button>

    <script>
        document.querySelector('#btn1').addEventListener('click', () => {
            const post1 = document.querySelector('#post1');
            post1.querySelectorAll('.thumb').forEach(v => {
                v.style.color = '#6f';
                v.style.fontWeight = 'bold';
            })
        })
    </script>
</body>
```

### 📌 1-4. previousElementSibling, nextElementSibling
- previousElementSibling, nextElementSibling는 각각 형제중에 이전요소, 다음요소 탐색을 의미한다.
- 버튼의 형제는 서로밖에 없으므로 한칸 부모로 올라갔다가 내려와야한다.
```html
<body>
    <div class="container">
        <span>1</span>
        <span>2</span>
        <span>3</span>
        <span>
            <button type="button" id="btn1">Prev</button>
            <button type="button" id="btn2">Next</button>
        </span>
        <span>4</span>
        <span>5</span>
        <span>6</span>
    </div>
    
    <script>
        let size1 = 16;
        let size2 = 16;

        document.querySelector('#btn1').addEventListener('click', e => {
            size1 += 2;
            e.currentTarget.parentElement.previousElementSibling.style.fontSize = size1 + 'px';
        });

        document.querySelector('#btn2').addEventListener('click', e => {
            size2 += 2;
            e.currentTarget.parentElement.nextElementSibling.style.fontSize = size2 + 'px';
        });
    </script>
</body>
```

### 📌 1-5. 메뉴바 만들기
- css에서 숨길 메뉴의 높이를 0으로 주고 overflow:hidden으로 감춘다음에 js에서 height를 숨긴 요소의 원래 높이만큼 증가시키면서 보이게 하는 방법
- 링크 크기가 height: 48px;로 a태그에 걸려있으므로 기본적으로 height가 작아도 아무처리가 없으면 내부요소의 크기를 따른다.
- height: 0;
- overflow: hidden;
- transition: height 180ms ease-out; : 적용할 대상, 속도, 가속곡선
- scrollHeight: 요소의 콘텐츠 전체가 차지하는 높이, 내부에 콘텐츠가 많아서 스크롤이 생기면, 스크롤로 내릴 수 있는 맨 끝까지의 전체 높이이다.
- z-index: 1000; : 이렇게 z축을 줘야 값이 다른 값보다 떠있을 수 있다.
- flex: 0 0; : 원본 코드에서 이코드로 grow와 shrink를 굳이 줄 필요가 없다. 고정값으로 px를 제공했기 때문이다.
```html
<style>
        /** 기본 속성 초기화 */
        .menu-container {
            list-style: none;
            margin: 0;
            padding: 0;
            display: flex;
        }

        /** 메뉴에 포함된 모든 링크에 대한 크기, 배경 지정 및 글자 꾸미기 */
        a {
            display: block;
            width: 179px;
            height: 48px;
            background: url('img/btn.png');
            line-height: 48px;
            text-align: center;
            font-weight: bold;
            color: #fcdfb5;
            text-decoration: none;
        }
        /** 마우스가 올라간 링크에 대한 배경이미지 변경 */
        a:hover {
            background: url('img/btn_over.png');
        }

        .menu-item {
            /* flex: 0 0; */
            /* 서브메뉴의 기준점을 부모요소로 지정하기 위한 처리 */
            position: relative;
        }

        /** 서브메뉴가 펼쳐지더라도 다른 요소들 위에 떠 있어야 하므로, Position 처리 */
        .sub {
            list-style: none;
            margin: 0;
            padding: 0;
            position: absolute;
            z-index: 1000;
            height: 0;
            overflow: hidden;
            transition: height 180ms ease-out;
        }
    </style>
</head>
<body>
    <ul class="menu-container">
        <li class="menu-item">
            <a href="#">Frontend</a>
            <ul class="sub">
                <li><a href="#">HTML+CSS</a></li>
                <li><a href="#">Javascript</a></li>
                <li><a href="#">jQuery</a></li>
            </ul>
        </li>
        <li class="menu-item">
            <a href="#">Backend</a>
            <ul class="sub">
                <li><a href="#">PHP</a></li>
                <li><a href="#">JSP</a></li>
                <li><a href="#">Node.js</a></li>
            </ul>
        </li>
        <li class="menu-item">
            <a href="#">Mobile</a>
            <ul class="sub">
                <li><a href="#">iOS</a></li>
                <li><a href="#">Android</a></li>
                <li><a href="#">Hybrid</a></li>
            </ul>
        </li>
    </ul>
    
    <!-- 페이지 컨텐츠를 가정한 요소 -->
    <h1>Hello World</h1>
    
    <script>
        document.querySelectorAll('.menu-item').forEach(v => {
            v.addEventListener('mouseover', e => {
                const sub = e.currentTarget.querySelector('.sub');
                sub.style.height = sub.scrollHeight + 'px';
            });

            v.addEventListener('mouseout', e => {
                const sub = e.currentTarget.querySelector('.sub');
                sub.style.height = '0px';
            })
        });

    </script>
</body>
```

### 📌 1-6. 요소 생성하기
- document.createElement('li'); : 'li'라는 태그 이름을 가진 요소를 새로 만든다. -> 노드상에만 추가되고 화면엔 보이지 않는다.
- 위의 생성한 새로운 태그를 어딘가 append해줘야 나타나고 의미가 생긴다.
-  e.currentTarget.remove() : 스스로 제거한다는 의미이다.
-  list.append(getItem('blue')); : 정의한 함수를 통해 생성한 li태그를 list라는 이름의 ul 태그에 넣기
-  insertBefore (삽입할 노드, 기준점 노드): 기준점 직전에 추가된다. (첫번째 항목의 직전 -> 첫번째)
```html
<body>
    <input type="text" id="comment">
    <button type="button" id="appendChild">appendChild</button>
    <button type="button" id="insertBefore1">insertBefore1</button>
    <button type="button" id="insertBefore2">insertBefore2</button>
    <hr>

    <!-- 동적으로 생성할 html요소가 추가될 위치 -->
    <ul id="list"></ul>

    <script>
        const list = document.querySelector('#list'); // 추가될 위치 객체를 변수로 저장해둠.
        const comment = document.querySelector('#comment'); // input 태그의 정보를 담은 객체 

        const getItem = (name) => {
            const li = document.createElement('li');
            li.classList.add(name, 'item');
            li.innerHTML = comment.value; // comment 객체 속 사용자가 입력한 정보를 innerHTML에 넣어준다.
            li.addEventListener('click', e => e.currentTarget.remove()); //스스로 제거

            return li;
        }

        // 진짜 기능
        document.querySelector('#appendChild').addEventListener('click', () => {
            list.append(getItem('blue')); // 현재 시점 사용자 입력을 바탕으로 li를 생성하여 바로 빈 list ul태그에 넣어줌
        });

        document.querySelector('#insertBefore1').addEventListener('click', () => {
            list.insertBefore(getItem('orange'), null); // 두번째 인자 null이면 위와 똑같이 작동
        });

        document.querySelector('#insertBefore2').addEventListener('click', () => {
            list.insertBefore(getItem('pink'), document.querySelector('li:first-child')); // 첫번째 항목 직전에 추가 -> 첫번째 요소로 추가 
        });
    </script>
</body>
```

### 📌 1-7. 이미지 미리보기
- display: none;으로 파일업로드 버튼을 없앤다. -> label에 for을 동일하게 주면 꼭 버튼을 누르지 않아도 라벨만 누르면 업로드가 클릭이 된다.
- e.currentTarget.files; : input받은 파일을 가져오기
- const imgUrl = URL.createObjectURL(v); : 해당 파일 객체에서 url을 뽑아온다.
- css는 생략한다.
```html
<body>
    <div class="image-upload">
        <label for="file-input">
            <img src="img/upload.jpg" />
        </label>
    
        <input id="file-input" type="file" multiple />
    </div>

    <div id="preview-container"></div>
    
    <script>
        document.querySelector('#file-input').addEventListener('change', e => {
            // 미리보기 상자 객체
            const previewContainer = document.querySelector('#preview-container');
            previewContainer.innerHTML = ''; // 입력되는 파일개수와 보이는 파일 개수를 맞춰주기 위한 초기화 작업

            const files = e.currentTarget.files; // input받은 파일을 가져오기
            Array.from(files).forEach(v => {
                const imgUrl = URL.createObjectURL(v);

                const imgTag = document.createElement('img');
                imgTag.classList.add('preview');
                imgTag.setAttribute('src', imgUrl);

                previewContainer.appendChild(imgTag);
            })
        })
    </script>
</body>
```

### 📌 1-8. 감췄던 페이지 열기
- const target = e.currentTarget.closest('.collapse').querySelector('.content');에서 '.content' 클래스에 소속된게 하나이므로 그냥 querySelector를 사용한다.
- 당연하지만 NodeList에는 style 접근이 안된다.
- if (target.style.maxHeight) target.style.maxHeight = 0; // 0이 아니라면 0을 의미하고 값이 없어도 가능하다. 이는 다시 접는 기능을 구현한다. 
- 위의 작동을 토글을 주고 클래스를 넣다뺐다하는 방식으로 구현할 수도 있을 것 같다.
- 근데 위처럼 했을 때 한번 닫으면 다시 안열리는 문제가 발생한다. 근데 값이 null이면 가능한데 null 이외의 값은 0을 넣어도 값이 있다고 인식해서 추가적인 조건으로 0이어도 작동하게끔 만들어주어야한다.
- 주요 코드만 모아서 가져왔다.
```html 
<script>
        document.querySelectorAll('.collapsible-title').forEach(v => {
            v.addEventListener('click', e => {
                const cur = e.currentTarget;
                cur.classList.toggle('active');
                const target = cur.closest('.collapse').querySelector('.content');

                if (target.style.maxHeight) target.style.maxHeight = null; 
                else target.style.maxHeight = target.scrollHeight + 'px';
            });
        });
</script>

<h2>Animated Collapsibles</h2>
    <p>Collapsible:</p>
    <div class="collapse">
        <h1 class="collapsible-title">Open Collapsible</h1>
        <div class="content">
            <p>
                Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            </p>
        </div>
    </div>
```
```css
.content {
            padding: 0 18px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.2s ease-out;
            background-color: #f1f1f1;
        }
```

### 📌 1-9. 감췄던 페이지를 여는데 열려있던 다른 페이지는 닫기
- 닫을때는 height = null; 로 닫기
- active로 활성화된 얘만 열고 닫을 수 있게 설계함. -> active면 무조건 엶
- 한번 더 했을때는 toggle 때문에 active가 꺼지면서 active를 contain하고있지 않게되어 닫히게 된다.
```html
<script>
        document.querySelectorAll('.collapsible-title').forEach(v => {
            v.addEventListener('click', e => {
                // 일단 전부 닫고 시작
                document.querySelectorAll('.content').forEach(w => w.style.maxHeight = null); 

                // 현재를 제외하고 active 클래스 삭제
                const cur = e.currentTarget;
                cur.classList.toggle('active');

                document.querySelectorAll('.collapsible-title').forEach(w => {
                    if (w!== cur) w.classList.remove('active');
                })

                const target = cur.closest('.collapse').querySelector('.content');

                if (cur.classList.contains('active')) target.style.maxHeight = null; 
                else target.style.maxHeight = target.scrollHeight + 'px';
            });
        });
    </script>
```

# 📌 2. 모듈 활용
- js폴더로 따로 빼서 script 안에 src 속성으로 파일 경로를 삽입하여 js를 가져와서 바로 사용할 수 있다.

### 📌 2-1. 사칙연산 모듈활용
- fieldset: 여러 입력 요소(input, select, button 등)를 논리적으로 하나의 그룹으로 묶어준다.
- legend: fieldset 그룹의 제목을 나타낸다.
```html
<body>
    <form>
        <fieldset>
            <legend>계산기</legend>
                <div>
                    <label for="x"></label>
                    <input type="text" id="x"/>
                </div>
                <div>
                    <label for="y"></label>
                    <input type="text" id="y"/>
                </div>
                <div>
                    <button type="button" id="plusButton">+</button>
                    <button type="button" id="minusButton">-</button>
                    <button type="button" id="timesButton">*</button>
                    <button type="button" id="divideButton">/</button>
                    <h1 id="result"></h1>
                </div>
        </fieldset>
    </form>
    
    <script src="js/function.js"></script>

    <script>
        const x = document.querySelector("#x");
        const y = document.querySelector("#y");
        const result = document.querySelector("#result");
        
        const plusButton = document.querySelector("#plusButton");
            plusButton.addEventListener('click', (e) => {
            const value = plus(parseInt(x.value), parseInt(y.value));
            result.innerHTML = value;
        });
        
        const minusButton = document.querySelector("#minusButton");
            minusButton.addEventListener('click', (e) => {
            const value = minus(parseInt(x.value), parseInt(y.value));
            result.innerHTML = value;
        });
        
        const timesButton = document.querySelector("#timesButton");
            timesButton.addEventListener('click', (e) => {
            const value = times(parseInt(x.value), parseInt(y.value));
            result.innerHTML = value;
        });
        
        const divideButton = document.querySelector("#divideButton");
            divideButton.addEventListener('click', (e) => {
            const value = divide(parseInt(x.value), parseInt(y.value));
            result.innerHTML = value;
        });
    </script>
</body>
```
- 사직연산 함수 파일
```js
function plus(x, y) {
    return x + y;
};

function minus(x, y) {
    return x - y;
};

function times(x, y) {
    return x * y;
};

function divide(x, y) {
    return x / y;
};
```

### 📌 2-2. 모듈 속 객체를 통하여 매서드 실행
- my객체가 속성으로 갖고 있는 kor 메서드 실행
- 정확히 말하면 kor이라는 키가 벨류로 함수를 가지고 있는 것
```html
<script src="js/myObject.js"></script>
    <script>
        document.querySelector('#kor').addEventListener('click', () => {
            document.querySelector('#msg').innerHTML = my.kor();
        })
        
        document.querySelector('#eng').addEventListener('click', () => {
            document.querySelector('#msg').innerHTML = my.eng();
        })
    </script>
```

# 📌 3. 라이브러리 활용

### 📌 3-1. AOS
- 화면에 페이지가 애니메이션과 함께 등장하도록 하는 라이브러리이다.
- https://github.com/michalsnik/aos 깃허브에서 사용법 확인, 혹은 js aos 등으로 검색하면 홈페이지에서 사용법을 확인할 수 있음.
```html
<body>
        <h1>AOS</h1>
        <p>
            <a href="https://michalsnik.github.io/aos/">https://michalsnik.github.io/aos/</a>
        </p>
        <hr>
        <ul>
            <li>data-aos : 애니메이션 종류 문자열 (필수)</li>
            <li>data-aos-duration: 애니메이션 속도 (1/1000초)</li>
            <li>data-aos-easing: 애니메이션 재생 옵션 (css의 transition 속성값을 따름)</li>
            <li>data-aos-offset: 대상 요소가 원래 화면 하단으로부터 떨어진 거리. <br>
            (이 거리에 도달하면 애니메이션이 작동)</li>
            <li>data-aos-anchor-placement="박스위치-화면위치"<br>
            - 대상 요소의 top,center,bottom이 브라우저의 top,center,bottom에 도달할 경우 애니메이션 시작</li>
        </ul>

        <div class="box" data-aos="fade-zoom-in" data-aos-offset="0" data-aos-easing="ease-in-sine" data-aos-duration="600">AOS</div>
        <div class="box" data-aos="fade-left" data-aos-anchor-placement="top-center" data-aos-easing="ease-in-sine" data-aos-duration="600">AOS</div>
        <div class="box" data-aos="fade-right" data-aos-anchor-placement="top-center" data-aos-easing="ease-in-sine" data-aos-duration="600">AOS</div>
        <div class="box" data-aos="fade-up" data-aos-anchor-placement="center-center" data-aos-easing="ease-in-sine" data-aos-duration="600">AOS</div>
        <div class="box" data-aos="fade-down" data-aos-offset="100" data-aos-easing="ease-in-sine" data-aos-duration="600">AOS</div>
        
    <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
    <script>
        AOS.init();
    </script>
</body>
```

### 📌 3-2. pageable
- 스크롤 조금만 내려도 한 화면 꽉차게 한 페이지씩 나오게 하는 라이브러리이다.
- https://github.com/Mobius1/Pageable 이 깃허브를 참고하면 된다.
- data-anchor="Page 1" 으로 해당하는 페이지를 지정하면 묶어서 pageable된다.
- 라이브러리를 적용하고 나의 css를 꺼보면서 문제가 생기면 css를 수정해야한다.
- css 링크와 js를 넣어주면 된다. (한 세트씩 존재) -> 아래는 aos를 같이 넣어서 파일이 2개씩이다.
```html
<body>
    <!-- 전체 화면 영역 -->
<div class="container">
    <!-- 각 페이지를 담당하는 영역 -->
    <div data-anchor="Page 1">
        <div class="page page1 video-background">
            <video src="assets/media/intro.mp4" autoplay muted loop></video>
            <div class="video-overlay">
                <h1 data-aos="fade-up" data-aos-duration="500">Hello Wrold</h1>
                <p data-aos="fade-up" data-aos-duration="500" data-aos-delay="300">Video Background Example</p>
            </div>
        </div>
    </div>
    <div data-anchor="Page 2">
        <div class="page page2">
            <h1>Page2</h1>
        </div>
    </div>
    <div data-anchor="Page 3">
        <div class="page page3">
            <h1>Page3</h1>
        </div>
    </div>
    <div data-anchor="Page 4">
        <div class="page page4">
            <h1>Page4</h1>
        </div>
    </div>
    <div data-anchor="Page 5">
        <div class="page page5">
            <h1>Page5</h1>
        </div>
    </div>
</div>
<script src="https://unpkg.com/pageable@latest/dist/pageable.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js"></script>
<script>
    // pageable 가동
    new Pageable(".container");
    // AOS 라이브러리 동작 시작
    AOS.init();
</script>
</body>
```