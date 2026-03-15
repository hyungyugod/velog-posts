# 📌 1. 자바 스크립트 코딩테스트
- 장염이슈로,, 한문제만
### 📌  1-1. 뒤에서 5등 위로
- sort가 문자열 정렬이라 정수 배열의 정확한 조건을 걸어주는 것이 좋다.
```js
function solution(num_list) {
    num_list = num_list.sort((a, b) => a - b);
    return num_list.slice(5, num_list.length); 
}
```