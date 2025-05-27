# 📌 0. 삼성 클론 코딩
### 📌 0-1. swipper에서 넘겨주는 페이지 버튼 만들기
- 우선 loop가 true일때 slideToLoop(idx)를 사용할 수 있어서 이를 true로 켜준다. 만약 loop가 아니어도 할 수 있는 방법은 있다.
- 버튼에 data로 인덱스를 넣어두고 클릭시 해당 인덱스로 이동하는 구조이다.
```js
document.querySelectorAll('.custom-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                const idx = Number(e.currentTarget.dataset.index); // his.dataset.index 값은 항상 문자열
                swiper.slideToLoop(idx); // loop:true일 때 사용, 아니면 slideTo(idx)
            });
        });
```

### 📌 0-2. 넘겨주는 페이지 버튼에 차오르는 기능 추가하기
- 버튼에 클릭이벤트를 만들어서 해당 인덱스와 같은 swipper로 넘어가기
```js
document.querySelectorAll('.custom-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                const idx = Number(e.currentTarget.dataset.index); // his.dataset.index 값은 항상 문자열
                swiper.slideToLoop(idx); // loop:true일 때 사용, 아니면 slideTo(idx)
            });
        });
```
- swiper.on('slideChange', function()): swiper 슬라이더에서 슬라이드가 바뀔 때(자동/수동 상관없이)마다 이 안에 있는 함수를 자동으로 실행한다는 의미이다. 
- swiper.realIndex: 현재 슬라이드의 인덱스
- toggle('active', 조건식) 이렇게 **두 번째 인자(조건식)**을 주면, 조건이 true일 때 → active 추가 조건이 false일 때 → active 제거 즉, 조건에 따라 무조건 추가 또는 제거만 하게 할 수 있다. 원래는 클래스 명만 주고 있으면 제거 없으면 추가하는 메서드이다.
- bar.classList.toggle('active', swiper.realIndex === i); : swiper.realIndex === i 현재 인덱스와 버튼 인덱스가 같으면 active를 활성화한다.
- swiper.emit('slideChange'); : 슬라이드가 바뀌는 이벤트를 강제로 처리해줘 !
- 버튼 높이가 2px인데 border가 1px씩 차지해서 색이 안바뀌어 보일 수 있다.
- 버튼 안에 div를 넣을 수 있다.
- 버튼 내부에 div를 넣은 다음에 active가 넘어왔을 때 배경색이 흰색인 div가 넘어가는 시간인 3초에 걸쳐서 width가 0에서 100%로 늘어나면 된다.
```js
        swiper.on('slideChange', () => {
            const btns = document.querySelectorAll('.custom-btn');
            btns.forEach((btn, i) => {
                btn.classList.toggle('active', swiper.realIndex === i);
            });
        });

        // 페이지 로드시 최초 active
        swiper.emit('slideChange');
```
```css
.sliding-main {
    max-width: 1440px;
    margin: auto;
    aspect-ratio: 21 / 9;
    overflow: hidden;
    position: relative;

    .custom-pagination {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 24px;  
        z-index: 1000;
        display: flex;
        justify-content: center;
        gap: 2vw;
        background: transparent;
        pointer-events: auto; 
        width: 95%;

        .custom-btn {
            width: 6vw;   
            height: 2px;
            background-color: #bbb;
            border-radius: 2px;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            border: 0;
            padding: 0;

            .innerbar {
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                width: 0;
                background: #fff;
                border-radius: 2px;
                border: 0;
                padding: 0;
            }
        
            &.active {
                .innerbar {
                    width: 100%;
                    transition: width 3s;
                }
            }
        }
    }
}
```

### 📌 0-3. 버튼 마우스를 올렸을 때 배경의 종류에 따라 다른 색의 버튼 고유 글자가 나오게 하기
- 우선 '.custom-btn'인 버튼들이 많으므로 모두 선택해서(querySelectorAll) 객체로 만들어야함.
- 또한 mouseover가 있으면 mouseout이 있어야 함을 잊으면 안된다.
- swiper.realIndex는 숫자타입이다. 
```js
const customBtns = document.querySelectorAll('.custom-btn');

[...customBtns].forEach(v => {
    v.addEventListener('mouseover', e => {
        e.preventDefault();
        const btnTexts = document.querySelectorAll('.btntext');
        
        [...btnTexts].forEach(v2 => {
            if (v2.dataset.index === e.currentTarget.dataset.index) {
                if (swiper.realIndex === 0){
                    v2.style.color = 'rgb(255, 255, 255)';
                }
                
                else {
                    v2.style.color = 'rgb(0, 0, 0)';
                }
            }
        })
    })

    v.addEventListener('mouseout', e => {
        e.preventDefault();
        const btnTexts = document.querySelectorAll('.btntext');
        
        [...btnTexts].forEach(v2 => {
            v2.style.color = 'rgba(240, 248, 255, 0)';
        })
    })
})
```


# 📌 1. 입력 수정 삭제 모듈화
### 📌 1-1. 일반객체와 formData 객체의 차이
- 이 둘은 설계철학 부터 달라서 이들을 구분할 필요가 있다.
- 일반 객체는 당연히 js 내부에서 일반적인 용도로 사용되므로 js 객체 리터럴로 작성되어있고 서버에서 데이터를 보내려면 직접 json.stringify로 JSON으로 변형을 해주어야 한다.
- formData는 HTML 폼 데이터를 그대로 담아 서버에 전송하기 위한 용도로 body에 넣어 바로 전달 가능하고 내부는 키, 벨류 쌍으로 값을 관리하고 있다. 다만 내부에는 문자열이나 파일밖에 벨류값으로 가질 수 없다.
- 자동으로 multipart/form-data 형식으로 인코딩되어 전송됨
- 이때 FormData는 객체처럼 보이지만 일반 객체처럼 키 값 접근(formData.key)이 안 되고, 반드시 append, get, set 같은 메서드로 값을 다뤄야하며 FormData는 같은 key를 여러 번 추가할 수 있어서(일반 자바 스크립트 객체는 불가능 - 예 취미:운동, 취미:음악), key-value 쌍이 "리스트"(엔트리 구조가 중복되어 순서있는 목록처럼 저장) 구조이다.

### 📌 1-2. 로그 메세지 관리
- 처음에 이를 선언함으로써 앞으로 생길 로그들을 객체 이름과 한국시간과 함께 묶어서 저장하게 해준다. 
- 로그가 닫히는 시점까지의 모든 로그가 들여쓰기되어 표시된다.
```js
console.group(`FetchHelper ::: ${new Date().toLocaleString()}`);
```

### 📌 1-3. constructor 프로퍼티
- 모든 객체는 자신을 만든 생성자(함수/클래스)를 constructor에 저장하고 있음.
- 즉 프로토타입 체인으로 연결된 상위 부모를 나타낸다.
- 아래는 url의 뿌리가 URL 객체가 아니고 문자열이면 URL객체로 만들어준다는 것을 의미한다.
```js
if (url.constructor !== URL) {
            url = new URL(url);
        }
```

### 📌 1-4. 폼 태그로 만들어주기
- HTMLFormElement는 폼 태그의 객체를 의미하고 이 경우에는 전체는 한번에 formData로 만들어 줄 수 있다.
- 아래 for문은 그냥 일반 js 객체인 경우 일일히 for문을 돌리면서 formData로 바꿔준다.
```js
if (method.toLocaleUpperCase() !== 'GET' && params) {
            if (params.constructor !== FormData){
                switch (params.constructor) {
                    case SubmitEvent:
                        params = new FormData(params.currentTarget);
                        break;
                    case HTMLFormElement:
                        params = new FormData(params);
                        break;
                    default:
                        const tmp = structuredClone(params);
                        params = new FormData();

                        for (const t in tmp) {
                            params.set(t, tmp[t]);
                        }
                        break;
                }
            }
        }
```

### 📌 1-5. URLSearchParams 생성자
- URLSearchParams 생성자는 다양한 형태의 입력을 받아 자동으로 쿼리 파라미터(key–value 쌍) 객체로 변환해 준다.
- 즉 어떤 “키–값” 집합이든 받아들이며 이로인해 복잡한 생각 안하고 쿼리 문자열을 쉽게 다룰 수 있다.
- 또 .entries()로 값을 키, 값을 동시에 뽑아낼 수 있다.
```js
// 1) 문자열
const sp1 = new URLSearchParams("x=10&y=20");

// 2) 객체 리터럴
const sp2 = new URLSearchParams({ x: 10, y: 20 });

// 3) 2중 배열
const sp3 = new URLSearchParams([ ["x","10"], ["y","20"] ]);

// 4) FormData
const form = new FormData();
form.append("x", 10);
form.append("y", 20);
const sp4 = new URLSearchParams(form);
```
```ini
x=10&y=20
```
- 이를 통한 get 메서드 디자인
- url.search = searchParams.toString(); 여기서 앞에 ?는 자동으로 붙여서 들어간다.
```js
get: async function (url, params) {

        if (url.constructor !== URL) {
            url = new URL(url);
        }

        if (params) {
            switch (params.constructor) {
                case SubmitEvent:
                    params = new FormData(params.currentTarget);
                    break;
                case HTMLFormElement:
                    params = new FormData(params);
                    break;
            }

            const searchParams = new URLSearchParams(params);
            url.search = searchParams.toString();
        }

        return await this.__request(url, 'GET');
    }
```
- 이때 호출조건이 2개면 =&처럼 붙어버려서 에러가 뜬다. 그래서 아래와 같을때는 조건 분기해주는게 낫다.
```js
try {
                    result = await fetchHelper.get('http://localhost:8080/students', {
                        _sort: 'id',
                        _order: 'desc',
                        name_like: keyword,
                        department_id: dept[dept.selectedIndex].value
                    });
                }
```
```js
if (params.constructor === FormData) {
    for (const p of params.keys()) {
        const value = params.get(p);
        if (value) {
            url.searchParams.set(p, value);
        }
    }
} else {
    for (const p in params) {
        const value = params[p];
        if (value) {
            url.searchParams.set(p, params[p]);
        }
    }
}
```


### 📌 1-6. 모듈 이용해서 학생 정보에 학과 검색도 가능하게 하기
- 드롭다운의 option 값이 바뀌었을때 getStudentsList를 호출하여 전체 값을 한번 더 업데이트한다.
```js
/** 학과 목록 조회하기 */
            (async () => {
                let result = null;

                try {
                    result = await fetchHelper.get("http://localhost:8080/departments", {
                        _sort: 'id',
                        _order: 'asc'
                    });
                } catch (err) {
                    alert(err.message);
                    return;
                }

                // 학과 목록 데이터를 드롭다운에 적용하기
                const departmentDropdown = document.querySelector("#department_id");

                result.item.forEach((v, i) => {
                    const option = document.createElement("option");
                    option.setAttribute('value', v.id);
                    option.innerHTML = v.dname;
                    departmentDropdown.appendChild(option);
                });
            })();

            // 드롭다운의 change 이벤트가 발생했을 때, 학생목록 함수를 콜백으로 연결
            document
                .querySelector("#department_id")
                .addEventListener('change', getStudentsList);
```

### 📌 1-7. 디버깅 습관
- 에러가 안뜰때는 정보가 도착하고 나가는 곳에 console.log를 찍어보자

