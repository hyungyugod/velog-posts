# 📌 0. jQuery 수업
### 📌 0-1. 요소 생성
- jquery는 바닐라 js와 달리 아직 만들어지지 않은 태그에도 클래스 기반으로 js 이벤트를 부여할 수 있다. 
- $(document).on("click", ".item", e => { 이런 문법으로 쓰인다.
- li.addClass(`item ${clsName}`); 바닐라 js와 달리 이렇게 클래스를 추가할때는 띄어쓰기를 기준으로 이런식으로 포멧팅하여 만들면 된다.
- prepend는 앞에 삽입하는 것이다.
- append는 뒤에 삽입하는 것이다.
- insertBefore는 A.insertBefore(B) --> A를 B의 직전에 삽입한다는 뜻이다.
```html
<script>
    // 동적으로 JS가 생성한 HTML요소가 추가될 객체
    const list = $('#list');

    // 사용자가 입력할 input 태그
    const comment = $('#comment');

    // 앞으로 생성될 .item 클래스가 지정된 요소에 대한 click 이벤트 미리 지정하기
    $(document).on("click", ".item", e => {
        // 클릭한 <li>태그를 제거함
        $(e.currentTarget).remove();
    });

    // 동적으로 <li>태그 Element 객체를 생성하여 리턴하는 함수
    const getItem = (clsName) => {
        const li = $('<li>');
        li.addClass(`item ${clsName}`);
        li.html(comment.val());
        return li;
    };

    $('#appendChild').on('click', (e) => {
        // A.append(B) --> A의 마지막 자식으로 B를 추가한다.
        list.append(getItem('blue'));
    });

    $('#insertBefore1').on('click', (e) => {
        // A.prepend(B) --> A의 첫번째 자식으로 B를 추가한다.
        list.prepend(getItem('orange'));
    });

    $('#insertBefore2').on('click', (e) => {
        // A.insertBefore(B) --> A를 B의 직전에 삽입한다.
        getItem('pink').insertBefore($('li:first-child'));
    });
</script>
```

### 📌 0-2. 복제
- clone을 통해 현재 요소를 모두 복사할 수 있다. 
- 이후 id 값은 유일해야하므로 copy.attr('id', id); 를 통해 id만 새로 정의해 주어야 한다.
- $(".item").not("#obj").remove(); 에서 첫번째 요소 id만 선택하여 첫번째 요소만 남기고 다시 다 지우는 로직을 구현한다.
```html
<script type="text/javascript">
    $("#btn1").on('click', e => {
        // 현재 시간의 timestamp
        const time = (new Date()).getTime();

        // 복제될 요소의 id값 만들기
        const id = 'copy_' + time;

        // '#obj'를 복제한다.
        const copy = $("#obj").clone();

        // 요소를 복제할 경우 id값까지 동일해지므로 id값은 새로운 값으로 변경해야 한다.
        copy.attr('id', id);

        // 복제된 요소를 '#box'에 추가한다.
        $("#box").append(copy);
    });

    $("#btn2").on('click', e => {
        // 첫 번째 요소를 남겨두고 삭제한다.
        $(".item").not("#obj").remove();
    });
</script>
```

### 📌 0-3. 이미지 미리보기
- FileList 객체는 jQuery가 아닌 순수 JavaScript 객체이기 때문에 Vanilla JS로 처리해야 한다.
- imgTag.attr('src', imgUrl).addClass('preview'); 이미지 태그에 새로운 주소를 붙여서 새로 만들어낸다.
```html
<script type="text/javascript">
    // file 요소에 대한 change 이벤트
    $('#file-input').on('change', (e) => {
        // 미리보기를 표시할 컨테이너 객체
        const previewContainer = $('#preview-container');

        // 컨테이너의 내부를 모두 지운다.
        previewContainer.empty();

        // 선택된 파일의 파일리스트(배열이 아님)
        // --> e.currentTarget.files는 FileList 객체로, 선택된 파일들의 정보를 담고 있다.
        // --> FileList 객체는 jQuery가 아닌 순수 JavaScript 객체이기 때문에 Vanilla JS로 처리해야 한다.
        const files = e.currentTarget.files;
        console.log(files);

        // 선택된 파일의 수 만큼 반복
        Array.from(files).forEach((v, i) => {
            // i번째 파일을 가져온다.
            const imgUrl = URL.createObjectURL(v);
            console.log(imgUrl);

            // 이미지를 표시할 img태그를 생성 --> jQuery 사용
            const imgTag = $('<img>');
            imgTag.attr('src', imgUrl).addClass('preview');

            // 그동안 생성한 새로운 HTML태그를 화면상에 표시하기 위해
            // 기존의 Element객체 안에 자식요소로 추가(append)
            previewContainer.append(imgTag);
        });
    });
</script>
```