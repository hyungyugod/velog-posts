# 📌 1. 삼성 클론코딩
### 📌 1.1 메뉴바가 상단 메뉴에서 내려오게 하기 위해 a링크를 바깥 박스의 바닥에 붙이기
- .header_inner에에	height: 39.33px, align-items: stretch를 주어서 내부 요소가 세로를 꽉채우게 하였고 명확한 높이를 주어서 자식이 height 100%를 했을 때 딱 붙을 수 있도록 하였다.
- .desktop-main_menu에에	height: 100%, margin: 0을 주어서 a링크를 담은 ul이 바깥에 딱 붙을 수 있게까지 하였다.
- 가장 바깥의 크기를 아예 키워버리고 세부조정은 안에서 하는 방식으로 li가 바닥에 붙으면서 padding을 준 효과를 내었다. .header_inner에	height: 39.33px에서 height: 58.33px까지 올리고 ul태그의 align-item center도 풀었다.

# 📌 2. Ajax 응용

### 📌 2-1. 가져온 표 테이터에 검색창 만들기
- submit 이벤트가 발생하는건 form 단위에서이다.
- url.searchParams.set('dname_like', keyword); : url.searchParams은 주소의 ? 뒤에 붙는 여러 가지 정보를 관리할 수 있게 해주는 도구이다. (queryString 관리)
- set('dname_like', keyword) : set(키, 벨류)을 주소에 추가하거나 이미 있으면 바꿔준다.
- 아래는 학과명 안에 사용자가 검색한 단어가 있으면, 그 부분만 노란색 배경(강조) 표시로 보여주는 처리이다.
- tbody.innerHTML = ""; 를 넣어서 조회할때마다 행이 누적되지 않도록 한다.
```js
else if (key === 'dname' && keyword !== ''){
    value = value.replaceAll(keyword, `<mark>${keyword}</mark>`);
}
```
```html
<body>
<img src="img/loading.gif" id="loader" />

<form id="my-form">
    <input type="search" id="my-search" placeholder="학과이름 검색">
    <button type="submit">검색</button>
</form>

<h1>학과 목록</h1>
<table class="my-table">
    <thead>
        <tr>
            <th>학과번호</th>
            <th>학과명</th>
            <th>위치</th>
            <th>전화번호</th>
            <th>이메일</th>
            <th>설립년도</th>
            <th>홈페이지</th>
        </tr>
    </thead>
    <tbody>
    </tbody>
</table>
<script>
    // 로딩바 객체
    const loader = document.querySelector("#loader");

    let keyword = '';

    document.querySelector('#my-form').addEventListener('submit', e => { // submit은 myform 단위에서 발생한다.
        e.preventDefault();
        keyword = document.querySelector('#my-search').value;
        getDepartmentList(); // 새로 바뀐 정보를 가져옴
    })

    // async 함수 선언
    async function getDepartmentList() {
        // 로딩바 화면 표시
        loader.style.display = 'block';

        let url = new URL("http://localhost:8080/departments");

        if (keyword) {
            url.searchParams.set('dname_like', keyword);
        }

        console.log(url.href);

        let result = null;

        try {
            // 백엔드로부터 응답 받기
            const response = await fetch(url);

            // 백엔드가 에러를 보냈다면?
            if (response.status != 200) {
                // 에러 객체 생성 후 에러 발생 --> catch로 이동함
                const err = new Error(response.statusText);
                err.status = response.status;
                throw err;
            }

            // 응답으로부터 JSON 데이터 추출
            result = await response.json();
            } catch (err) {
                console.error(err);
                alert(err.message);
                return;
            } finally {
                // 로딩바 숨김
                loader.style.display = 'none';
            }

        // 결과 데이터 확인
        console.log(result);

        // JSON 응답에서 코드만 추출
        const {item} = result;
        console.log(item);

        // tbody 찾기
        const tbody = document.querySelector(".my-table tbody");
        tbody.innerHTML = "";

        // 데이터만큼 <tr>태그 생성
        item.forEach((row) => {
            const tr = document.createElement("tr");
            // 각 키값을 있는 key에 맞게 반복
            for (const key in row) {
                // 값이 null이거나 공백인 경우 빈칸으로 출력하는 형태로 생성
                const td = document.createElement("td");
                let value = row[key];

                if (value == null) {
                    value = "";
                } else {
                    if (key === "phone") {
                        value = `<p><a href="tel:${value}">${value}</a></p>`;
                    } else if (key === "email") {
                        value = `<a href="mailto:${value}">${value}</a>`;
                    } else if (key === "homepage") {
                        value = `<a href="${value}" target="_blank">${value}</a>`;
                    } else if (key === 'dname' && keyword !== ''){
                        value = value.replaceAll(keyword, `<mark>${keyword}</mark>`);
                    }
                    
                }
                td.innerHTML = value;
                tr.appendChild(td);
            }
            // 완성된 <tr>을 tbody에 추가
            tbody.appendChild(tr);
        });
    }
    getDepartmentList();
</script>
</body>
</html>
```

### 📌 2-2. 영화진흥위원회 api 활용 영화 순위 만들기

#### REST 방식과 GET 매서드에 대하여
- 당일데이터는 집계가 안된다. (하면 컴퓨터 엔진이 힘들다.)
- REST(Representational State Transfer) 방식 : "서버의 자원이 가진 현재 상태를 여러 가지 표현 방식(JSON, XML 등)으로 **전송(Transfer)**하는 아키텍처 스타일" 이다.
- 인터넷에서 서버와 클라이언트(브라우저, 앱 등)가 서로 데이터를 주고받을 때, 일정한 규칙을 정해놓으면 개발도 쉽고, 유지보수도 편하기 때문에 이러한 통신 규격을 정해둔다.
- REST의 핵심 원칙: 자원의 식별(URI), 행위는 HTTP 메서드로, 무상태성(Stateless), 일관된 인터페이스
1) 자원의 식별(URI) : 모든 자원(데이터)은 **URI(주소)**로 표현한다.
2) 행위는 HTTP 메서드로(자원에 대해 **무엇을 할지(행위)**는 HTTP 메서드로 구분한다.) : GET : 데이터 조회(url에 쿼리스트링 형식으로 표현), POST : 데이터 생성, PUT : 데이터 전체 수정, PATCH : 데이터 일부 수정, DELETE : 데이터 삭제
3) 무상태성(Stateless) : 사용자가 서버에 요청을 보낼 때, 서버는 "이 사람이 누구인지, 직전에 무슨 요청을 했는지" 기억(저장)하지 않는다는 뜻이다. 서버가 사용자의 상태를 저장하지 않으니 매번 사용자 정보를 메타데이터로 보내야하므로 무겁지만 대신 한 곳에 정보가 없으니 여러 대로 서버를 가동하여 요청을 효율적으로 처리할 수 있다.
- HTTP 메서드: 클라이언트가 서버에게 “내가 이 데이터에 대해 무엇을 하고 싶다”라고 **의도(행동)**를 알려주는 명령이다.(행동의 종류를 나타내는 규약) 즉 요청하는 방식을 정해놓은 것이다.
- SODA, SOAP, RPC 행동 중심(함수명/메서드명 노출)으로 설계가 자유로워 보이지만, API가 많아지면 규칙 없이 뒤죽박죽 섞이고 API 혼란이 발생하기 쉽다.
- 반면 REST는 일관성 + 표준화가 장점이며 현재 http의 규약에 가장 적합하다.

#### API의 의미
- API는 "소프트웨어끼리 소통(통신)"을 위한 약속이다.
- API = 기능을 제공하고, 그 기능을 어떻게 쓸지(호출 방법, 입력/출력 등)를 “약속”해 놓은 인터페이스이다.

#### 코드
- finally 뒤에 ;는 굳이 필요 없다.
- url 복사할때 앞에 스페이스바가 들어가있으면 안된다.
- 객체 구조 따라가면서 체이닝할때 중간에 건너뛰면 안된다.
- td_audi.innerHTML = parseInt(v.audiCnt).toLocaleString(); : 정수형 숫자로 바꾸고 사람이 읽게 쉽게 따옴표 붙여서 출력해줌.
- https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js 여기서 UMD는 Universal Module Definition으로 여러 환경에서 동시에 쓸 수 있도록 만든 자바스크립트 모듈 포멧을 의미한다. 또한 min은 minified(압축됨)을 의미한다. 이는 코드의 공백, 주석, 줄바꿈을 다 없애고 최대한 짧게 만든 "최적화 파일"이다.
```html
    <title>05-boxoffice</title>
    <link rel="stylesheet" href="css/style.css">
    <style>
        .container { 
            display: flex;
            box-sizing: border-box;

            .item{
                flex: 0 0 50%;

                &:first-child {
                    padding-right: 10px;
                }

                &:last-child {
                    padding-left: 10px;
                    height: 450px;
                }
            }
        }
    </style>
</head>
<body>
    <img src="img/loading.gif" id="loader">

    <h1>영화진흥위원회 박스오피스 순위</h1>
    <input type="date" id="targetDt">
    <hr>
    <div class="container">
        <div class="item">
            <table class="my-table">
                <thead>
                    <tr>
                        <th>순위</th>
                        <th>영화제목</th>
                        <th>관객수</th>
                        <th>개봉일</th>
                    </tr>
                </thead>

                <tbody id="list-body"></tbody>

            </table>
        </div>
        <div class="item">
            <canvas id="my-chart"></canvas>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
    <script>
        const loader = document.querySelector('#loader');

        let chart;

        document.querySelector('#targetDt').addEventListener('change', async e => {
            const dtInput = e.currentTarget.value.replaceAll('-', '');
            
            if (!dtInput) return ; // 사용자 입력이 없으면 처리 중단

            loader.style.display = 'block';

            // 요청 url 설정
            const requestUrl = new URL('http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json');
            requestUrl.searchParams.set('key', 'c736fdc8abfaf3afbb4884778bc76e27');
            requestUrl.searchParams.set('targetDt', dtInput);

            let result = null; // rest 방식으로 가져올 박스오피스 정보 객체를 저장할 변수

            try {
                const response = await fetch(requestUrl);

                if (response.status !== 200){
                    const err = new Error(response.statusText); // 상태 메세지를 에러 메세지로 넣어서 에러를 정의함.
                    err.status = response.status; // 새로운 status라는 err의 속성을 만들고 404등의 에러코드를 넣어줌
                    throw err;
                } 

                result = await response.json(); // 가져온 정보를 js object로 변환
            } 

            catch (err) {
                console.log(err);
                alert(err.message);
                return;
            }

            finally {loader.style.display = 'none'}

            // 차트를 만들 배열 생성
            const movieNm = [];
            const audiCnt = [];

            const listbody = document.querySelector('#list-body');
            listbody.innerHTML = ''; // 매번 새로운 값을 가져오기 위해

            result.boxOfficeResult.dailyBoxOfficeList.forEach(v => { // tr, td 모두 재사용해야하므로 그냥 변수 만들고 값넣고 html에 넣어야 한다.
                const tr = document.createElement('tr');
                listbody.appendChild(tr);

                const td_rank = document.createElement('td');
                td_rank.innerHTML = v.rank;
                tr.appendChild(td_rank);

                const td_name = document.createElement('td');
                td_name.innerHTML = v.movieNm;
                td_name.style.textAlign = 'left';
                tr.appendChild(td_name);

                const td_audi = document.createElement('td');
                td_audi.innerHTML = parseInt(v.audiCnt).toLocaleString();
                td_audi.style.textAlign = 'left';
                tr.appendChild(td_audi);
                
                const td_opndDt = document.createElement('td');
                td_opndDt.innerHTML = v.openDt;
                tr.appendChild(td_opndDt);

                movieNm.push(v.movieNm);
                audiCnt.push(v.audiCnt);
            });

            if (chart !== undefined) {chart.destroy();} // 그래프가 이미 표시되고 잇으면 기존 출력 내용을 삭제해야한다.
            
            chart = new Chart(document.querySelector('#my-chart'), {
                type: 'bar',
                data: {
                    labels: movieNm,
                    datasets: [
                        {
                            laber: '관람객 수',
                            data: audiCnt
                        }
                    ]
                },
                options: {
                    maintainAspectRatio: false
                }
            });
        });
    </script>
</body>
</html>
```

# 📌 3. Ajax로 input 직접 만들어보기 + CRUD
- 404에러: 존재하지 않는 주소
- let requestUrl = new URL('http://192.168.10.40:8080/students').searchParams.set('name_like', userinput); : 이렇게 작성하면 .searchParams.set('name_like', userinput);의 반환값인 undefined가 requestUrl에 저장된다.
- const userinput = ''; 이렇게 하면 한번 할당한 값을 다시 저장할 수 없으므로 let으로 값을 바꿀 수 있게 해야 사용자가 입력한 값을 받아서 그때그때 넣어줄 수 있다.
- 이미지 주소를 img 태그로 바꾸기: value = `<img src="${value}" alt="사진" style="max-width:50px; max-height:50px;">`;를 통해 만든 td 태그를 변형 할 수 있다.
- 생일 같은 거: value = value.substring(0, 10); 뒤에 불필요한 시각 같은 것을 버릴 수 있다.
```html
<body>
    <img src="img/loading.gif" id="loader" />

    <form id="my-form">
        <input type="search" id="my-search" placeholder="학생이름 검색">
        <button type="submit">검색</button>
    </form>

    <h1>학생 목록</h1>
<table class="my-table">
    <thead id="my_thead">
        <tr id="my_tr">
            <th>학생 번호</th>
            <th>학생 이름</th>
            <th>학생 아이디</th>
            <th>학년</th>
            <th>주민등록 번호</th>
            <th>생년월일</th>
            <th>전화번호</th>
            <th>키</th>
            <th>몸무게</th>
            <th>이메일</th>
            <th>성별</th>
            <th>재학 상태</th>
            <th>사진 URL</th>
            <th>입학일</th>
            <th>졸업일</th>
            <th>학과 ID</th>
            <th>지도교수 ID</th>
        </tr>
    </thead>
    <tbody id="my_tbody"></tbody>
</table>
<script>
    // Ajax로 데이터 받아오기 (fetch가 비동기 처리 방식을 사용하므로)
    const loadingBar = document.querySelector('#loader');

    let userinput = ''; // 기본은 문자열로 선언

    document.querySelector('#my-form').addEventListener('submit', e => {
        e.preventDefault();
        userinput = document.querySelector('#my-search').value;
        getStudentList();
    });

    async function getStudentList() {
        loadingBar.style.display = 'block';

        let requestUrl = new URL('http://192.168.10.40:8080/students');      
        if (userinput) requestUrl.searchParams.set('name_like', userinput);

        let result = null;

        try {
            const response = await fetch(requestUrl);

            if (response.status !== 200) {
                const err = new Error(response.statusText);
                err.status = response.status;
                throw err;
            }

            result = await response.json();
        }

        catch (err) {
            console.error(err);
            alert(err);
            return;
        }

        finally {
            loadingBar.style.display = 'none';
        }
        // 여기까지가 데이터를 받아오는 과정


        const tbody = document.querySelector('#my_tbody');
        tbody.innerHTML = ''; // 목록 초기화

        const {item} = result; // 학생들 정보가 담긴 배열만 구조분해

        item.forEach(p => { // 배열 분해
            const tr = document.createElement('tr');

            for (v in p) { // 배열 내부에 학생 개인 객체를 순회
                let td = document.createElement('td');
                let value = p[v];

                if (value == null) {
                    value = "";
                } 
                
                else {

                    if (v === "phone") {
                        value = `<p><a href="tel:${value}" style="color: #000;">${value}</a></p>`;
                    }
                    
                    else if (v === "email") {
                        value = `<a href="mailto:${value}" style="color: #000;">${value}</a>`;
                    }

                    else if (v === "birthdate") {
                        value = value.substring(0, 10);
                    }
                    
                    else if (v === 'name' && userinput !== ''){
                        value = value.replaceAll(userinput, `<mark>${userinput}</mark>`);
                    }

                    else if (v === 'photo_url'){
                        value = `<img src="${value}" alt="사진" style="max-width:50px; max-height:50px;">`;
                    }
                }

                td.innerHTML = value;
                tr.appendChild(td);
            }

            tbody.appendChild(tr);
        });
    };

    getStudentList();
</script>
</body>
</html>
```

#### CRUD
- get, post, put, delete로 데이터를 요청하면 crud(입력, 읽기 수정, 삭제)로 백엔드가 받는다.
- 일반적으로 GET-Read, POST-Create, PUT/PATCH-Update, DELETE-Delete로 대응