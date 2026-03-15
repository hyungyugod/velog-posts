# 📌 0. 삼성전자 클론 코딩
### 📌 0-1. before와 after 활용하여 회색선 넣기
- 이 둘은 가상요소로 실제 HTML에 없지만, CSS로 "가짜" 요소를 만들어 꾸밀 수 있는 기능을 의미한다. html로 직접 그리기 귀찮은데 많이 사용되는 요소들에 이를 넣어서 사용한다.
- ::before는 선택한 요소의 '내용 앞'에 삽입하고 ::after는 선택한 요소의 '내용 뒤'에 삽입된다.
- content: 보여줄 내용(필수)를 작성하고 스타일을 꾸미면 된다.
- ::before, ::after로 생긴 가상 요소의 기본 display 값은 inline이다. 즉 아무 스타일도 주지 않으면 텍스트처럼 취급된다. display: block이나 inline-block을 주면 박스모델처럼 width와 height를 조절할 수 있다.
- 보통 선만 그리고 싶다면 position absolute로 직접 라인을 잡아주는 경우가 많다.
- 근데 결국 list-side에 border-right 주고 끝냈다,,
```css
.menuinner_wrapper{
                    max-width: 1440px;
                    margin: auto;
                    display: flex;
                    .listside{
                        position: relative;
                        .menuinner-lists {
                            display: flex;
                            width: 100%;
                            
                            > li {
                                display: flex;
                                flex-direction: column;
                                flex: 1 1 16%;
                                min-width: 100px;
                                border: none;
                                list-style: none;
                                padding: 1.5rem 1rem 8rem;
                            }
                        }

                        &::after {
                            content: "";
                            position: absolute;
                            right: 0;
                            top: 0;
                            width: 1px;
                            height: 100%;
                            background: #e3e3e3;
                            z-index: 2;
                        }
                    }
                }
```

### 📌 0-2. list-style: none은 ul에 사용하자
- 세부사항 ul에 직접 사용해야 li들에 전파될 수 있다.
```css
.menuinner-lists {
                            display: flex;
                            width: 100%;
                            
                            > li {
                                display: flex;
                                flex-direction: column;
                                flex: 1 1 16%;
                                min-width: 100px;
                                border: none;
                                padding: 1.5rem 1rem 8rem;

                                ul { /* 각각 세부항목 */
                                    list-style: none;
                                }
                            }
                        }
```

### 📌 0-3. width 기본값
- width의 기본값은 100%이다. 따라서 width를 설정하지 않으면 자동적으로 부모요소의 100%로 설정된다.

# 📌 1. handlebars.js
- 정해진 html 태그에 특정부분을 포멧팅해서 새로 생산해주는 라이브러리

### 📌 1-1. 템플릿 생성기본
- const template = Handlebars.compile(document.querySelector('#my-tmpl').innerHTML); : 미리 스크립트에 양식을 만들어두고 이를 컴파일한 템풀랏 함수를 미리 만들어두면 아래와 같은 따로 생성한 컨텐츠와 함께 얼마든지 조합한 이벤트 핸들러를 만들 수 있다.
```js
const my_content = {
            title: '제목입니다.',
            content1: '첫 번째 <strong>내용</strong>입니다.',
            content2: '두 번째 <strong>내용</strong>입니다.'
        };
```
- 아래는 전체 코드이다.
```html
<h1>handlebars</h1>
    <div id="my-container">

    </div>

    <button id="my-btn">한번 눌러보셔</button>

    <script type="text/x-handlebars-template" id="my-tmpl">
        <a href="#" class="list-group-item">
            <h4 class="list-group-item-heading">{{title}}</h4>
            <p class="list-group-item-text">
                {{content1}} <br>
                {{{content2}}}
            </p>
        </a>
    </script>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.7.8/handlebars.min.js"></script>

    <script>
        const my_content = {
            title: '제목입니다.',
            content1: '첫 번째 <strong>내용</strong>입니다.',
            content2: '두 번째 <strong>내용</strong>입니다.'
        };

        const template = Handlebars.compile(document.querySelector('#my-tmpl').innerHTML); // 미리 지정한 양식을 컴파일해둔 템플릿 함수를 생성

        document.querySelector('#my-btn').addEventListener('click', e => {
            const result = template(my_content); 
            document.querySelector('#my-container').insertAdjacentHTML('beforeend', result); // 문자열을 내부 (끝부분)에 삽입
        });
    </script>
```

### 📌 1-2. 변수가 지정한 함수를 거쳐서 입력되도록 하기
- {{convertAge birthday}}: 이렇게 포멧팅할 변수 앞에 Handlebars.registerHelper로 설정해 둔 함수 이름을 입력하면 해당 변수가 함수에 먼저 들어간 다음에 포멧팅이 적용된다.
```html
<body>
    <h1>handlebars</h1>
    <div id="my-container">

    </div>

    <button id="my-btn">한번 눌러보셔</button>

    <script type="text/x-handlebars-template" id="my-tmpl">
        <a href="#" class="list-group-item">
            <h4 class="list-group-item-heading">{{name}}</h4>
            <p class="list-group-item-text">
                나이: {{convertAge birthday}} / 성별: {{convertGender gender}}
            </p>
        </a>
    </script>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.7.8/handlebars.min.js"></script>
    
    <script>
        // Handlebars 훅(헬퍼) 안에 convertGender라는 함수를 추가하기
        Handlebars.registerHelper('convertGender', value => value === "M" ? "남자" : "여자");
        Handlebars.registerHelper('convertAge', value => (new Date().getFullYear() - parseInt(value.substring(0, 4)) + 1));
    </script>
    
    <script>
        const my_content = {
            name: "설계일",
            birthday: "2000-01-14",
            gender: "M"
        };

        const template = Handlebars.compile(document.querySelector("#my-tmpl").innerHTML);
        
        document.querySelector("#my-btn").addEventListener("click", e => {
            const result = template(my_content);
            document.querySelector("#my-container").insertAdjacentHTML("beforeend", result);
        });
    </script>
    
</body>
```

### 📌 1-3. 어제 만든 index에 핸들러 적용
- 고정된 템플릿에 새로운 내용을 변환해서 자동으로 입력해야 할때는 handler를 사용하면 재사용성도 좋고 코드도 간결해져서 유용한 것 같다.
- handlebars를 가져오고 우선 template type을 아래 처럼 생성했다. 이때 {{#each item}}로 묶으면 item 배열 내부(result.item)에 대해 계속 반복을 돌아서 출력해준다. 
- 
```js
<script type="text/x-handlebars-template" id="my-tmpl">
    {{#each item}}
    <tr>
        <td>{{id}}</td>
        <td><a href="view.html?id={{id}}">{{convertKeyword dname}}</a></td>
        <td>{{loc}}</td>
        <td>{{convertPhone phone}}</td>
        <td>{{convertEmail email}}</td>
        <td>{{established}}</td>
        <td>{{convertHomepage homepage}}</td>
    </tr>
    {{/each}}
</script>
```
- 이제 핸들바 라이브러리에 위의 템플릿을 만들어낼 수 있는 함수와 변수에 적용할 함수를 생성, 등록해준다.
```js
//handlebars 라이브러리에 helper 함수, 템플릿 등록
    Handlebars.registerHelper('convertPhone', value => value && `<a href="tel:${value}">${value}</a>`);
    Handlebars.registerHelper('convertEmail', value => value && `<a href="mailto:${value}">${value}</a>`);
    Handlebars.registerHelper('convertHomepage', value => value && `<a href="${value}" target="_blank">${value}</a>`);
    Handlebars.registerHelper('convertKeyword', (value, keyword) => !keyword ? value : value.replace(keyword, `<mark>${keyword}</mark>`));
    const template1 = Handlebars.compile(document.querySelector('#my-tmpl').innerHTML); 
```
- 이후 백엔드에서 자료를 받아온 다음에 아래와 같이 템플릿을 활용해 tbody안에 넣어준다.
```js
async function getDepartmentList() {
        let result = null;

        try {
            result = await fetchHelper.get('http://localhost:8080/departments', {
                _sort: 'id',
                _order: 'desc',
                dname_like: keyword
            });
        }

        catch (err) {
            alert(err.message);
            return;
        }

        //handelbars 이용한 템플릿 삽입
        document.querySelector('.my-table tbody').innerHTML = template1(result);
    }
```

### 📌 1-4. view에서는 item 배열이 아니라 result 내부 item 속성을 따로 빼서 템플릿에 직접 복사
- 템플릿 정의해준다. 배열이 아니라 단일 객체일 것이기 때문에 each는 쓰지 않는다.
```js
<script type="text/x-handlebars-template" id="my-tmpl">
    <tr>
        <th>학과번호</th>
        <td>{{id}}</td>
    </tr>
    <tr>
        <th>학과명</th>
        <td>{{dname}}</td>
    </tr>
    <tr>
        <th>위치</th>
        <td>{{loc}}</td>
    </tr>
    <tr>
        <th>전화번호</th>
        <td>{{convertPhone phone}}</td>
    </tr>
    <tr>
        <th>이메일</th>
        <td>{{convertEmail email}}</td>
    </tr>
    <tr>
        <th>설립년도</th>
        <td>{{established}}</td>
    </tr>
    <tr>
        <th>홈페이지</th>
        <td>{{convertHomepage homepage}}</td>
    </tr>
</script>
```
- 템플릿과 함수를 정의해준다. 
```js
// 템플릿 등록
        const template1 = Handlebars.compile(document.querySelector('#my-tmpl').innerHTML);
        /** Handlebars 라이브러리에 helper함수 등록(index.html과 동일) */
        Handlebars.registerHelper('convertPhone', value => value && `<a href="tel:${value}">${value}</a>`);
        Handlebars.registerHelper('convertEmail', value => value && `<a href="mailto:${value}">${value}</a>`);
        Handlebars.registerHelper('convertHomepage', value => value && `<a href="${value}" target="_blank">${value}</a>`);
```
- 함수를 사용하여 tbody 내부에 삽입한다.
```js
// 결과를 화면에 출력함.
            document.querySelector('my-table tbody') = template1(result.item);
```


