# 📌 1. 입력 폼 만들기
- 원래 input을 테이블에 넣는 것은 테이블의 원래 목적인 데이터 제공과 맞지 않아 이렇게 구현하는 것이 아니라 div 태그로 구현하는 것이 낫다.
### 📌 1-1. input에는 왜 height가 position 없이는 안먹을까?
- input은 인라인 요소여서 height를 줘도 눈에 띄는 변화가 없다.
- position처리를 하면 해당 요소를 블록 요소처럼 처리하려는 성질이 강해지기 때문에 height가 먹는다.
- 위와 같은 논리이기 때문에 inline-block을 걸면 원하는 대로 처리할 수 있고 이게 정석이다.
- 웹 레이아웃의 크기 흐름: 부모가 명확한 크기를 가져야, 자식이 상대적인 크기를 가질 수 있다.
- 즉 상대(%) 단위의 한계: % 단위는 항상 “부모 크기가 확실할 때”만 의미가 있다. 이때 vw로 확실한 크기를 명시해주는 것과 같다.
- 하여 inline-block 처리를 하고 부모에 명확한 사이즈를 명시하면 height 100% 가 드디어 정상 작동한다.
- 이전에는 자식도 부모의 정확한 사이즈가 명시되어 있지 않기 때문에 논리가 꼬여서 그냥 자기가 보여줄 수 있는 글꼴 높이 만큼만 보여주게 된다.
- 즉 부모기준 100%가 아니라 자기가 할 수 있는 100%를 보여주는 것이다.
- 물론 기존처럼 td에 position: relative, input에 position: absolute를 줘도 잘 작동한다. 근데 이때는 그냥 이렇게만 하면 기준이 다시 모호해지므로 left 0, top 0을 부여해주어야한다.
```css
.my-table {
            th {
                width: 100px;
                text-align: left;
            }

            td {
                padding: 0; 
                height: 40px;

                input {
                    display: inline-block;
                    margin: 0;
                    width: 100%;
                    height: 100%;
                    box-sizing: border-box;
                    border: 0;
                    padding: 10px;
                }
            }
        }
```

### 📌 1-2. 입력 구현
- 데이터의 입력, 수정, 삭제가 발생하는 페이지는 중복처리를 방지하기 위해서 결과를 확인할 수 있는 페이지로 이동해야한다.
- 리뷰 목록 같은거는 바로 새로고침 해버려서 바로 반영을 해버린다.
- 하여 바로 window,location = `view.html?id=${result.item.id}`; 이렇게 해서 입력한 정보를 바탕으로 한 새로운 html을 사용한다.
- fetch의 두번째 메서드는 요청과 관련된 다양한 설정을 할 수 있고 기본 값은 method: get이다. 때문에 입력을 할때는 설정을 post로 바꾸어 주어야 한다.
- 스프링은 에러가 아니면 정확히 200만 준다는데 node.js로 만든 백엔드는 이게 201번도 나오고 그런가보다.
- 입력값 처리할때 id=my-form은 가장 큰 범위인 form에 넣어야 submit도 보고 내용도 볼 수 있다.
- method: 'POST'는 대문자가 표준이다.
- 그리고 form 데이터는 name이 있어야 쿼리스트링에 입력이 가능해서 input 태그들에 모두 name을 넣어주어야 한다.
```html
<script>
        document.querySelector('#my-form').addEventListener('submit', async e => {
            e.preventDefault();
            
            const loader = document.querySelector('#loader');

            loader.style.display = 'block';

            const url = new URL('http://localhost:8080/departments');

            const formData = new FormData(e.currentTarget);

            let result = null;

            try {
                // fetch의 두번째 메서드는 요청과 관련된 다양한 설정을 할 수 있고 기본 값은 method: get이다.
                const response = await fetch(url, {
                    method: 'POST', // 대문자가 표준이다.
                    body: formData
                });

                // 백엔드가 에러(200번대가 아닌 번호)를 보냈다면?
                if (parseInt(response.status / 100) !== 2) {
                    // 에러 객체 생성 후 에러 발생 --> catch로 이동함
                    const err = new Error(response.statusText);
                    err.status = response.status;
                    throw err;
                }

                // 응답으로부터 JSON 데이터 추출
                result = await response.json();
            } 
            
            catch (err) {
                console.error(err);
                alert(err.message);
                return;
            } 
            
            finally {
                // 로딩바 숨김
                loader.style.display = 'none';
            }

            console.log(result);

            window.location = `view.html?id=${result.item.id}`;

        });
    </script>
```

### 📌 1-3. 데이터를 가져올 때 효율적으로 가져오기
- 이걸 언제 다 하드코딩하고 있습니까?
- 키값 정해져있으면 그냥 순서 배열을 만들어서 데이터를 가져오면 일정한 순서를 유지하면서 표에 쌓을 수 있다.
```js
// 데이터를 가져올 순서
        const order = ["id", "dname", "loc", "phone", "email", "established", "homepage"];

        item.forEach(row => { // 데이터 배열의 각 행마다
            const tr = document.createElement("tr");

            order.forEach(key => {
                const td = document.createElement("td");
                let value = row[key]; // 이 키에 맞는 값을 꺼냄

                // 필요에 따라 가공/포맷
                if (key === "phone") {
                    td.innerHTML = `<a href="tel:${value}">${value}</a>`;
                } else if (key === "email") {
                    td.innerHTML = `<a href="mailto:${value}">${value}</a>`;
                } else if (key === "homepage") {
                    td.innerHTML = `<a href="${value}" target="_blank">${value}</a>`;
                } else if (key === "dname" && keyword !== '') {
                    td.innerHTML = value.replaceAll(keyword, `<mark>${keyword}</mark>`);
                } else {
                    td.innerHTML = value != null ? value : "";
                }
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });
```

### 📌 1-4. name을 백엔드가 요구하는 이름과 맞춰줘야한다. 
- name="name", name="location" 으로 했었는데 이는 백엔드 규격과 달랐다.
```html
<tr>
    <th>학과명</th>
    <td><input type="text" name="dname" id="name" placeholder="학과명을 입력하세요." /></td>
</tr>
<tr>
    <th>위치</th>
    <td><input type="text" name="loc" id="location" placeholder="위치를 입력하세요." /></td>
</tr>
```

# 📌 2. 정보로드하고 삭제하기
- 링크 뒤에 붙은 쿼리 스트링은 해당 링크에 정보를 추가할 뿐 경로는 .html까지이다.

### 📌 2-1. 학과 이름을 클릭하면 정보창으로 넘어가도록 만들기
- 아래와 같이 태그로 포멧팅하여 클릭하면 해당 학과에 아이디를 쿼리스트링으로 제공하고 있는 view.html로 넘어갈 수 있게 한다.
```js
else if (key === "dname") {
                    const dname = keyword === '' ? value : `<mark>${value}</mark>`;
                    td.innerHTML = `<a href='view.html?id=${row["id"]}'>${dname}</a>`; }
```
- 아래처럼 처리하면 value 값이 없을 때 이는 거짓이므로 여기까지만 컴퓨터가 읽고 그냥 value를 반환한다. (if는 이 상황에서 전체 문맥을 보고 블록을 건너뛸지를 판단하는 것이었다.)
```js
td.innerHTML = value && `<a href="${value}" target="_blank">${value}</a>`;
```

### 📌 2-2. 주소에 붙은 쿼리스트링 다루기
- const search = location.search; // 현재 페이지 주소에서 쿼리스트링 부분만 잘라냄
- entries: 키-값 쌍 배열
- Object.fromEntries(entries): js 객체로 변환, 원래 키-값 쌍으로 이루어진 데이터여야함.
- 위를 하는 이유는 searchParams는 key, value로 접근할 수 없기 때문임.
```js
        const search = location.search; // 현재 페이지 주소에서 쿼리스트링 부분만 잘라냄
        const searchParams = new URLSearchParams(search); // 위를 객체로 변환
        const params = Object.fromEntries(searchParams); // js 객체로 변환, 원래 키-값 쌍으로 이루어진 데이터여야함.
```
- path 파라미터는 개별 리소스(단일 데이터) 지정할 때, 쿼리 파라미터는 데이터를 검색하거나 정렬하고, 여러 페이지로 나누는 등 표시 조건을 지정할 때 사용한다.
- 즉 고유값 같은 단일값을 조회할 때는 path로 하는게 좋다. 
```js
// 백엔드 요청 준비 --> 데이터를 식별하기 위한 고유값은 백엔드 규격에 의해 path 파라미터로 전송
            const url = new URL(`http://localhost:8080/departments/${params.id}`);
```

### 📌 2-3. 삭제단계
- 삭제 들어가기 전에 링크 data-set에 id, 이름 새겨두기
```js
// 삭제 링크에 넘겨줄 학과이름 저장하기 - 버튼에 새겨두기
            const linkDelete = document.querySelector("#link-delete");
            linkDelete.dataset.id = id;
            linkDelete.dataset.dname = dname;
```
- 버튼을 클릭했을때 confirm으로 검사하기 
```js
const dname = e.currentTarget.dataset.dname;
            if (!confirm(`정말 ${dname}(을)를 삭제하시겠습니까?`)) {
                return;
            }
```
- 백엔드에 삭제하라고 적어서 보내면 백엔드가 json을 보고 삭제를 처리할 것
```js
const response = await fetch(url, {
                    method: "DELETE"
                });
```
- 삭제가 끝나면 빨리 자리를 뜨기
```js
// 목록 페이지로 이동
            window.location = "index.html";
```

### 📌 2-4. 전체 코드
```html
<body>
    <img src="img/loading.gif" id="loader" />

    <h1>학과 정보</h1>
    <table class="my-table">
        <tbody>
            <tr>
                <th>학과번호</th>
                <td id="id"></td>
            </tr>
            <tr>
                <th>학과명</th>
                <td id="dname"></td>
            </tr>
            <tr>
                <th>위치</th>
                <td id="loc"></td>
            </tr>
            <tr>
                <th>전화번호</th>
                <td id="phone"></td>
            </tr>
            <tr>
                <th>이메일</th>
                <td id="email"></td>
            </tr>
            <tr>
                <th>설립년도</th>
                <td id="established"></td>
            </tr>
            <tr>
                <th>홈페이지</th>
                <td id="homepage"></td>
            </tr>
        </tbody>
    </table>

    <div class="buttons">
        <a href="index.html">목록보기</a>
        <a href="add.html">신규등록</a>
        <a href="#" id="link-edit">수정하기</a>
        <a href="#" id="link-delete">삭제하기</a>
    </div>

    <script>
        /** [1] 페이지 초기화 */
        const search = location.search; // 현재 페이지 주소에서 쿼리스트링 부분만 잘라냄
        const searchParams = new URLSearchParams(search); // 위를 객체로 변환
        const params = Object.fromEntries(searchParams); // js 객체로 변환, 원래 키-값 쌍으로 이루어진 데이터여야함.

        if(!params.id) {
            alert('정상적인 경로로 접근하세요.');
            if (!history.back()) {
                window.location = 'index.html'
            }
        }

        /** [2] 백엔드에게 데이터 요청하기 */
        // 페이지 열림과 동시에 작동해야 하므로 즉시실행함수로 구현
        (async () => {
            loader.style.display = 'block';

            // 백엔드 요청 준비 --> 데이터를 식별하기 위한 고유값은 백엔드 규격에 의해 path 파라미터로 전송
            const url = new URL(`http://localhost:8080/departments/${params.id}`);

            let result = null;

            try {
                // 백엔드에 데이터를 요청하고, 응답 받기
                const response = await fetch(url);

                // 백엔드가 에러를 보내왔다면?
                if (parseInt(response.status / 100) != 2) {
                    // 에러 객체 생성후 에러 발생 --> catch문 이동함
                    const err = new Error(response.statusText);
                    err.status = response.status;
                    throw err;
                }

                // 응답으로부터 JSON 데이터 추출
                result = await response.json();
            } 

            catch (err) {
                console.error(err);
                alert(err.message);
                return;
            } 

            finally {
                // 로딩바를 숨김
                loader.style.display = 'none';
            }

            // 결과를 화면에 출력함
            const { id, dname, loc, phone, email, established, homepage } = result.item;

            document.querySelector('#id').innerHTML = id;
            document.querySelector('#dname').innerHTML = dname;
            document.querySelector('#loc').innerHTML = loc;
            document.querySelector('#phone').innerHTML = phone && `<a href="tel:${phone}">${phone}</a>`;
            document.querySelector('#email').innerHTML = email && `<a href="mailto:${email}">${email}</a>`;
            document.querySelector('#established').innerHTML = established;
            document.querySelector('#homepage').innerHTML = homepage && `<a href="${homepage}" target="_blank">${homepage}</a>`;

            // 수정페이지 이동 링크의 주소 설정하기
            document.querySelector("#link-edit").setAttribute("href", `edit.html?id=${id}`);

            // 삭제 링크에 넘겨줄 학과이름 저장하기 - 버튼에 새겨두기
            const linkDelete = document.querySelector("#link-delete");
            linkDelete.dataset.id = id;
            linkDelete.dataset.dname = dname;
        })();

        /** [3] 데이터 삭제 요청 */
        
        document.querySelector("#link-delete").addEventListener("click", async e => {
            e.preventDefault();

            const dname = e.currentTarget.dataset.dname;
            if (!confirm(`정말 ${dname}(을)를 삭제하시겠습니까?`)) {
                return;
            }

            // 로딩바를 화면에 표시함
            loader.style.display = 'block';

            // 백엔드 요청 URL --> 데이터를 식별하기 위한 고유값은 백엔드 규격에 의해 path 파라미터로 전송
            const url = new URL(`http://localhost:8080/departments/${params.id}`);

            let result = null;

            try {
                // 백엔드에 데이터를 요청하고, 응답 받기
                const response = await fetch(url, {
                    method: "DELETE"
                });

                // 백엔드가 에러를 보내왔다면?
                if (parseInt(response.status / 100) != 2) {
                    // 에러 객체 생성후 에러 발생 --> catch로 이동함
                    const err = new Error(response.statusText);
                    err.status = response.status;
                    throw err;
                }

                // 응답으로부터 JSON 데이터 추출
                result = await response.json();
            } 
            
            catch (err) {
                console.error(err);
                alert(err.message);
                return;
            } 
            
            finally {
                // 로딩바를 숨김
                loader.style.display = 'none';
            }

            // 목록 페이지로 이동
            window.location = "index.html";
        });

    </script>
</body>
```

# 📌 3. 정보 로드하고 수정하기
- 새로운 페이지를 생성할 때 정보를 로드하는 과정은 삭제 페이지와 같고 정보를 수정하는 과정은 정보 입력하는 과정과 비슷하다.
- 하여 주요한 다른 점만 적어두겠다.
- html 구조에서 원래 넣던 id는 사용자가 수정하면 안되므로 hidden으로 숨겨준다.
```html
<input type="hidden" name="id" id="id">
```
- 정보를 로드할때 input 태그 안으로 로드 해주어야 하므로 input태그의 정보 중 value만 콕 찝어서 삽입해 주어야 한다.
- 위와 같은 처리가 끝나면 수정할때 새로운 정보를 원래 정보 위에서 수정할 수 있다.
```js
document.querySelector('#id').value = id;
            document.querySelector('#dname').value = dname;
            document.querySelector('#loc').value = loc;
            document.querySelector('#phone').value = phone;
            document.querySelector('#email').value = email;
            document.querySelector('#established').value = established;
            document.querySelector('#homepage').value = homepage;
```
- 수정이 완료된 후 다시 view로 가서 올바르게 수정이 되었음을 보여준다.
```js
window.location = `view.html?id=${result.item.id}`;
```
