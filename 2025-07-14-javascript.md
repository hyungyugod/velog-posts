# 📌 0. jQuery form 객체 활용
### 📌 0-1. form 값 제출과 활용
- username.val() 은 해당 선택자가 붙은 객체에 입력되어있는 value 값을 가져온다.
- $(e.currentTarget).off("submit").submit(); : 현재 타겟에서 바로 submit을 보내면 일반 js와 달리 이벤트가 다시 발동되므로 on 뒤에 off를 사용해주고 submit을 호출해야한다.
```html
<form id="myform">
        <div>
            <label for="username">사용자이름</label>
            <input type="text" name="username" id="username" />
        </div>
        <div>
            <label for="userpass">비밀번호</label>
            <input type="password" name="userpass" id="userpass" />
        </div>
        <!-- Backend에 입력값을 전송하는 버튼 -->
        <button type="submit" id="btn">입력값 확인</button>
        <hr />
        <!-- 선택결과를 표시할 div -->
        <div id="result"></div>
    </form>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script type="text/javascript">
        $("#myform").on("submit", e => {
            e.preventDefault();

            const username = $("#username");
            const userpass = $("#userpass");

            if (!username.val()) {
                alert("사용자 이름을 입력하세요.");
                username.focus();
                return;
            }

            if (!userpass.val()) {
                alert("비밀번호를 입력하세요.");
                userpass.focus();
                return;
            }

            // 모든 타운을 통과했다면 입력 내용을 #result에 출력
            const result = $("#result");
            result.html(`사용자이름: ${username.val()}, 비밀번호: ${userpass.val()}`);

            // 폼의 submit 이벤트를 제거하고, 강제 전송
            // [중요!] submit 이벤트를 제거하지 않으면 강제 전송시에 이벤트 핸들러가 다시 호출되기 때문에 무한루프에 빠진다.
            $(e.currentTarget).off("submit").submit();
        });
    </script>
```

### 📌 0-2. focus와 blur
- focus는 input 태그에 포커스가 갔을때를 의미한다. 
- blur는 input 태그에서 포커스가 빠져나왔을 때를 의미한다. -> 초점이 갔다가 초점이 흐려진다는 뜻이다.
```html
<form id="myform">
    <h3>주민번호를 입력하세요</h3>
    <input type="text" name="jumin1" id="jumin1" class="jumin" maxlength="6" />
    -
    <input type="text" name="jumin2" id="jumin2" class="jumin" maxlength="7" />
</form>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script>
    $('.jumin').on('focus', e => {
        e.currentTarget.style.backgroundColor = '#ffffcc';  
    });

    $('.jumin').on('blur', e => {
        e.currentTarget.style.backgroundColor = '#000';
    });
</script>
```

### 📌 0-3. change 이벤트에 대하여
- change 이벤트는 select(드롭다운)에서 선택값이 바뀌고, 그 바뀐 값이 실제로 적용된 "이후"에 발생한다.
- 즉 사용자가 드롭다운의 항목을 클릭하거나 방향키로 바꾸고 최종적으로 변경을 확정한 뒤에 (즉, 이미 값이 바뀐 상태) 이벤트가 실행된다.
- 이를 활용하여 새로 바뀐 값에 대해서 새로운 처리를 해줄 수 있다.
- window.open(choose); : 내부에 전달한 파라미터 url로 새 창을 띄운다.
```html
<label for="subject">과목</label>
<select id="my-dropdown">
    <option value="">---선택하세요---</option>
    <option value="http://www.naver.com">네이버</option>
    <option value="http://www.daum.net">다음</option>
    <option value="http://www.google.com">구글</option>
</select>
<button type="button" id="my-button">사이트 열기</button>

<div id="result"></div>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script>
    $("my-dropdown").on("change", e => {
        const value = $(e.currentTarget).val();
        const index = $(e.currentTarget).prop("selectedIndex");
        $("#result").html(`선택된 값: ${value}, 선택된 인덱스: ${index}`);
    });

    document.querySelector("#my-button").addEventListener("click", e => {
        const dropdown = $("#my-dropdown");
        const choose = dropdown.val();
        if (choose) {
            window.open(choose);
        }
    });
</script>
```

### 📌 0-4. 라디오 버튼 구현
- 라디오 버튼에서 값이 선택될때마다 콘솔 div에 입력되는 값을 바꾼다.
```html
<form id="myform">
    <label><input type="radio" name="subject" value="html" />HTML</label>
    <label><input type="radio" name="subject" value="css" />CSS</label>
    <label><input type="radio" name="subject" value="javascript" />Javascript</label>
    <button type="button" id="btn">입력값 확인</button>
</form>

<hr />

<p id="console"></p>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script type="text/javascript">
    $("input[name='subject']").on('change', (e) => {
        // 선택된 radio의 value값을 #console에 출력
        const checked = $("input[name='subject']:checked");
        $("#console").html(`라디오 change 이벤트: ${checked.val()}(이)가 선택됨`);
    });

    // 전송 버튼이 눌러진 경우의 처리
    $("#btn").on("click", e => {
        // 선택된 radio 객체
        const checked = $("input[name='subject']:checked");
        $("#console").html(`버튼 click 이벤트: ${checked.val()}(이)가 선택됨`);
    });
</script>
```

### 📌 0-5. 체크박스
- prop은 프로퍼티를 의미한다.
- 체크박스들 중에 선택된 값들을 배열로 만들고 배열에 map을 사용하여 그 값들만 따로 가져온다.
- 이후 join을 통해 ,로 이어붙인다.
```html
<form id="myform">
    <label><input type="checkbox" class="hobby" value="soccor" />축구</label>
    <label><input type="checkbox" class="hobby" value="basketball" />농구</label>
    <label><input type="checkbox" class="hobby" value="baseball" />야구</label>
    <button type="button" id="btn">입력값 확인</button>
</form>

<hr />

<p id="console"></p>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script type="text/javascript">
    // 선택 항목이 변경되었을 경우의 이벤트 처리
    $(".hobby").on('change', e => {
        const div = $("#console");
        const current = $(e.currentTarget);
        div.html(current.value);
        div.html(div.html() + (current.prop('checked') ? " 체크됨" : " 체크 해제됨"));
    });

    // 버튼이 눌러진 경우의 처리
    $("#btn").on("click", e => {
        // 선택된 체크박스 객체로 생성
        const checkedItem = $(".hobby:checked");

        // 선택 항목의 체크박스 배열에서 value값을 추출
        const checkedValue = Array.from(checkedItem).map((v, i) => $(v).val());

        // 배열의 원소 사이에 ","를 포함하여 하나의 문자열로 결합 후 출력
        $("#console").html(`선택항목: ${checkedValue.join(", ")}`);
    });
</script>
```

### 📌 0-6. prop의 두 인자로 값 복사하기 
- current.prop('checked') : 현재 클릭된 체크박스가 체크되어 있으면 true, 아니면 false를 반환한다.
- prop('checked', 값) 체크드의 값을 두번째 인자와 똑같이 한다.
- 즉 다른 체크박스에 현재 체크박스의 상태를 복사해서 적용하게 된다.
```html
<label>전체선택<input type="checkbox" data-checked=".hobby" /></label>
<label><input type="checkbox" class="hobby" value="soccor" />축구</label>
<label><input type="checkbox" class="hobby" value="basketball" />농구</label>
<label><input type="checkbox" class="hobby" value="baseball" />야구</label>

<hr />

<label>전체선택<input type="checkbox" data-checked=".food" /></label>
<label><input type="checkbox" class="food" value="김치" />김치</label>
<label><input type="checkbox" class="food" value="불고기" />불고기</label>
<label><input type="checkbox" class="food" value="계란말이" />계란말이</label>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script type="text/javascript">
    $("input[data-checked]").on('change', e => {
        const current = $(e.currentTarget);
        const targetSelector = current.data('checked');
        $(targetSelector).prop('checked', current.prop('checked'));
    });
</script>
```

### 📌 0-7. disabled 속성을 체크박스 선택여부와 동기화 하기
- 'disabled' 속성을 checkbox.prop('checked')의 true, false로 결정한다.
```html
<div>
    <label for="username">이름 <input type="checkbox" data-disabled="#username" /></label>
    <input type="text" name="username" id="username" />
</div>
<div>
    <label for="email">이메일 <input type="checkbox" data-disabled="#email" /></label>
    <input type="email" name="email" id="email" />
</div>
<div>
    <label for="phone">연락처 <input type="checkbox" data-disabled="#phone" /></label>
    <input type="tel" name="phone" id="phone" />
</div>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script type="text/javascript">
    // 체크박스의 상태에 따라 대상 요소를 비활성화/활성화하는 함수
    // ---> 전달되는 파라미터는 jQuery 객체
    function disableCheck(checkbox) {
        const target = checkbox.data('disabled');
        $(target).prop('disabled', checkbox.prop('checked'));
    }

    const checkbox = $("input[data-disabled]");

    checkbox.each((i, v) => {
        disableCheck($(v));
    });

    checkbox.on('change', e => {
        const checkbox = $(e.currentTarget);
        disableCheck(checkbox);
    });
</script>
```

### 📌 0-8. 부모요소 선택자
- current.parent(); 은 부모요소를 선택한다.
- parent.css('background-color', color); jQuery에서는 이런식으로  css 속성을 추가할 수 있다.
- 같은 메커니즘으로 children도 가능하다.
```html
<script>
    /** 1) 부모 요소 찾기 */
    $('.find-parent').on('click', (e) => {
        e.preventDefault();
        const current = $(e.currentTarget);
        const color = current.data('color');

        // 부모요소
        const parent = current.parent();

        // 부모요소의 배경 색상을 변경
        parent.css('background-color', color);
    });

    /** 2) 조상 요소 찾기 */
    // 객체들의 수 만큼 반복처리
    $('.find-parents').on('click', (e) => {
        e.preventDefault();
        const current = $(e.currentTarget);
        const color = current.data('color');

        // 상위 요소들 중에서 주어진 selector를 충족하는 가장 가까운 요소를 검색
        const parents = current.parents('.list-group');

        // 검색된 조상 요소의 배경 색상을 변경
        parents.css('background-color', color);
    });
</script>
```

### 📌 0-9. 이전, 다음 선택자
- prev()를 통해 자신의 형제중에 바로 이전 요소를 선택할 수 있다.
- next()를 통해 자신의 형제중에 바로 다음 요소를 선택할 수 있다.
```html
<script>
        let size1 = 15;
        let size2 = 15;

        $('#btn1').on('click', (e) => {
            size1 += 5;
            // 자신의 '이전' 요소의 style변경
            $(e.currentTarget).prev().css('font-size', `${size1}px`);
        });

        $('#btn2').on('click', (e) => {
            size2 += 5;
            // 자신의 '다음' 요소의 style변경
            $(e.currentTarget).next().css('font-size', `${size2}px`);
        });
    </script>
```

### 📌 0-10. scrollHeight
- 'scrollHeight'는 스크롤이 포함된 전체 콘텐츠의 실제 높이(px) 를 의미하는 DOM property이다.
```html
<script>
    $('.collapsible-title').on('click', (e) => {
        const current = $(e.currentTarget);
        current.toggleClass('active');
        const content = current.next();
        const height = content.height();
        console.log(height);   // ---> 0 (단위 없음)
        if (!height) {
            const contentHeight = content.prop('scrollHeight'); // 실제 컨텐츠 높이
            console.log(contentHeight); // --> 실제 높이 출력(단위 없음, 정수)
            content.height(contentHeight); // 단위 설정 안함
        } else {
            content.height(0);
        }
    });
</script>
```
