# 📌 0. jQuery Ajax
### 📌 0-1. 두가지 방식의 ajax요청 방법
- Promise 방식의 Ajax는 기존의 fetch에서 요청하던 방식에서 try-catch-finally 처리를 모두 설정할 수 있다.
- beforeSend 시작전, success 성공시, error 실패시, complete 성공, 실패에 상관 없이 맨 마지막에 무조건 호출되는 설정을 양식에서 걸어서 요청할 수 있다.
- 이는 비동기 동작을 함수안에 계속 작성해야 해서 콜백지옥이 생길 수 있다.
```html
<script>
    /** Promise 방식의 Ajax 요청 */
    $("#btn1").on("click", (e) => {
        e.preventDefault();

        // 요청(접속)할 대상 페이지 주소 -> 이 파일의 소스코드로 읽어온다.
        const url = "http://localhost:8080sdf/hello.html";

        $.ajax({
            /** ajax 기본 옵션 */
            cache: false,       // 캐시 사용 금지 처리
            url: url,           // 읽어올 파일의 경로
            method: 'get',      // 통신방식 (get(기본값), post)
            data: {},           // 접속대상에게 전달할 파라미터
            dataType: 'html',   // 읽어올 내용 형식 (json(기본값), html, xml)
            timeout: 30000,     // 타임아웃 (30초)

            // 통신 시작전 실행할 기능 (ex: 로딩바 표시)
            beforeSend: function () {
                console.log("loading...");
            },
            // 통신 성공시 호출할 함수 (파라미터는 읽어온 내용)
            success: function (req) {
                $("#result").append(req);
            },
            // 통신 실패시 호출할 함수 (파라미터는 에러내용)
            error: function (error) {
                alert(`${error.status} Error가 발생함 - ${error.statusText}`);
            },
            // 성공, 실패에 상관 없이 맨 마지막에 무조건 호출됨 ex) 로딩바 닫기
            complete: function () {
                console.log(">> Ajax 통신 종료!!!");
            }
        });
    });
```
- Async Await 방식의 Ajax 요청 
- success, error, complete 콜백도 여전히 실행되나 하지만 실제 결과값이나 에러 처리는 try-catch에서 할 수 있으니 코드 흐름이 동기식처럼 깔끔하게 이어진다.
- 또 에러처리를 에러 처리를 catch에서 일괄적으로 할 수 있어서 깔끔하다.
```html
<script>
    /** Async Await 방식의 Ajax 요청(권장) */
    $("#btn2").on("click", async (e) => {
        e.preventDefault();

        console.log("Loading...");

        // 요청(접속)할 대상 페이지 주소 -> 이 파일의 소스코드로 읽어온다.
        const url = "http://localhost:8080/woertld.html";

        // 결과값 저장할 변수
        let response = null;

        try {
            response = await $.ajax({
                /** ajax 기본 옵션 */
                cache: false,        // 캐시 사용 금지 처리
                url: url,            // 읽어올 파일의 경로
                method: 'get',       // 통신방식 (get(기본값), post)
                data: {},            // 접속대상에게 전달할 파라미터
                dataType: 'html',    // 읽어올 내용 형식 (json(기본값), html, xml)
                timeout: 30000,      // 타임아웃 (30초)
                // async-await로 처리하더라도 콜백함수는 모두 실행됨
                beforeSend: function () {
                    console.log("callback ::: beforeSend");
                },
                success: function (req) {
                    console.log("callback ::: success");
                    console.log(req);
                },
                error: function (error) {
                    // 여기가 먼저 실행되고 catch로 넘어감
                    // -> 에러 처리를 여기서 할지, catch에서 할지는 개발자가 결정할 부분
                    console.log("callback ::: error");
                    console.error(error);
                },
                complete: function () {
                    console.log("callback ::: complete");
                }
            });
        } catch (error) {
            console.error(error);
            alert(`${error.status} Error가 발생함 - ${error.statusText}`);
            return;
        } finally {
            console.log("Finish!!!");
        }

        console.log(response);
        $("#result").append(response);
    });
    </script>
```
- 프로미스 방식과 aync-await 방식의 차이는 아래와 같다.
```js
$.ajax({
  success: function(res1) {
    $.ajax({
      success: function(res2) {
        // 또 다른 비동기...
      }
    });
  }
});

try {
  const res1 = await $.ajax(...);
  const res2 = await $.ajax(...);
  // 그 다음 순서대로 쭉~
} catch(e) {
  // 에러처리도 한 곳에서
}
```

