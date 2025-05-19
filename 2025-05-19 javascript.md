# 📌 1. html, css 제어 기본
### 📌 1-1. 이벤트 객체를 핸들링하여 css 값 바꾸기
- 핸들러 = 이벤트 발생 시 실행될 함수
- e = 이벤트 객체 = 브라우저가 이벤트(클릭, 키 입력, 폼 제출 등)를 처리할 때 자동으로 생성하여 핸들러에 전달하는 자바스크립트 객체
- html 객체들은 모두 이벤트 -> [핸들러 배열]을 모아둔 리스트를 갖는다.
- 이벤트 객체의 구성
```js
element.addEventListener('click', function(e) {
  console.log(e.type);            // 이벤트 종류 ("click")
  console.log(e.target);          // 실제 발생 요소
  console.log(e.currentTarget);   // 핸들러가 붙은 요소
  console.log(e.defaultPrevented);// preventDefault() 호출 여부
  console.log(e.timeStamp);       // 이벤트 발생 시각 (ms)
});
```
- 브라우저가 마우스 클릭, 키 입력 등 이벤트를 감지 
- -> 이벤트 객체(Event)를 생성 
- -> 캡처링 단계: 최상위 문서부터 이벤트가 내려옴 
- -> 타겟 단계: 실제 이벤트가 발생한 요소 도착 
- -> 버블링 단계: 다시 최상위로 전파 
- -> 등록된 핸들러가 있으면 이 객체를 인자로 받아 함수 호출 
- -> 전파가 끝나면 이벤트 객체는 더 이상 참조되지 않아 가비지 컬렉션 대상이 됨

#### 이벤트 발생 3 단계 이해하기
- 캡처링(Capturing) 단계
window → document → html → body → … → 타겟 요소 순으로 “내려오며” 이벤트를 감지한다.
이때 addEventListener의 세 번째 인자로 true를 주면, 캡처링 단계에서 핸들러가 실행된다.
- 타겟(Target) 단계
실제 이벤트가 발생한 요소에서 “한 번” 실행된다.
기본값(capture: false)인 addEventListener는 이 타겟 단계부터 실행된다.
- 버블링(Bubbling) 단계
타겟에서 실행된 후 → 부모 요소 → 조상 요소 순으로 “올라가며” 실행된다.
- 아래는 클릭한 링크의 정보로 viewer의 정보를 바꾸는 예제이다.
```html
<body>
        <ul class="img-list">
            <li><a href="img/img01.jpg" title="테스트 이미지 1" class="link"><img src="img/img01.jpg" /></a></li>
            <li><a href="img/img02.jpg" title="테스트 이미지 2" class="link"><img src="img/img02.jpg" /></a></li>
            <li><a href="img/img03.jpg" title="테스트 이미지 3" class="link"><img src="img/img03.jpg" /></a></li>
            <li><a href="img/img04.jpg" title="테스트 이미지 4" class="link"><img src="img/img04.jpg" /></a></li>
            <li><a href="img/img05.jpg" title="테스트 이미지 5" class="link"><img src="img/img05.jpg" /></a></li>
        </ul>
        
        <div class="viewer">
            <img src="img/img01.jpg" id="target" />
        </div>

        <script>
            document.querySelectorAll(".link").forEach((v, i) => {
                v.addEventListener("click", e => {
                    e.preventDefault();

                    const src = e.currentTarget.getAttribute("href");
                    const title = e.currentTarget.getAttribute("title");

                    const target = document.querySelector("#target");
                    target.setAttribute("src", src);
                    target.setAttribute("alt", title);
                });
            });
        </script>
        </body>
```

### 📌 1-2. css와 클래스 변경하기
- inline 스타일은 외부 CSS나 <style> 안의 규칙보다 우선순위가 높다. 이때 JS로 조작한 .style은 마치 HTML에 style="width:auto;"를 직접 쓴 것처럼 브라우저가 알아서 삽입하여 동작하므로 우선적으로 실행된다. => .style은 삽입까지가 기능이다.
- 클래스 이름을 js에서 add나 remove로 넘길떄는 .을 빼고 넘긴다.
- togle은 class가 있으면 추가하고 없으면 넣는다. -> 아래 예제에서 togle을 두 개 사용하여 클릭할때마다 클래스가 바뀌는 것을 구현하였다.
- 이벤트 객체를 사용하지 않으면 굳이 인자로 넣지 않아도 된다.
```html
<body>
    <div id="box" class="box1">
        <h1>테스트 영역 입니다.</h1>
    </div>
    <input type="button" id="btn1"  value="(폰트) red" />
    <input type="button" id="btn2"  value="(폰트) green" />
    <input type="button" id="btn3"  value="(폰트) blue" />
    <input type="button" id="btn4"  value="(배경) red" />
    <input type="button" id="btn5"  value="(배경) green" />
    <input type="button" id="btn6"  value="(배경) blue" />
    <input type="button" id="btn7"  value="width=50%" />
    <input type="button" id="btn8"  value="width=auto" />
    <input type="button" id="btn9"  value="box1 클래스 적용" />
    <input type="button" id="btn10" value="box2 클래스 적용" />

    <script>
        // js 객체로 가져온 html 요소는 모두 style이라는 프로퍼티를 내장하고 이는 모든 css 스타일이 카멜 표기법으로 저장되어 있다.
        document.querySelector('#btn1').addEventListener('click', e => document.querySelector('#box').style.color = '#f00');
        document.querySelector('#btn2').addEventListener('click', e => document.querySelector('#box').style.color = '#0f0');
        document.querySelector('#btn3').addEventListener('click', e => document.querySelector('#box').style.color = 'red');
        document.querySelector('#btn4').addEventListener('click', e => document.querySelector('#box').style.color = 'green');
        document.querySelector('#btn5').addEventListener('click', e => document.querySelector('#box').style.color = 'blue');
        document.querySelector('#btn6').addEventListener('click', e => document.querySelector('#box').style.color = '#00f');
        document.querySelector('#btn7').addEventListener('click', e => document.querySelector('#box').style.width = '50%');
        document.querySelector('#btn8').addEventListener('click', e => document.querySelector('#box').style.width = 'auto');

        // 클릭할때마다 클래스가 바뀜
        document.querySelector('#btn9').addEventListener('click', () => {
            box.classList.toggle('box1');
            box.classList.toggle('box2');
        });

        document.querySelector('#btn10').addEventListener('click', e => {
            const box = document.querySelector('#box');
            box.classList.add('box2');
            box.classList.remove('box1');
        });
    </script>
</body>
```

### 📌 1-3. dataset활용 (dataset은 data-로 시작하는 모든 속성을 담은 map이다.)
- HTMLElement.dataset는 해당 요소에 **data-로 시작하는 모든 사용자 정의 속성(data attributes)**을 키-값 쌍으로 담고 있는 DOMStringMap 객체를 가리킨다.
- '*[data-color]'는 CSS 선택자(selector) 문법으로, 모든 요소 중에서(*) data-color라는 속성(attribute)을 가진 요소를 모두 선택하라는 뜻이다.
```html
<!DOCTYPE html>
<body>
    <button type="button" class="mybtn" data-name="javascript" data-age="20" data-color="#f60" data-background="#060">javascript;20</button>
    <button type="button" class="mybtn" data-name="vanilla" data-age="15" data-color="#06f" data-background="#990">vanilla;15</button>

    <h1 id="console"></h1>

    <script>
        document.querySelectorAll('.mybtn').forEach((v,i) => {
            v.addEventListener('click', e => {
                // html 태그에 존재하지 않는 속성을 js로 추가할 수 있다.
                e.currentTarget.dataset.helloworld = '안녕하세요';
                const name = e.currentTarget.dataset.name;
                const age = e.currentTarget.dataset.age;
                document.getElementById('console').innerHTML = '이름: ' + name + ', 나이: ' + age;
            });
        });

        // 미리 데이터에 설정해둔 색으로 데이터 변경하기
        document.querySelectorAll('*[data-color]').forEach((v, i) => {
            v.style.color = v.dataset.color;
        });

        document.querySelectorAll('*[data-backgrund]').forEach((v, i) => {
            v.style.backgrundColor = v.dataset.backgroundColor;
        })
    </script>
</body>
```

### 📌 1-4. 메뉴 탭 만들기 (active class를 현재 위치에만 존재하게 하면서 효과 옮기기)
- outline: none; — 외곽선(포커스 링) 제거하기
- transition 은 CSS 속성이 '변경될 때' 애니메이션 효과를 줄 수 있는 단축 속성이다.
- querySelectorAll에서는 클래스 이름을 전달할때 '.tab-page' 와 같이 점을 찍어서 줘야한다.
- classList: class 속성에 포함된 CSS 클래스 목록을 조작하기 위한 DOMTokenList 객체
- 위 객체는 배열처럼 인덱스로 접근할 수 있고, .length 프로퍼티를 가진다.
```html
<body>
        <div id="tab-container">
            <div class="tab-button-group">
            <a class="tab-button active" href="#newyork">NewYork</a>
            <a class="tab-button" href="#london">London</a>
            <a class="tab-button" href="#paris">Paris</a>
            <a class="tab-button" href="#seoul">Seoul</a>
            </div>
        
            <div id="newyork" class="tab-page active">
            <h3>NewYork</h3>
            <p>NewYork is the capital city of US.</p>
            </div>
        
            <div id="london" class="tab-page">
            <h3>London</h3>
            <p>London is the capital of England.</p>
            </div>
        
            <div id="paris" class="tab-page">
            <h3>Paris</h3>
            <p>Paris is the capital of France.</p>
            </div>
        
            <div id="seoul" class="tab-page">
            <h3>Seoul</h3>
            <p>Seoul is the capital of Korea.</p>
            </div>
        </div>
        
        <script>
            document.querySelectorAll('.tab-button').forEach((v, i) => {

                v.addEventListener('click', e => {
                    const currentIndex = i;
                    const href = e.currentTarget.getAttribute('href');

                    document.querySelectorAll('.tab-button').forEach((v1, i1) => {
                        if (currentIndex == i1) {
                            v1.classList.add('active');
                        }

                        else {
                            v1.classList.remove('active');
                        }
                    });

                    // 인덱스로 제어하는 것이 통일성 있지만 여기서는 최대한 다양한 방법으로 접근해보았다.
                    document.querySelectorAll('.tab-page').forEach((v2, i2) => {
                        v2.classList.remove('active');
                    });

                    document.querySelector(href).classList.add('active');
                });

            });
        </script>
</body>
</html>
```

### 📌 1-5. interval로 banner 변경하기
- setInterval을 통해 인덱스를 올려가면서 배열에 있는 이미지와 링크를 차례로 하나의 박스에 할당하기
```html
<!DOCTYPE html>
<html lang="ko" translate="no">
<head>
    <meta charset="UTF-8">
    <meta name="google" content="nottranslate" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>banner</title>
</head>
<body>
    <a href="https://www.naver.com" id="bannerLink"><img src="img1.html" id="bannerImg" width="200"></a>

        <script>
            // 출력할 이미지 경로들
            const imgList = ['img/1.png', 'img/2.jpg', 'img/3.jpg'];
            const urlList = ['https://www.naver.com', 'https://www.daum.net', 'https://www.google.com']
        
            // 현재 출력하고 있는 이미지의 인덱스
            let currentIndex = 0;
        
            setInterval(() => {
            document.querySelector('#bannerImg').setAttribute('src', imgList[currentIndex]);
            document.querySelector('#bannerLink').setAttribute('href', urlList[currentIndex]);
            // currentIndex++;
            // if (currentIndex >= imgList.length) {
            //   currentIndex = 0;
            // }
            currentIndex = (currentIndex + 1) % imgList.length;
            }, 1000);
        </script>
</body>
</html>
```

# 📌 2. form요소
- form은 action 태그를 통해 내부에 얻은 값을 다른 웹사이트로 전송한다.
- queryString: 변수에 url이 포함된 값이다. (서버나 클라이언트 쪽에서 추가 데이터를 전달할 때 사용)
- 쿼리 스트링 문법: 시작 기호: ?, 키=값 쌍: key=value, 구분자: &
```ruby
[프로토콜]://[호스트]/[경로]?[쿼리스트링]#[해시]
```
- form 태그의 역할
- method="get": URL에 쿼리스트링(?key=value…)으로 데이터를 붙여 전송
- method="post": HTTP 요청의 본문에 데이터를 담아서 전송
- 빈요소 슬래시 태그: 슬래시는 과거 호환성과 가독성을 위해 남아있는 표기이며, HTML5에선 없어도 됨
- id—문서 내에서 유일한 식별자
- name—폼 데이터 전송을 위한 키 (id**는 전송되지 않는다. **name**만 폼 데이터에 포함된다.)
- for="username"은 id="username"인 요소를 가리킨다.

### 📌 2-1. 폼에 입력받고 링크로 정보보내기
- if와 return; 으로 끊어가도 되는데 일단 if else로 바꿨다.
- if, return으로 블록을 줄이는게 가독성에 좋다고는 한다. 또 이 방식은 검증 함수 하나마다 if … return을 독립적으로 추가하기가 쉽다.
- 또한 if, return은 완전한 중단을 보장하지만 else문은 조건을 잘못 설정했을 때 잘못하면 실행될 수 있다.
```html
<body>
    <form id="myform" action="https://www.naver.com">
        <div>
            <label for="username">사용자 이름</label>
            <input type="text" name="username" id="username" />
        </div>
        <div>
            <label for="userpass">비밀번호</label>
            <input type="password" name="userpass" id="userpass" />
        </div>

        <!-- backend에 입력값을 전송하는 버튼 -->
        <button type="submit" id="btn">입력값 확인</button>
        <hr>

        <!-- 선택결과를 표시할 div -->
        <div id="result"></div>
    </form>

    <script type="text/javascript">
        const myform = document.querySelector('#myform');

        myform.addEventListener('submit', e => {
            // 값 다 입력 안됐는데 전송되면 안되니까 일단 막음.
            e.preventDefault()

            const username = document.querySelector('#username');
            const userpass = document.querySelector('#userpass');

            if (!username.value) {
                alert("사용자 이름을 입력하세요");
                // 커서 이동시킴
                username.focus();
            }

            else if (!userpass.value) {
                alert("비밀번호를 입력하세요");
                userpass.focus();
            }

            else {
                document.querySelector('#result').innerHTML = '사용자 이름: ' + username.value + '<br>비밀번호: ' + userpass.value;
                // 중단 시켜 놓은 원래 기능을 무시하고 전송
                e.currentTarget.submit();
            }
        });
    </script>
</body>
```
- if와 return; 같이 쓰기 이러면 이 시점에서 바로 중단되어서 깔끔하다.
```js
if (!username.value) {
        alert("사용자 이름을 입력하세요");
        // 커서 이동시킴
        username.focus();
        return ;
    }
```

### 📌 2-2. 드롭다운에서 선택된 값 표시하기
```js
<body>
<form id="myform">
    <div>
        <label for="subject">과목</label>
        <select name="subject" id="subject">
            <option value="">--- 선택하세요 ---</option>
            <option value="html">HTML</option>
            <option value="css">CSS</option>
            <option value="javascript">JAVASCRIPT</option>
        </select>
    </div>
    <button type="submit">입력값 확인</button>
    <hr>

    <div id="result"></div>
</form>

<script type="text/javascript">
    document.querySelector('#myform').addEventListener('submit', e => {
        e.preventDefault();

        const dropdown = document.querySelector('#subject');
        const choose = dropdown.selectedIndex;

        if (choose == 0) {
            alert('선택된 항목이 없습니다.');
            return ;
        }

        const value = dropdown[choose].value;
        document.querySelector('#result').innerHTML = value;
    });
    
</script>
</body>
```

### 📌 2-3. 값이 바뀔 때 특정 효과를 발생시키기
- type="text/javascript는 코드의 종류를 브라우저에 알려주기 위한 용도였으나 html4까지는 필수였다가 현재는 기본 값이 되어서 더 이상 신경쓰지 않아도 된다.
- 실시간으로 화면에 표시하기 위해서는 웬만하면 keyup이벤트를 사용한다.
- readonly: 읽기 전용 input, backend에 전송을 한다.
- select 내부 option으로 드롭다운을 나타낸다. 즉 전체 객체를 가져와서 그 내부 객체에 접근하기 위해서는 인덱스를 가져와야한다.
- selectedIndex는 HTML의 <select> 요소에서 **현재 선택된 옵션(option)의 인덱스(순서 번호)**를 반환한다.
```html
<body>
<select name="site" id="site">
    <option value="">--- 선택하세요 ---</option>
    <option value="http://www.naver.com">네이버</option>
    <option value="http://www.daum.net">다음</option>
    <option value="http://www.google.com">구글</option>
</select>

<hr>

<input type="text" id="src">
<input type="text" id="dsc" readonly> 

<hr>

<input type="text" id="keycheck">
<p id="keycopy"></p>

<script type="text/javascript">
    // 내부에 트리구조가 형성되어있으므로 e.currentTarget 자체는 인덱스로 접근 가능한 like 배열 객체이다.
    document.querySelector('#site').addEventListener('change', e => {
        const value = e.currentTarget[e.currentTarget.selectedIndex].value;

        if (value) {
            window.open(value);
        }
    });

    document.querySelector('#src').addEventListener('change', e => {
        document.querySelector('#dsc').value = e.currentTarget.value;
    });

    // 실시간으로 화면에 표시하기 위해서는 keyup이벤트를 사용한다.
    document.querySelector('#keycheck').addEventListener('keyup', e => {
        document.querySelector('#keycopy').innerHTML = e.currentTarget.value;
    });

</script>
</body>
```

### 📌 2-4. 라디오 버튼 제어
- cheked 속성을 잘 활용하여 제어한다.
- Array.from(radio)으로 해당 nodeLinked 객체를 array 객체로 만든다.
```html
<body>
    <form id="myform">
        <label><input type="radio" name="subject" value="html" /> HTML</label>
        <label><input type="radio" name="subject" value="css" /> CSS</label>
        <label><input type="radio" name="subject" value="javascript" /> JavaScript</label>
        <button type="button" id="btn">입력값 확인</button>
    </form>

    <hr>

    <p id="console"></p>

    <script type="text/javascript">
        // name이 subject인 input을 모았는데 이는 nodeList 객체로 반환되고 forEach 이외의 메서드를 사용할 수 없어 값을 배열로 바꿔줘야 한다.
        const radio = document.querySelectorAll("input[name='subject']");

        // 실시간으로 누른값을 보여줌
        radio.forEach((v, i) => {
            v.addEventListener('change', e => {
                document.querySelector("#console").innerHTML = e.currentTarget.value;
            });
        });

        // 전송버튼이 눌러진 경우의 처리
        document.querySelector('#btn').addEventListener('click', e => {
            Array.from(radio).some((v, i) => {
                if (v.checked) {
                    document.querySelector('#console').innerHTML = i + '번째 항목 ' + v.value + '이(가) 선택됨';
                    return true;
                }
            });
        });
    </script>
</body>
```

### 📌 2-5. 체크 박스 선택 시, 버튼 눌렀을 때 역할 정의하기
- filter와 map을 활용하여 선택된 체크박스만 모아서 그 벨류값을 뽑기. 이는 input에 정의한 value를 의미한다.
```html
<body>
    <form id="myform">
        <label><input type="checkbox" class="hobby" value="soccor" />축구</label>
        <label><input type="checkbox" class="hobby" value="basketball" />농구</label>
        <label><input type="checkbox" class="hobby" value="baseball" />야구</label>
        <button type="button" id="btn">입력값 확인</button>
    </form>

    <hr />

    <p id="console"></p>

    <script type="text/javascript">
    // 3개의 input 태그를 모아 NodeList객체로 변환
    const checkbox = document.querySelectorAll(".hobby");

    // 체크 여부에 따라 다른 값을 console에 넣음.
    checkbox.forEach((v, i) => {
        v.addEventListener("change", e => {
            const div = document.querySelector("#console");
            div.innerHTML = e.currentTarget.value;
            div.innerHTML += e.currentTarget.checked ? " : 체크됨" : " : 체크 해제됨";
        });
    });

    // 버튼이 눌린 경우의 처리
    document.querySelector("#btn").addEventListener("click", e => {
        const checkedValue = Array.from(checkbox).filter((v, i) => v.checked).map((v, i) => v.value);
        document.querySelector("#console").innerHTML = checkedValue;
    });
    </script>
</body>
```

### 📌 2-6. 전체선택 자동화
- "input[data-checked]"의 작동: "<input>이면서 data-checked 속성이 있는” 요소면 모두 선택
- const targetSelector = current.dataset.checked; : data-옆에 checked인 속성의 값을 리턴한다.
```html
<body>
        <hr />
        <label>전체선택<input type="checkbox" id="all_check" data-checked=".hobby" /></label>
        <hr />
        <label><input type="checkbox" class="hobby" value="soccor" />축구</label>
        <label><input type="checkbox" class="hobby" value="basketball" />농구</label>
        <label><input type="checkbox" class="hobby" value="baseball" />야구</label>
        <hr />

    <br />

        <hr />
        <label>전체선택<input type="checkbox" id="all_check2" data-checked=".food" /></label>
        <hr />
        <label><input type="checkbox" class="food" value="a" />a</label>
        <label><input type="checkbox" class="food" value="b" />b</label>
        <label><input type="checkbox" class="food" value="c" />c</label>
        <hr />

    <script type="text/javascript">

        /** data-checked 속성을 개발자가 정의하여 자동화 할 경우 */
        document.querySelectorAll("input[data-checked]").forEach((v, i) => {
        v.addEventListener('change', e => {
                const current = e.currentTarget; // data-checked가 가능한 input태그(전체선택을 선택) 중 하나
                const targetSelector = current.dataset.checked; // data-checked에 할당된 값
                document.querySelectorAll(targetSelector).forEach((v2, i2) => { // data-checked에 할당된 값을 클래스 이름으로 가지면 모두 같은 체크상태로 만듦
                    v2.checked = current.checked;
                });
            });
        });
    </script>
</body>
```

### 📌 2-7. focus가 갔을 때 특정 효과 적용하기
- focus() 함수는 특정 항목에 입력커서를 할당하는 기능.
- focus 이벤트는 특정 항목에 입력커서가 할당되었을 때 동작하는 이벤트
- blur 이벤트는 특정 항목에서 입력커서가 빠져나왔을 때 동작하는 이벤트 → focus의 반대
```html
<body>
    <form id="myform">
        <h3>주민번호를 입력하세요</h3>
        <input type="text" name="jumin1" id="jumin1" class="jumin" />
        <input type="password" name="jumin2" id="jumin2" class="jumin" />
    </form>
    
        <script type="text/javascript">
        // focus() 함수는 특정 항목에 입력커서를 할당하는 기능.
        // focus 이벤트는 특정 항목에 입력커서가 할당되었을 때 동작하는 이벤트
        // blur 이벤트는 특정 항목에서 입력커서가 빠져나왔을 때 동작하는 이벤트 → focus의 반대
        document.querySelectorAll('.jumin').forEach((v, i) => {
            v.addEventListener('focus', e => {
                e.currentTarget.style.backgroundColor = '#06f';
                e.currentTarget.style.color = '#fff';
            });
    
            v.addEventListener('blur', e => {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.color = '#000';
            });
        });
    
            // 첫 번째 입력항목에 대한 독립적 이벤트
            document.querySelector('#jumin1').addEventListener('keyup', e => {
            // 키보드를 누를 때마다 스스로의 입력값을 가져옴
            const value = e.currentTarget.value;
    
            if (value.length >= 6) {
                // 스스로의 입력값을 6글자만 남겨놓고 제거
                e.currentTarget.value = value.substring(0, 6);
                document.querySelector('#jumin2').focus();
            }
        });
        </script>
</body>
```

### 📌 2-8. disabled를 활용하여 checked되었을때 입력받기
- input에 걸 수 있는 속성 값
- disabled => 비활성=true, 활성=false (모든 input 요소)
- readonly => 읽기전용=true, 읽기,쓰기 겸용=false (모든 input 요소)
- checked => 체크됨=true, 체크안됨=false (체크박스, 라디오 버튼)
- selected => 선택됨=true, 선택해제=false (dropdown의 option태그)
```html
<style>
        /* disabled 속성을 갖는 요소의 배경색상 처리 */
        input[disabled] {
            background-color: #d5d5d5;
        }
    </style>
</head>
<body>
    <label for="username"> 입력하기 <input type="checkbox" id="input_enable" /> </label>
    <input type="text" name="input" id="input" disabled />

    <script type="text/javascript">
        /**
         * attribute --> 값을 갖는 속성. setAttribute, getAttribute 등의 메서드로 제어함.
         *   ex) src, href, width, height 등
         * property --> 값을 갖지 않는 속성. 각 속성 자체가 객체의 멤버변수로 존재하고 true/false의 값을 갖는다.
         *   ex) checked, readonly, selected 등
         */
        document.querySelector("#input_enable").addEventListener("change", e => {
            document.querySelector("#input").disabled = !e.currentTarget.checked;
        });
    </script>
</body>
```

# 📌 3. 브라우저 관련 기능

### 📌 3-1. window open의 3가지 파라미터
- window.open을 통해 특정 파일을 윈도우 창에 열 수 있다.
- window.open(url, name, features)
- url : 열고자 하는 페이지 주소
- name : 새 창의 고유 이름 (같은 이름이면 기존 창을 재활용)
- features : UI 요소 및 크기·위치 등을 정의하는 문자열

| 옵션 이름        | 설명                                       | 값          |
| ------------ | ---------------------------------------- | ---------- |
| `scrollbars` | 창 안 콘텐츠가 넘칠 때 스크롤바(수직·수평)를 표시할지 결정       | `yes`/`no` |
| `toolbar`    | 뒤로 가기·앞으로 가기·새로 고침 등 브라우저 기본 툴바를 표시할지 결정 | `yes`/`no` |
| `menubar`    | 파일·편집·보기 등 브라우저 상단 메뉴바를 표시할지 결정          | `yes`/`no` |
| `status`     | 창 하단 상태 표시줄(status bar)을 표시할지 결정         | `yes`/`no` |
| `location`   | 주소 표시줄(location bar)을 표시할지 결정            | `yes`/`no` |

- window.close(): 열렸던 창을 닫는다.
- open.html
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
</head>
<body>
    <h1>새로 열린 창</h1>
    <p>이 페이지는 팝업창으로 사용될 샘플 페이지</p>
    <hr />
    <div>
        <a href="#" id="close">창 닫기</a>
    </div>

    <script>
        document.querySelector("#close").addEventListener("click", e => {
            e.preventDefault();
            window.close();
        });
    </script>
</body>
</html>
```
- 3가지 파리미터
```html
<body>
    <h1>window 객체</h1>
    <h3>open 메소드 확인</h3>
    <div>
        <a href="#" id="link1">새 창 열기</a>
        <br />
        <a href="#" id="link2">팝업 창 열기(1)</a>
        <br />
        <a href="#" id="link3">팝업 창 열기(2-1)</a>
        <br />
        <a href="#" id="link4">팝업 창 열기(2-2)</a>
        <br />
        <!-- 다음 예제 진행용 링크(이 예제와 연관 없음) -->
        <a href="02-history.html">일반 링크</a>
    </div>

    <script type="text/javascript">
        document.querySelector('#link1').addEventListener('click', e => {
            e.preventDefault();
            /** 새 창(혹은 탭) 띄우기 */
            window.open('open.html');
        });

        document.querySelector('#link2').addEventListener('click', e => {
            e.preventDefault();

            /** 클릭할 때 마다 창이 새로 열리는 팝업창 */
            // 두 번째 파라미터인 창 이름이 빈 문자열이므로, 매번 새로운 팝업창을 생성한다.
            // location 옵션은 피싱 사이트를 방지하기 위해 브라우저 개발자들이
            // 담당하여 지원하지 않고 있다.
            const popup = window.open('open.html', '', 'width=300, height=500, scrollbars=no, toolbar=no, menubar=no, status=no, location=no');

            // 팝업창이 차단된 경우
            if (!popup) {
                alert('팝업 차단을 해제해 주세요.');
            } else {
                popup.focus();
            }
        });

        document.querySelector('#link3').addEventListener('click', e => {
            e.preventDefault();
            // #link4가 눌렸을 때 호출되는 팝창과 창 이름이 동일하므로,
            // 같은 창을 공유한다.
            window.open('https://www.naver.com', 'mywin', 'width=500, height=300, scrollbars=no, toolbar=no, menubar=no, status=no, location=no');
        });

        document.querySelector('#link4').addEventListener('click', e => {
            e.preventDefault();
            window.open('https://www.daum.net', 'mywin', 'width=500, height=300, scrollbars=no, toolbar=no, menubar=no, status=no, location=no');
        });
    </script>
</body>
```

### 📌 3-2. 페이지 이동과 window.location
- location 객체: 현재 로드된 문서의 URL 정보를 관리한다.
```html
<body>
    <h1>History 객체</h1>
    <h2 id="datetime"></h2>
    <a href="#" id="link1">이전 페이지로 이동</a>
    <a href="#" id="link2">앞 페이지로 이동</a>

    <hr />

    <a href="01-window.html">1번 예제로 이동</a>
    <button type="button" id="move">1번 예제로 이동</button>
    <button type="button" id="refresh">페이지 새로 고침</button>

    <script>
        // 1) 현재 시각을 #datetime 요소에 출력
        document.querySelector("#datetime").innerHTML = new Date();

        // 2) 버튼 클릭 시 01-window.html로 이동
        document.querySelector("#move").addEventListener("click", e => {
            e.preventDefault();
            // 아래 두 줄은 동일한 동작을 함
            // window.location.href = '01-window.html';
            window.location = '01-window.html';
        });

        // 3) 버튼 클릭 시 페이지 새로 고침
        document.querySelector("#refresh").addEventListener("click", e => {
            e.preventDefault();
            window.location.reload();
        });

        // 4) ‘이전 페이지로 이동’ 링크 클릭 시 히스토리 뒤로 가기
        document.querySelector("#link1").addEventListener("click", e => {
            e.preventDefault();
            history.back();
        });

        // 5) ‘앞 페이지로 이동’ 링크 클릭 시 히스토리 앞으로 가기
        document.querySelector("#link2").addEventListener("click", e => {
            e.preventDefault();
            history.forward();
        });
    </script>
</body>
```
