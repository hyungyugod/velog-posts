# 📌 0. 대화
### 📌 0-1. 웹브라우저의 캐시에 대해
- 웹 브라우저 캐시는 한 번 방문한 웹사이트의 이미지나 파일을 내 컴퓨터에 잠시 저장해두었다가, 다음에 같은 사이트에 들어갈 때 더 빠르게 보여주기 위해 사용하는 임시 저장소이다.
- 보통 **내 컴퓨터의 하드디스크(SSD/HDD)**에 있는, 브라우저가 관리하는 특별한 폴더에 저장된다. 
- 저장 공간이 부족해지면 오래된 캐시부터 자동으로 삭제된다.
- Ctrl + Shift + Delete (브라우저 공통)으로 캐시를 수동으로 삭제할 수 있다.
- 혹은 개발자 도구를 열고 새로고침을 우클릭해서 강력 새로고침을 할 수 있다.

### 📌 0-2. CDN(Content Delivery Network)에 대하여
- 서버가 한국에만 있으면, 미국이나 유럽, 일본 등 먼 나라에서 접속할 때 느리게 열릴 수 있기 때문에 전 세계 여러 곳(도시)에 파일을 미리 복사해 두는 네트워크를 만들어 놓는다.
- 이 네크워크는 엣지 서버를 통해 운영되는데 엣지 서버는 가장자리라는 의미에서 사용자와 가장 가까운 위치(지역/도시/나라 등)에 배치된 서버를 의미한다.
- 이는 공용캐시로서 같은 ISP(Internet Service Provider)의 여러 사용자가 함께 사용 가능하다.
- 라이브러리의 cdn들은 cdnjs에 모여있다.

### 📌 0-3. 의존성 관리도구에 대하여
- Dependency는 내가 만드는 프로그램(프로젝트)이 제대로 동작하기 위한 필요한 외부 코드(라이브러리, 패키지 등)을 의미한다.
- 직접 다운로드/설치/업데이트/버전 관리를 대신 해주는 것이 의존성 관리 도구이다.
- gradle (Java, Kotlin 등)은 자바에서 쓰는 의존성 관리도구였고 파이썬에서 pip install하던 것도 pip이라는 의존성 관리도구를 활용한 것이었다.
- javascript에서의 의존성 관리도구는 npm = Node Package Manager이다. 여기서 npm install에서 원하는 라이브러리를 명시하면 node modules에 다운받아진다.
- 이때 납품할때는 node modules 파일을 빼고 넘기는데 이때 남아있는 package.json에 사용한 Dependency가 기록되어있는데 이 파일이 있는 폴더에서 npm install만 치면 자동으로 파일들이 다운받아 진다.

### 📌 0-4. 원시값의 자동 래퍼객체 변환
- 래퍼 객체: 원시값(primitive value: number, string, boolean 등)에
객체처럼 메서드와 프로퍼티를 쓸 수 있게 해주는 임시 객체이다.
- Number 객체: let obj = new Number(123); // Number 객체
- Object 객체: let obj2 = new Object({ x: 1 }); // Object 생성자로 만든 객체
- let obj = new String("hello"); // String 객체
- let obj = new Boolean(true);  // Boolean 객체
- 이는 매서드 호출을 인식하면 자동 변환된다.
```yaml
원시값(숫자) n
   |
   |  (메서드 호출)
   V
[Number 객체로 변신]
   |
   |  (toFixed 실행)
   V
[메서드 결과 반환]
   |
   |  (임시 객체 소멸)
   V
최종 결과만 남음!
```

# 📌 1. fslightbox
- https://fslightbox.com/
- https://fslightbox.com/javascript : 사용법은 여기에 나와있다.
- 이미지, 영상을 클릭하면 크게 보여주는 라이브러리 같은 이미지끼리 묶어서 큰 화면에서 넘길 수 있는 기능을 제공한다.
> Every <a> element (anchor element) with the "data-fslightbox" attribute opens the lightbox. The content behind the URL or path passed to the "href" attribute will be displayed in the lightbox. There is no need to place anything specific inside of an <a> element. 
- -> <a> 태그에 data-fslightbox 속성만 추가하면 됨, href에 있는 이미지(또는 동영상) 파일이 라이트박스로 표시됨, a 태그 안에 이미지가 아니더라도, 버튼이나 텍스트 등 아무 내용이나 넣을 수 있음
> Every unique value of the "data-fslightbox" attribute will be treated as an instance (or gallery).
To access a specific instance, use its methods, attach events to it, etc., you need to use the global JavaScript "fsLightboxInstances" object.
- -> "data-fslightbox" attribute를 가진 값들은 각각의 객체로 분류되며(값은 값이면 같은 객체에 포함된다.) 이 객체에 접근하기 위해선 fsLightboxInstances를 이용해야한다.
> If you have only one instance on a page, you can access it using the global"fsLightbox" object. (You can use this object when you have multiple instances as well, but it will affect only the one that is declared last.) "fsLightbox.open();"
- -> 하나의 객체만 만들었다면 해당 함수로 접근할 수 있지만 여러개의 객체가 있다면 가장 마지막에 사용한 하나의 객체에 적용된다.
> To incorporate new galleries or updates of existing ones (through adding or modifying <a> elements), invoke the global "refreshFsLightbox" function.
- 새로운 사항을 업데이트하기 위해서 refreshFsLightbox()를 호출하면 업데이트 할 수 있다.
```js
var a = document.createElement("a");
a.setAttribute("data-fslightbox", "gallery");
a.setAttribute("href", "/Images/2.jpg");
document.body.appendChild(a);
refreshFsLightbox();
```
```html
<body>
    <h1>fslightbox</h1>
    <p>https://fslightbox.com/javascript</p>

    <h2>Single Gallery</h2>
    <a data-fslightbox="my-single" href="assets/img/img1.png">
        <img src="assets/img/img1.png" width="200" />
    </a>

    <h2>Multi Gallery</h2>
    <!-- data-fslightbox의 값을 동일하게 지정한다. -->
    <a data-fslightbox="my-multi" href="assets/img/img2.png">
        <img src="assets/img/img2.png" width="200" />
    </a>
    <a data-fslightbox="my-multi" href="assets/img/img3.png">
        <img src="assets/img/img3.png" width="200" />
    </a>
    <a data-fslightbox="my-multi" href="assets/img/img4.png">
        <img src="assets/img/img4.png" width="200" />
    </a>

    <h2>Youtube Single Gallery</h2>
    <!--
    [Youtube 썸네일]
    - 동영상 배경 썸네일(480x360): https://img.youtube.com/vi/영상코드/0.jpg
    - 동영상 시작지점 썸네일(120x90): https://img.youtube.com/vi/영상코드/1.jpg
    - 동영상 중간지점 썸네일(120x90): https://img.youtube.com/vi/영상코드/2.jpg
    - 동영상 끝 지점 썸네일(120x90): https://img.youtube.com/vi/영상코드/3.jpg
    - 플레이상태 썸네일(1280x720): https://img.youtube.com/vi/영상코드/maxresdefault.jpg
    - 강좌최소화 썸네일(640x480): https://img.youtube.com/vi/영상코드/sddefault.jpg
    - 고화질 썸네일(480x360): https://img.youtube.com/vi/영상코드/hqdefault.jpg
    - 중화질 썸네일(320x180): https://img.youtube.com/vi/영상코드/mqdefault.jpg
    - 보통품질 썸네일(120x90): https://img.youtube.com/vi/영상코드/default.jpg
    -->

    <a data-fslightbox="youtube-single" href="https://www.youtube.com/watch?v=SmsINbHbWtk">
        <img src="https://img.youtube.com/vi/SmsINbHbWtk/maxresdefault.jpg" width="200" />
    </a>

    <h2>Youtube Multi Gallery</h2>
    <a data-fslightbox="youtube-multi" href="https://www.youtube.com/watch?v=JUzPQ0JaLHE">
        <img src="https://img.youtube.com/vi/JUzPQ0JaLHE/maxresdefault.jpg" width="200" />
    </a>
    <a data-fslightbox="youtube-multi" href="https://www.youtube.com/watch?v=OjuwbwbvQjQ">
        <img src="https://img.youtube.com/vi/OjuwbwbvQjQ/maxresdefault.jpg" width="200" />
    </a>
</body>
</html>
```

# 📌 2. glider
- 화면이 넘어가는 처리를 버튼과 함께 구현해주는 라이브러리이다.
- https://nickpiscitelli.github.io/Glider.js/ 에 사용방법이 자세히 나와있다.
```html
    <title>04-glide</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/glider-js/1.7.9/glider.css"/>
    <style>

        * {
            margin: 0;
            padding: 0;
        }
        
        .glider-contain {
            width: 100%;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }
        
        .glider-contain .glider,
        .glider-contain .glider div,
        .glider-contain .glider div img {
            width: 100%;
            height: 100%;
        }
        
        .glider-contain .glider div img {
            object-fit: cover;
        }
        
        /* 이전, 다음 버튼 설정 */
        .glider-prev, .glider-next {
            position: absolute;
            left: 30px;
            top: 50%;
            transform: translateY(-50%);
            color: #fff;
            font-size: 100px;
            z-index: 999;
        }
        
        .glider-next {
            left: auto;
            right: 30px;
        }
        
        /* 페이지 표시 동그라미 설정 */
        .dots {
            position: absolute;
            z-index: 999;
            left: 50%;
            transform: translateX(-50%);
            bottom: 30px;
        }
        
        .glider-dot {
            background-color: #fff;
        }
        
        .glider-dot.active {
            background-color: #ff0;
        }
        </style>
        
</head>
<body>
    <div class="glider-contain">
        <div class="glider">
            <div><img src="assets/img/img1.png"></div>
            <div><img src="assets/img/img2.png"></div>
            <div><img src="assets/img/img3.png"></div>
            <div><img src="assets/img/img4.png"></div>
        </div>
        
        <button aria-label="Previous" class="glider-prev">«</button>
        <button aria-label="Next" class="glider-next">»</button>

        <div role="tablist" class="dots"></div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/glider-js/1.7.9/glider.min.js"></script>
    <script>
        new Glider(document.querySelector('.glider'), {
        slidesToShow: 1, // 한번에 1개만 보여줌
        dots: '.dots', // 도트를 표시할 요소
        draggable: true, // 드래그 가능 여부
        arrows: { // 화살표 사용 여부 -> 아래 클래스를 갖는 요소를 찾아서 기능을 부여한다.
            prev: '.glider-prev',
            next: '.glider-next'
        }
        });
    </script>
</body>
```

# 📌 3. sweetalert
- 알람을 표시하는 라이브러리이다.
- 생성자에 다양한 값을 조정하여 알림 객체를 생성하고 객체가 가지고 있는 메서드를 사용할 수 있다.
- then은 객체가 리턴하는 값에 따라서 다음 알림을 띄울 수 있는 메서드이다.
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Hello, Javascript</title>
    <link href="https://cdn.jsdelivr.net/npm/sweetalert2@11.7.5/dist/sweetalert2.min.css" rel="stylesheet" />
    <style>
        .title {
            color: white;
            font-size: 36px;
            text-shadow: 0 1px #000;
        }
        .content {
            color: white;
            font-size: 18px;
            text-shadow: 0 1px #000;
        }
    </style>
</head>
<body>
    <button id="btn1" type="button">button1</button>
    <button id="btn2" type="button">button2</button>
    <button id="btn3" type="button">button3</button>
    <button id="btn4" type="button">button4</button>
    <button id="btn5" type="button">button5</button>
    <button id="btn6" type="button">button6</button>

    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.7.3/dist/sweetalert2.all.min.js"></script>
    <script>
        document.querySelector("#btn1").addEventListener("click", (e) => {
            // 메시지만 적용하여 확인창 표시
            new Swal("안녕하세요.");
        });

        document.querySelector("#btn2").addEventListener("click", (e) => {
            // 메시지 제목, 내용, 종류
            // 종류 -> 'success', 'warning', 'info', 'question', 'error'
            new Swal("탈퇴확인", "정말 탈퇴하시겠습니까?", "question");
        });

        document.querySelector("#btn3").addEventListener("click", (e) => {
            // 옵션 지정하여 메시지 창 표시
            new Swal({
                title: "<font color='red'>에러</font>", // 제목
                html: "요청하신 처리에 실패했습니다.<br/>관리자에게 문의 바랍니다.", // 내용
                icon: "error", // 종류
                showCloseButton: true, // 닫기 버튼 표시 여부
                confirmButtonText: "확인", // 확인버튼 표시 문구
                confirmButtonColor: "#000", // 확인버튼 색상
                showCancelButton: true, // 취소버튼 표시 여부
                cancelButtonText: "취소", // 취소버튼 표시 문구
                cancelButtonColor: "#f60", // 취소버튼 색상
            });
        });

        document.querySelector("#btn4").addEventListener("click", (e) => {
            // 확인, 취소버튼에 따른 후속 처리 구현
            new Swal({
                title: "확인!", // 제목
                text: "정말 선택하신 항목을 삭제하시겠습니까?", // 내용
                icon: "warning", // 종류
                confirmButtonText: "Yes", // 확인버튼 표시 문구
                showCancelButton: true, // 취소버튼 표시 여부
                cancelButtonText: "No", // 취소버튼 표시 문구
            }).then((result) => {
                console.log(result);
                // 확인 버튼 클릭시
                if (result.value) {
                    new Swal("삭제", "성공적으로 삭제되었습니다.", "success");
                } else if (result.dismiss === "cancel") {
                    // 취소버튼 눌러질 경우
                    new Swal("취소", "삭제가 취소되었습니다.", "error");
                }
            });
        });

        document.querySelector("#btn5").addEventListener("click", (e) => {
            // 이미지 표시 -> 종류(icon)는 지정할 수 없음
            new Swal({
                title: "Thank you!", // 제목
                text: "성원에 감사합니다.", // 내용
                imageUrl: "assets/img/img5.png", // 이미지 경로
                imageWidth: 480, // 이미지 가로 크기
                imageHeight: 240, // 이미지 세로 크기
            });
        });

        document.querySelector("#btn6").addEventListener("click", (e) => {
            // 배경 지정
            new Swal({
                title: '<span class="title">Thank you!</span>', // 제목(CSS클래스 지정)
                html: '<span class="content">성원에 감사드립니다.</span>', // 내용(CSS클래스 지정)
                width: 600, // 팝업 가로 크기 (내용에 맞게 지정됨)
                padding: "100px", // 팝업 여백 (CSS스타일명령 모두 적용 가능)
                background: "#fff url(assets/img/img5.png) center center/cover no-repeat", // 배경설정
            });
        });
    </script>
</body>
</html>
```

# 📌 4. chartjs
- 그래프를 그려주는 라이브러리이다.
- canvas 태그는 직접 js로 선이나 점, 도형을 그릴 수 있도록 해준다.
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>documenttitle</title>
    <style>
        * {
            box-sizing: border-box;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
        }
        .subplot {
            width: 50%;
            padding: 10px;
        }
        .subplot > div {
            width: 100%;
        }
        .subplot-item {
            width: 100%;
            height: 400px;
        }
    </style>
</head>
<body>
    <h3>chart.js 예제</h3>
    <p>
        <a href="https://www.chartjs.org/">https://www.chartjs.org/</a>
    </p>
    <br/>
    <div class="container">
        <div class="subplot">
            <h2>1. 선형(line) 그래프</h2>
            <div class="subplot-item">
                <canvas id="mychart1"></canvas>
            </div>
        </div>
        <div class="subplot">
            <h2>2. 막대(bar) 그래프</h2>
            <div class="subplot-item">
                <canvas id="mychart2"></canvas>
            </div>
        </div>
        <div class="subplot">
            <h2>3. 다중 막대 그래프</h2>
            <div class="subplot-item">
                <canvas id="mychart3"></canvas>
            </div>
        </div>
        <div class="subplot">
            <h2>4. polar area Chart</h2>
            <div class="subplot-item">
                <canvas id="mychart4"></canvas>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <script>
        const names = ["강아지", "고양이", "토끼", "햄스터", "다람쥐", "고슴도치"];
        const score1 = [99, 88, 92, 63, 71];
        const score2 = [98, 92, 79, 73, 68, 63];

        // 1개씩 가져와서 변수에 저장
        const mychart1 = document.getElementById("mychart1");
        const mychart2 = document.getElementById("mychart2");
        const mychart3 = document.getElementById("mychart3");
        const mychart4 = document.getElementById("mychart4");

        /* 1. 선형 그래프 */
        new Chart(mychart1, {
            type: "line", // 타입 종류 (line, bar, pie, polarArea, doughnut, scatter)
            data: {
                labels: names, // x축
                datasets: [
                    {
                        label: "강아지 점수",
                        data: score1, // y 데이터 배열 --> [99, 88, 92, 63, 71]
                        borderWidth: 0.5, // 선 굵기
                        borderColor: "#6699FF", // 선 색상
                        backgroundColor: "offset:0",
                    },
                ],
            },
        });

        /* 2. 막대 그래프 그리기 */
        new Chart(mychart2, {
            type: "bar",
            data: {
                labels: names,
                datasets: [
                    {
                        label: "점수",
                        data: score2,
                        borderWidth: 0.5,
                        // 아래와 같이, border와 background: 동일 색상으로 처리하면, border는 흰색, background는 반투명
                        // 이 배열의 순서는 x축과 같은 순서 -> 즉, 데이터별로 다른 색상
                        borderColor: [
                            "rgba(255,99,132,1)", "rgba(54,162,235,1)", "rgba(255,206,86,1)",
                            "rgba(75,192,192,1)", "rgba(153,102,255,1)", "rgba(255,159,64,1)",
                        ],
                        backgroundColor: [
                            "rgba(255,99,132,0.2)", "rgba(54,162,235,0.2)", "rgba(255,206,86,0.2)",
                            "rgba(75,192,192,0.2)", "rgba(153,102,255,0.2)", "rgba(255,159,64,0.2)",
                        ],
                    },
                ],
            },
            options: {
                maintainAspectRatio: false, // 기본 비율(가로:세로 or 1:1), 막대그래프가 정밀 사용되는 옵션
            },
        });

        /* 3. 다중 막대 그래프 그리기 */
        new Chart(mychart3, {
            type: "bar",
            data: {
                labels: names,
                datasets: [
                    {
                        label: "강아지",
                        data: score1, // --> [99, 88, 92, 63, 71]
                        borderWidth: 0.5,
                        borderColor: "rgba(54,162,235,1)",
                        backgroundColor: "rgba(54,162,235,0.2)",
                    },
                    {
                        label: "점수",
                        data: score2, // --> [98, 92, 79, 73, 68, 63]
                        borderWidth: 0.5,
                        borderColor: "rgba(255,99,132,1)",
                        backgroundColor: "rgba(255,99,132,0.2)",
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "left", // left, right, top, bottom
                        title: {
                            display: true,
                            text: "강아지와 점수",
                        },
                    },
                },
            },
        });

        /* 4. polar area 차트 */
        new Chart(mychart4, {
            type: "polarArea",
            data: {
                labels: names,
                datasets: [
                    {
                        label: "점수",
                        data: score1,
                        borderWidth: 0.5,
                        borderColor: [
                            "rgba(54,162,235,1)", "rgba(255,206,86,1)", "rgba(75,192,192,1)",
                            "rgba(153,102,255,1)", "rgba(255,159,64,1)", "rgba(255,99,132,1)",
                        ],
                        backgroundColor: [
                            "rgba(54,162,235,0.2)", "rgba(255,206,86,0.2)", "rgba(75,192,192,0.2)",
                            "rgba(153,102,255,0.2)", "rgba(255,159,64,0.2)", "rgba(255,99,132,0.2)",
                        ],
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "left",
                        title: {
                            display: true,
                            text: "강아지와 점수",
                        },
                    },
                },
            },
        });
    </script>
</body>
</html>
```

# 📌 5. 삼성 프로젝트
### 📌 5-1. swiper 라이브러리 사용시 이미지 짜부 문제
- 아래 두 요소를 가장 큰 메인에 넣어주면 해결된다.
```css
aspect-ratio: 21 / 9;  /* 슬라이더 전체 비율 고정 */
overflow: hidden;
```

### 📌 5-2. 모바일에서 swiper 사용문제
- swiper는 swiper안에 모바일, 데스크탑 wrapper 2개를 넣으면 안되는 문제가 있어서 html 코드안에서 이미지만 바뀌고 미디어 쿼리로 해당 일을 수행하여야한다.
- media query 안에서 .sliding-main { aspect-ratio: 9 / 16; } 이렇게 작성하면 오직 aspect-ratio 속성만 덮어씌워진다.
- css 내부에서 모바일을 실현할 때는 무조건 큰 틀 안에서 다 선언하고 꼬이는 부분만 아래서 중첩해서 짜는 것이 좋다.
- 스위퍼 고려한 html 변경
```html
<div class="sliding-main swiper">
        <div class="swiper-wrapper">
            <div class="img-wrapper swiper-slide">
                <img class="pc-img" src="img/sliding-main-img1.jpg" alt="main 이미지">
                <img class="mo-img" src="img/mo-sliding-main-img1.jpg" alt="main 이미지">

                <div class="text-wrapper">
                    <p>즉시할인 6% + 구매자 전원 신세계상품권 3만원 증정!</p>
                    <ul>
                        <li><a href="#" class="more">더 알아보기</a></li>
                        <li><a href="#" class="button">구매 혜택 보기</a></li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="swiper-pagination"></div>

        <div class="swiper-button-prev"></div>
        <div class="swiper-button-next"></div>

        <div class="swiper-scrollbar"></div>
    </div>
```
- 스위퍼 고려한 css 변경
```css
.sliding-main {
    max-width: 1440px;
    margin: auto;
    aspect-ratio: 21 / 9;
    overflow: hidden;

    .img-wrapper {
        margin: auto;
        max-width: 1440px;
        position: relative;

        img {
            width: 100%;
            height: 100%;
        }
        .pc-img { display: block; }
        .mo-img { display: none; }
    }

    .text-wrapper {
        position: absolute;
        bottom: 15%;
        left: 6.11%;
        display: flex;
        flex-direction: column;
        gap: 3.2rem;
        margin-bottom: 0.3rem;

        p {
            color: white;
            font-size: 1rem;
        }
        ul {
            list-style: none;
            display: flex;
            gap: 1.5rem;

            .more {
                color: white;
                font-size: 0.9rem;
                text-decoration: underline;
                font-weight: 580;
            }
            .button {
                font-size: 0.9rem;
                background-color: white;
                padding: 0.7rem 1.5rem;
                color: #000;
                border-radius: 1.3rem;
                font-weight: 580;
            }
        }
    }

    @media (max-width: 769px) {
        aspect-ratio: 9 / 16;

        .img-wrapper {
            .pc-img { display: none; }
            .mo-img { display: block; }

            .text-wrapper {
                position: absolute;
                bottom: clamp(6rem, 6rem, 7rem);
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 1.8rem;
                margin-bottom: 0.3rem;

                p {
                    font-size: 0.8rem;
                    white-space: wrap;
                }
                ul {
                    gap: 1.5rem;

                    .more {
                        font-size: 0.8rem;
                    }
                    .button {
                        font-size: 0.8rem;
                        padding: 0.5rem 2rem;
                        border-radius: 1rem;
                    }
                }
            }
        }
    }
}
```

### 📌 5-3. swiper 객체 설정 바꾸기
- direction: vertical을 horizontal로 바꿔야 가로로 움직인다. 스위퍼의 점은 움직이는 방향에 맞춰 생성되는 것 같다.
- 기본적으로 내가 만들고 있는 사이트에서 f12를 눌러서 요소의 클래스 명을 확인한 뒤에 해당 클래스의 스타일을 css에서 지정해주면 된다.
- 아래는 대략적인 버튼 설정이다.
```css
    .swiper-button-next{
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        background-color: rgba(15, 15, 15, 0.027);
        padding: 30px;
        border-radius: 50%;

        &:after {
            font-size: 20px;
            color: #f7f7f7;
        }
    }

    .swiper-button-prev {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        background-color: rgba(15, 15, 15, 0.027);
        padding: 30px;
        border-radius: 50%;
        &:after {
            font-size: 20px;
            color: #f7f7f7;
        }
    }
```

# 📌 6. 자바스크립트 예외처리

### 📌 6-1. 예외처리 기본
- js는 에러를 정의할때 새로운 에러 클래스를 정의하여 사용한다.
```js
/** 에러 객체를 활용한 예외처리 */
function foo(id, pw) {
    if (!id) {
        // 함수 안에서 에러를 강제로 발생시킬 경우, 이 함수를 호출하는 위치를 에러로 인식한다.
        throw new Error("아이디를 입력하세요.");
    }

    if (!pw) {
        // 함수 안에서 에러를 강제로 발생시킬 경우, 이 함수를 호출하는 위치를 에러로 인식한다.
        throw new Error("비밀번호를 입력하세요.");
    }

    return "로그인 되었습니다.";
}

// try블록 안의 코드는 최소화 하는 것이 프로그램 효율에 좋다.
// 그래서 k값을 정상적으로 리턴 받았다면 그 결과값을 활용하는 처리는 try블록 밖에서 하는것이 좋다.
// 에러 점검이 끝난 후 try~catch 블록 밖에서 k값을 활용하려면
// 변수의 선언 위치가 try블록보다 상위에 위치해야 한다. --> 변수의 스코프 규칙
let a = null;
let b = null;

try {
    a = foo("", "1234");
} catch (err) {
    // 이 블록으로 전달되는 err객체는 5라인에서 생성한 Error 클래스의 객체이다.
    console.log("에러이름: %s", err.name);
    console.log("에러내용: %s", err.message);
}

try {
    b = foo("hello", "");
} catch (err) {
    // 이 블록으로 전달되는 err객체는 9라인에서 생성한 Error 클래스의 객체이다.
    console.log("에러이름: %s", err.name);
    console.log("에러내용: %s", err.message);
}

console.log(a);
console.log(b);
```

### 📌 6-2. 예외처리 활용 회원가입
- html, js
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no" />
    <title>Document</title>
    <style>
        .form-horizontal {
            border: 2px solid #d5d5d5;
            width: 500px;
            margin: 40px auto;
            padding: 0 10px;
            font-size: 14px;
        }
        .field-container {
            display: flex;
            width: 100%;
            margin: 15px 0;
            align-items: center;
        }
        .field-title {
            width: 25%;
            display: block;
        }
        .field-content {
            width: 75%;
            display: block;
        }
        .field-content .form-control {
            width: 100%;
            padding: 5px 0;
            border: 1px solid #eee;
        }
        .field-content input[type='checkbox'],
        .field-content input[type='radio'] {
            width: 18px;
            height: 18px;
        }
        .identify {
            font-size: 16px;
            color: #f00;
            font-weight: 500;
            vertical-align: middle;
        }
        .button-container {
            margin: 20px auto;
            text-align: center;
        }
    </style>
</head>
<body>
<!-- 가입 폼 시작 -->
<form class="form-horizontal" name="join_form" id="join_form">
    <div class="field-container">
        <label for="user_id" class="field-title">아이디 <span class="identify">*</span></label>
        <div class="field-content">
            <input type="text" name="user_id" id="user_id" class="form-control" />
        </div>
    </div>
    <div class="field-container">
        <label for="user_pw" class="field-title">비밀번호 <span class="identify">*</span></label>
        <div class="field-content">
            <input type="password" name="user_pw" id="user_pw" class="form-control" />
        </div>
    </div>
    <div class="field-container">
        <label for="user_pw_re" class="field-title">비밀번호 확인 <span class="identify">*</span></label>
        <div class="field-content">
            <input type="password" name="user_pw_re" id="user_pw_re" class="form-control" />
        </div>
    </div>
    <div class="field-container">
        <label for="user_name" class="field-title">이름 <span class="identify">*</span></label>
        <div class="field-content">
            <input type="text" name="user_name" id="user_name" class="form-control" />
        </div>
    </div>
    <div class="field-container">
        <label for="email" class="field-title">이메일 <span class="identify">*</span></label>
        <div class="field-content">
            <input type="email" name="email" id="email" class="form-control" />
        </div>
    </div>
    <div class="field-container">
        <label for="tel" class="field-title">연락처 <span class="identify">*</span></label>
        <div class="field-content">
            <input type="tel" name="tel" id="tel" class="form-control" />
        </div>
    </div>
    <div class="field-container">
        <label for="gender1" class="field-title">성별 <span class="identify">*</span></label>
        <div class="field-content">
            <label><input type="radio" name="gender" id="gender1" value="M" /> 남자</label>
            <label><input type="radio" name="gender" id="gender2" value="F" /> 여자</label>
        </div>
    </div>
    <div class="field-container">
        <label for="gender1" class="field-title">수강과목 <span class="identify">*</span></label>
        <div class="field-content">
            <label><input type="checkbox" name="subject" id="subject1" value="html" /> HTML</label>
            <label><input type="checkbox" name="subject" id="subject2" value="css" /> CSS</label>
            <label><input type="checkbox" name="subject" id="subject3" value="js" /> JavaScript</label>
            <label><input type="checkbox" name="subject" id="subject4" value="jquery" /> jQuery</label>
            <label><input type="checkbox" name="subject" id="subject5" value="php" /> PHP</label>
        </div>
    </div>
    <div class="button-container">
        <button type="submit">가입하기</button>
        <button type="reset">다시작성</button>
    </div>
</form>
<!-- 참고) RegHelper 검사 객체를 호출하여 DOM에 추가하면. -->
<script src="js/RegHelper.js"></script>
<script type="text/javascript">
    document.querySelector("#join_form").addEventListener("submit", e => {
        e.preventDefault();

        try {
            // 아이디 검사
            regexHelper.minLength("#user_id", 4, '아이디는 최소 4자 이상 입력 가능합니다.');
            regexHelper.maxLength("#user_id", 20, '아이디는 최대 20자까지 입력 가능합니다.');
            regexHelper.engNum("#user_id", '아이디는 영문+숫자로만 입력하세요.');

            // 비밀번호 검사
            regexHelper.value("#user_pw", '비밀번호를 입력하세요.');
            regexHelper.minLength("#user_pw", 4, '비밀번호는 최소 4자 이상 입력 가능합니다.');
            regexHelper.maxLength("#user_pw", 20, '비밀번호는 최대 20자까지 입력 가능합니다.');

            // 비밀번호 확인 검사
            regexHelper.value("#user_pw_re", '비밀번호 확인을 입력하세요.');
            regexHelper.compareTo("#user_pw", "#user_pw_re", '비밀번호 확인이 일치하지 않았습니다.');

            // 이름 검사
            regexHelper.value("#user_name", '이름을 입력하세요.');
            regexHelper.minLength("#user_name", 2, '이름은 최소 2자 이상 입력 가능합니다.');
            regexHelper.maxLength("#user_name", 10, '이름은 최대 10자까지 입력 가능합니다.');
            regexHelper.kor("#user_name", '이름은 한글로만 입력 가능합니다.');

            // 이메일 검사
            regexHelper.value("#email", '이메일을 입력하세요.');
            regexHelper.email("#email", '이메일 형식이 잘못되었습니다.');

            // 연락처 검사
            regexHelper.value("#tel", '연락처를 입력하세요.');
            regexHelper.phone("#tel", '연락처 형식이 잘못되었습니다.');

            // 성별 검사
            regexHelper.check("input[name='gender']", '성별을 선택하세요.');

            // 수강과목 검사 (최소 2개, 최대 4개)
            regexHelper.checkMin("input[name='subject']", 2, '수강과목은 최소 2개 이상 선택해야 합니다.');
            regexHelper.checkMax("input[name='subject']", 4, '수강과목은 최대 4개까지 선택 가능합니다.');

        } catch (e) {
            alert(e.message);
            console.error(e);
            console.log(e.element);
            e.element.value = "";
            e.element.focus();
            return;
        }
        // 가입 완료
        alert("회원가입 검사 완료!!!");
        e.currentTarget.reset();
    });
</script>
</body>
</html>
```
- js 파일
```js
function getValueError(msg = '정상적인 요청이 아닙니다.', selector = undefined) {
    const error = new Error(msg);
    error.element = document.querySelector(selector);
    return error;
}

/**
 * 정규표현식을 기반으로 입력값에 대한 검사 결과를 반환하는 클래스.
 * HTML에서 사용하는 각종 <input> selector에 대한 검증 메서드를 정의함.
 */
const regexHelper = {
    /**
     * 입력값이 존재하는지 검사한다.
     * @param {string} selector 검사할 대상 <input>요소의 selector
     * @param {string} msg 검사에 실패할 경우 표시할 메시지
     */
    value: function(selector, msg) {
        const content = document.querySelector(selector).value;

        if (content === undefined || content === null || (typeof content === 'string' && content.trim().length === 0)) {
            throw getValueError(msg, selector);
        }

        return true;
    },

    /**
     * 입력값이 지정된 글자수를 초과하는지 검사한다.
     * @param {string} selector 검사할 대상 <input>요소의 selector
     * @param {int} len 검사할 글자 수
     * @param {string} msg 검사에 실패할 경우 표시할 메시지
     */
    maxLength: function(selector, len, msg) {
        const content = document.querySelector(selector).value;

        if (content.trim().length > len) {
            throw getValueError(msg, selector);
        }

        return true;
    },

    /**
     * 입력값이 지정된 글자수 미만인지 검사한다.
     * @param {string} selector 검사할 대상 <input>요소의 selector
     * @param {int} len 검사할 글자 수
     * @param {string} msg 검사에 실패할 경우 표시할 메시지
     */
    minLength: function(selector, len, msg) {
        const content = document.querySelector(selector).value;

        if (content.trim().length < len) {
            throw getValueError(msg, selector);
        }

        return true;
    },

    /**
     * 두 입력값이 동일한지 검사한다.
     * @param {string} origin 원본에 해당할 대상 <input>요소의 selector
     * @param {string} compare 검사할 대상 <input>요소의 selector
     * @param {string} msg 검사에 실패할 경우 표시할 메시지
     */
    compareTo: function(origin, compare, msg) {
        this.value(compare, msg);

        var src = document.querySelector(origin).value.trim();   // 원본의 값(공백 제거)
        var dest = document.querySelector(compare).value.trim(); // 비교할 값(공백 제거)

        if (src !== dest) {
            throw getValueError(msg, origin);
        }

        return true; // 성공했을 때만
    },

    /**
     * 체크박스의 체크 여부 검사한다.
     * @param {string} selector 검사할 CheckBox의 대상 selector
     * @param {string} msg 검사에 실패할 경우 표시할 메시지
     */
    check: function(selector, msg) {
        const checkList = Array.from(document.querySelectorAll(selector));
        const checkedItem = checkList.filter((v) => v.checked);

        if (checkedItem.length === 0) {
            throw getValueError(msg, selector);
        }
        return true;
    },

    /**
     * 체크박스 체크 수의 최소 값 검사를 수행한다.
     * @param {string} selector 검사할 CheckBox의 대상 selector
     * @param {int} len 최소 체크 개수
     * @param {string} msg 검사에 실패할 경우 표시할 메시지
     */
    checkMin: function(selector, len, msg) {
        const checkList = Array.from(document.querySelectorAll(selector));
        const checkedItem = checkList.filter((v) => v.checked);

        if (checkedItem.length < len) {
            throw getValueError(msg, selector);
        }
        return true;
    },

    /**
     * 체크박스 체크 수의 최대 값 검사를 수행한다.
     * @param {string} selector 검사할 CheckBox의 대상 selector
     * @param {int} len 최대 체크 개수
     * @param {string} msg 검사에 실패할 경우 표시할 메시지
     */
    checkMax: function(selector, len, msg) {
        const checkList = Array.from(document.querySelectorAll(selector));
        const checkedItem = checkList.filter((v) => v.checked);

        if (checkedItem.length > len) {
            throw getValueError(msg, selector);
        }
        return true;
    },

    /**
     * 입력값이 정규표현식을 만족하는지 검사한다.
     * @param {string} selector 검사할 대상 <input>요소의 selector
     * @param {string} msg 검사에 실패할 경우 표시할 메시지
     * @param {object} regexExpr 검사할 정규표현식
     */
    regexTest: function(selector, msg, regexExpr) {
        this.value(selector, msg);

        // 입력값에 대한 정규표현식 검사 수행
        if (!regexExpr.test(document.querySelector(selector).value.trim())) {
            throw getValueError(msg, selector);
        }

        return true;
    },

    /** 숫자로만 이루어졌는지 검사하기 위한 selector의 값 검사 */
    num: function(selector, msg) {
        return this.regexTest(selector, msg, /^[0-9]+$/);
    },
    /** 영문으로만 이루어졌는지 검사하기 위한 selector의 값 검사 */
    eng: function(selector, msg) {
        return this.regexTest(selector, msg, /^[a-zA-Z]+$/);
    },
    /** 영문과 숫자로만 이루어졌는지 검사하기 위한 selector의 값 검사 */
    engNum: function(selector, msg) {
        return this.regexTest(selector, msg, /^[a-zA-Z0-9]+$/);
    },
    /** 한글로만 이루어졌는지 검사하기 위한 selector의 값 검사 */
    kor: function(selector, msg) {
        return this.regexTest(selector, msg, /^[가-힣]+$/);
    },
    /** 최소한의 이메일 형식인지 검사하기 위한 selector의 값 검사 */
    email: function(selector, msg) {
        return this.regexTest(selector, msg, /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/);
    },
    /** 핸드폰 번호 형식인지 검사하기 위한 selector의 값 검사 */
    cellphone: function(selector, msg) {
        return this.regexTest(selector, msg, /^01([0|1|6|7|8|9])+([0-9]{3,4})+([0-9]{4})$/);
    },
    /** 전화번호 형식인지 검사하기 위한 selector의 값 검사 */
    telphone: function(selector, msg) {
        return this.regexTest(selector, msg, /^0\d{1,2}-\d{3,4}-\d{4}$/);
    },
    /** 핸드폰 및 전화번호 형식 둘다 통과하는지 검사 */
    phone: function(selector, msg) {
        this.value(selector, msg);
        const content = document.querySelector(selector).value.trim();
        const check1 = /^01([0|1|6|7|8|9])+([0-9]{3,4})+([0-9]{4})$/; // 핸드폰 형식
        const check2 = /^0\d{1,2}-\d{3,4}-\d{4}$/; // 전화번호 형식
        if (!(check1.test(content) || check2.test(content))) {
            throw getValueError(msg, selector);
        }
        return true; // 성공했을 때만
    }
};
```