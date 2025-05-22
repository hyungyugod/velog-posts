# 📌 1. 삼성전자 클론코딩
### 📌 1-1. gap 이 일정한 상황에서 한쪽의 gap만 줄이는 법
- margin을 -로 주면 된다. margin은 바깥여백이므로 만약 -10을 주면 준 요소만 정해진 방향으로 -10을 이동하면서 gap에 덮어씌워진다. 이는 gap에서 바깥 여백이 해당요소 기준으로 줄어들었음을 의미한다. 

### 📌 1-2. 글자크기를 반응형으로 줄이되 이미지 사이즈에 비례하게 줄이는 법
- 기본적으로 vw로 설정해서 하되 clamp를 통해서 내가 기준으로 만든 화면 해상도에서의 px을 확인하여 그 값을 max 값으로 준다 그러면 이미지가 더 이상 커지지 않을때 폰트도 더이상 작아지지 않을 수 있다. 최솟값은 너무 깨진다 싶으면 점점 내려서 모바일 쿼리로 바뀌기 전까지 조정하면 된다.
- gap이나 다른 모든 것들도 마찬가지이다.
- 1440px에서 기준을 1vw으로 잡았을 때 column-gap 14.4px인 경우
```css
.text-wrapper2 {
    gap: clamp(8px, 1vw, 14.4px);
}
```
- 근데 보통 gap은 고정 값으로 주고 폰트를 vw로 주는 것이 비율 유지에 주는 것이 좋으나 gap이 너무 커질 수도 있으므로 웬만하면 처리해주는게 또 좋아보이긴 한다.

### 📌 1-3. 미디어 쿼리는 덮어쓰기
- 미디어 쿼리는 원본에 덮어쓰기하는 식으로 작업하는 것이 편한 것 같다.
- 모바일 사이즈에서는 작아지는데에 한계를 두는 것이 좋다. 기본적으로 글씨나 gap을 vw로 설정한다음에 clamp를 걸어서 최소사이즈를 건다. 그런데 굳이 그렇게 소형 핸드폰보다 작은 기기까지 고려하기는 쉽지 않아서 일단 굳이 설정해두진 않았다.

# 📌 2. promise, async, await
- 프로미스 문법은 기존에 나란히 실행하면 각각 자신이 설정한 시간에 맞게 시간이 흐른 후 작동하던 비동기 함수들의 처리에 순서를 부여하기 위해 만들어졌다. 이는 한 비동기 함수의 리턴값을 받아 다른 비동기 함수를 리턴해야하는 경우에 기존에는 중첩구문을 사용해야했지만 promise 객체 안에서 비동기 처리를 사용하면 then, catch의 구문을 사용할 수 있게되어 비동기 처리간의 순서를 가독성있게 부여할 수 있게 된다는 점에서 의의가 있다.
- 즉 then으로 연결된 비동기 함수들은 그 자체로 한 덩어리가 되어 다른 코드 흐름들을 방해하지 않고 알아서 정해진 시간내에 따로 진행되게 된다.
- 즉 작은 틀에서는 순서가 있게 된거지만 하나의 큰 비동기 시스템을 구축할 수 있게되는 것이다.
```js
getUser(userId)
  .then(user => getPosts(user))
  .then(posts => getComments(posts))
  .then(comments => console.log(comments))
  .catch(error => console.error(error));
```

### 📌 2-1. fetch
- fetch는 fetch(주소) 형태로 작성되며 백엔드에 해당 주소로 get을 요청한다. 이는 비동기로 작동되며 요청만 한뒤 다음 함수로 실행순서를 넘긴다 이때 then으로 연결된 함수를 의미하는게 아니라 (then까지 하나의 묶음이므로) 그 다음에 호출되어있는 아래의 dependent같은 함수를 의미한다.
- fetch 함수의 리턴값은 Promise
```js
fetch('someurl')
  .then(res => res.json())
  .then(data => console.log(data));

dependent();
```
- 만약 묶어서 병렬 처리를 원한다면 아래와 같은 문법을 사용할 수 있다.
```js
async function run() {
  // 두 작업을 동시에 시작!
  const helloPromise = sayHello(); // 실행 시작, Promise 반환
  const byePromise = sayBye();     // 실행 시작, Promise 반환

  // 모두 끝날 때까지 기다림
  await Promise.all([helloPromise, byePromise]);
}
run();
```

### 📌 2-2. await, async
- awit과 async는 promis아래에 then으로 체이닝하다가 에러가 생기면 가까운 catch로 해결해야하는 즉 체인 안에서만 모든 것을 해결해야하는 문제를 해결하고 각각의 함수들을 좀 더 자유롭게 해주었다는데에 의의가 있다.
- async를 함수 앞에 붙이면 엔진이 무조건 리턴값을 promise로 씌워서 내보내준다. return이 1인 async 함수는 Promise.resolve(1) 이 되는식이다.
- async 함수는 실행 흐름 전체를 하나의 "비동기 컨텍스트(작업 묶음)"로 관리하게 된다.
- 함수 안에서 await이 등장하면 거기서 멈추고 해당 프로미스가 완료되면 그 다음 줄부터 이어서 실행한다. 함수 끝까지 이런 방식으로 처리된다.
- await을 프로미스를 리턴하는 함수 뒤에 붙이면 이전 프로미스가 끝날 때까지 기다렸다가 진행한다. 내부적으론 then으로 이어준다.
- 이렇게 처리했을때 좋은 것은 내부의 함수 사이 관계를 좀 더 유동적으로 if문 이나 try catch를 자유자재로 사용해서 꾸며줄 수 있게된다는 것이다. then으로 직선적으로 이어지던 공간이 acync 함수 내부라는 평면적인 공간으로 넓어진 것이다. 
```js
function fetchData1() {
  return new Promise(resolve => setTimeout(() => resolve("데이터1"), 1000));
}
function fetchData2() {
  return new Promise(resolve => setTimeout(() => resolve("데이터2"), 1000));
}

async function processData(type) {
  let data;
  if (type === 1) {
    data = await fetchData1();
  } else {
    data = await fetchData2();
  }
  console.log(`받은 데이터: ${data}`);
}

processData(1); // 1초 후: 받은 데이터: 데이터1
processData(2); // 1초 후: 받은 데이터: 데이터2
```

### 📌 2-3. resolve와 reject의 목적
- resolve(값) → 프로미스를 “성공 상태(fulfilled)”로 만들고, 전달한 “값”을 then으로 넘겨줌
- reject(값) → 프로미스를 “실패 상태(rejected)”로 만들고, 전달한 “값”을 catch로 넘겨줌
- 내부적으로 promise의 status를 변경하고 값을 전달하는 '기능'을 가진 함수이다.
```js
new Promise((resolve, reject) => {
  resolve("성공!");
})
.then(result => {
  console.log(result); // "성공!" 출력
});
```

# 📌 3. Ajax (Asynchronous JavaScript And XML)
- 핵심은 웹 페이지를 새로고침하지 않고도 서버와 데이터를 주고받을 수 있다는 것이다. 비동기 처리이기 때문에 가능하며 다른 시스템의 흐름을 바꾸지 않기 때문이다.

### 📌 3-1. 포트와 서버
- 포트는 네트워크에서 컴퓨터 안의 여러 프로그램(서비스)들을 구분하기 위한 번호
- IP 주소가 "컴퓨터" 자체의 주소라면,
포트 번호는 그 컴퓨터 안에서 '어떤 프로그램(서비스)'에 연결할지를 정하는 우편함 번호 같은 것이다.
- "포트 번호 1개에는 프로그램 1개" → 맞다.
- "프로그램 1개에는 포트 번호 1개" → 꼭 그런 건 아니다 (하나의 프로그램이 여러 포트 사용할 수 있음)

### 📌 3-2. fetch 활용
- 앞서 설명했던 것처럼 fetch 함수의 리턴값은 Promise이다.
- 이 Promise는 서버에서 응답이 오면(즉, 통신이 성공하면) 내부적으로 Response 객체를 담아서 "resolve"된다. 
- 응답이 아예 안 오거나, 네트워크 문제가 생기면 → Promise는 "reject" 상태가 된다. 이때는 Response 객체가 아니라 **"실제 에러 객체"**를 넘겨준다. 
- 이는 통신 자체의 성공의 의미가 있다. 주소가 잘못돼도 통신이 성공하면 resolve이다.
- 아래는 Response 객체 구조는 아래와 같다.

| 속성           | 설명                                    |
| ------------ | ------------------------------------- |
| `status`     | HTTP 상태 코드 (200, 404, 500 등)          |
| `ok`         | 상태 코드가 200\~299면 true, 아니면 false      |
| `url`        | 요청했던 URL                              |
| `headers`    | 응답의 헤더 정보 (Headers 객체)                |
| `statusText` | 상태 코드에 해당하는 메시지 ("OK" 등)              |
| `type`       | 응답의 유형 (basic, cors, error, opaque 등) |

- status, statusText는 http 상태코드이다. redirected는 백엔드가 처리를 못해서 다른 백엔드로 넘겼다는 것을 의미한다.
- headers(헤더): 웹 브라우저(클라이언트)와 서버가 **요청(Request)**과 **응답(Response)**을 주고받을 때 본문(body) 데이터 외에, 추가적인 정보를 담는 부분이다 (메타데이터). 버전 정보와 처리 가능한 컨텐츠 종류 등을 알려준다. 
- 아래는 response 객체의 주요 매서드이다.

| 메서드             | 설명                       |
| --------------- | ------------------------ |
| `text()`        | 응답 본문을 텍스트로 읽어옴          |
| `json()`        | 응답 본문을 JavaScript Object로 변환해서 읽어옴 |
| `blob()`        | 응답 본문을 Blob(파일 데이터)로 읽어옴 |
| `arrayBuffer()` | 응답 본문을 ArrayBuffer로 읽어옴  |
| `formData()`    | 응답 본문을 FormData로 읽어옴     |

### 📌 3-3. 두가지 방식의 Ajax 요청
```html
<body>
    <h1>Simple Get</h1>
    <div class="container">
        <a href="http://localhost:8080/hello.html">move to hello.html</a>
        <a href="#" id="btn1">Promise Load</a>
        <a href="#" id="btn2">Async Await Load</a>
    </div>
    <div id="result"></div>

    <script>
        // promise 방식의 ajax 요청
        document.querySelector('#btn1').addEventListener('click', e =>{
            e.preventDefault();
            console.log('loading');

            // 해당 파일에 있는 소스를 가져온다.
            const url = 'http://192.168.10.40:8080/hello.html';

            fetch(url)
                .then(response => {
                    console.log(response);

                    if (response.status !== 200) {
                        alert(`${response.status} error가 발생함 - ${response.statusText}`);
                        return;
                    }

                    response.text().then(txt => {
                        console.log(txt);
                        document.querySelector('result').innerHTML = txt;
                    });
            }).catch(error => {
                console.error(error);
            }).finally(() => {
                console.log('Finish!!!');
            });
        });

        // Async Await 방식의 ajax 요청
        document.querySelector('#btn2').addEventListener('click', async e => {
            e.preventDefault();

            console.log('Loading');

            const url = 'http://192.168.10.40:8080/hello.html';

            let response = null; // try-catch 전에 변수 미리 생성해놓음.

            try{
                response = await fetch(url);
            } catch (error) {
                console.error(error);
                alert(error.message);
                return;
            } finally {
                console.log('Finish!!!');
            }
            
            if (response.status !== 200) {
                alert(`${response} Error가 발생함 - ${response.statusText}`);
                return;
            }

            response.text().then(txt => {
                console.log(txt);
                document.querySelector('#result').innerHTML = txt;
            })
        })
    </script>
</body>
```

### 📌 3-4. Ajax 요청 개선, 로딩바 출력
- 로딩바를 html로 넣어놓고 css를 조절하여 나타나게하기
- async, await, feych를 활용하여 통신을 시도하고 성공했을 경우에도 에러코드가 200번이 아닌 비정상 케이스이면 에러처리
- 에러 status에 response의 status를 넣어서 출력해주기
-  js 객체에서 const {item} = result;로 필요한 키에 해당하는 것만 가져오기
-  새로운 html 태그를 동적으로 생성해서 item 키값에 해당하는 객체가 포함하고 있는 msg 속성을 값을 h1 속 innerHTML으로 넣어서 내용 표시하기
-  class도 하나 지정해주기, css는 미리 짜둬야함.
```html
<style>
    #loader {
        width: 50px;
        height: 50px;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        z-index: 9999999999;
        display: none;
    }

    .text-success {
        color: #0066ff;
        font-size: 24px;
    }
</style>
</head>
<body>
    <img src="img/loading.gif" id="loader" />

    <h1>Simple Json</h1>
    <a href="#" id="btn">load hello.json</a>
    <div id="result"></div>

    <script>
        const loader = document.querySelector('#loader');

        document.querySelector('#btn').addEventListener('click', async e => {
            e.preventDefault();

            loader.style.display = 'block';

            const result = null;

            try {
                const response = await fetch('http://localhost:8080/simple');

                if (response.status != 200){ // 백엔드가 에러를 보내온 경우
                const err =  new Error(response.statusText)
                err.status = response.status;
                throw err;
                }
                result = await response.json(); // 함수가 사용되면 await 일단 써줘야 순서가 안꼬임.
            }

            catch (err) {
                console.err(err);
                alert(err.message);
                return;
            }

            finally {
                loader.style.display = 'none';
            }

            const {item} = result; // 키가 item인 것만 가져옴.

            const h1 = document.createElement('h1').classList.add('text-success');
            h1.innerHTML = item.msg;
            document.querySelector('#result').appendChild(h1);
            
        });
    </script>
</body>
```

### 📌 3-5. 학과목록 표로 받아오기
- 데이터를 추출하면서 데이터를 가공할 수 있다. 추출할때 value 값을 key 값에 따라 다르게 가공하여서 innerHTML에 포함시킨다.
```html
<script>
    // 로딩바 객체
    const loader = document.querySelector("#loader");

    // async 함수 선언
    async function getDepartmentList() {
        // 로딩바 화면 표시
        loader.style.display = 'block';

        const url = "http://localhost:8080/departments";
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
```