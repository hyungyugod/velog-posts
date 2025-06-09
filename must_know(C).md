# 1. <stdio.h>
### 1-1. 입출력 관련 함수 모음
- printf: 포맷에 맞게 값을 화면에 출력
- scanf: 포맷에 맞게 값을 키보드로부터 입력받음
- puts: 문자열을 한 줄(줄바꿈 포함) 출력
- putchar: 문자 1개 출력
- getchar: 문자 1개 입력
- sprintf: 문자열로 결과 저장 (출력은 안함)
- sscanf: 문자열에서 값을 추출 (입력)
- fopen: 파일 열기 (읽기/쓰기/추가 등 모드 선택)
- fclose: 파일 닫기
- fgets: 한 줄 입력 받기(문자열로 저장, 파일/키보드 모두 가능)

# 2. <stdlib.h>

### 2-1. 동적메모리 할당
- malloc(size_t size) : size 바이트만큼 메모리 할당
- calloc(size_t n, size_t size) : n개 * size 바이트, 0으로 초기화된 메모리 할당
- realloc(void *ptr, size_t size) : 기존 메모리 크기 변경
- free(void *ptr) : 할당한 메모리 해제

### 2-2. 문자열
- atoi(const char *str) : 문자열을 정수(int)로 변환
- atol(const char *str) : 문자열을 long으로 변환
- atof(const char *str) : 문자열을 실수로 변환
- strtod(const char *str, char **endptr) : 문자열을 double로 변환

### 2-3. 수학
- abs(int x): 절댓값 반환 


### 2-4. 배열
- qsort(void *base, size_t nitems, size_t size, int (*compar)(const void *, const void *)) : 배열을 빠르게 정렬
- bsearch(const void *key, const void *base, size_t nitems, size_t size, int (*compar)(const void *, const void *)) : 배열에서 이진탐색 수행

# 3. <string.h>

### 3-1. 문자열 복사(Copy) 및 덧붙이기(Concatenation)
- strcpy(dest, src): 한 문자열을 다른 문자열에 복사
- strncpy(dest, src, n): 지정한 길이만큼만 복사 (일부 복사)
- strcat(dest, src) : 문자열 끝에 다른 문자열을 이어붙이기
- strncat(dest, src, n): 지정한 길이만큼만 이어붙이기

### 3-2. 문자열 비교(Compare)
- strcmp(a, b): 두 문자열을 비교 (같으면 0)
- strncmp(a, b, n) : 앞에서 n글자까지만 비교

### 3-3. 문자열 길이 측정 
- \0(널 문자) 전까지의 글자 수만 센다.
- strlen(str) : 문자열의 길이(문자 개수) 반환

### 3-4. 문자/문자열 탐색(Search)
- strchr(str, 'a') : 문자열에서 특정 문자 첫 번째 위치 찾기
- strrchr(str, 'a') : 문자열에서 특정 문자 마지막 위치 찾기
- strstr(str, "abc") : 문자열에서 다른 문자열의 첫 위치 찾기
- strpbrk(str, "abc") : 어떤 문자가 여러 개 있을 때, 그 중 첫 위치 찾기
- strspn(str, "abc") : 첫 부분에 지정한 문자만 몇 개나 연속되는지 반환
- strcspn(str, "xyz") : 지정한 문자가 처음 나오는 위치 반환

### 3-5. 문자열 토큰 분리
- 문자열을 "공백", "쉼표" 등 구분자 기준으로 여러 부분으로 나눌 때 사용
- strtok(str, " ,."): 문자열을 구분자(delimiter)로 쪼개기

### 3-6. 메모리 조작(Memory Operation) 함수
- 문자열 뿐만 아니라, 배열이나 구조체 등 일반적인 메모리 블록에도 사용
- memcpy(dest, src, n): 메모리의 특정 구간을 복사
- memmove(dest, src, n): 겹치는 영역도 안전하게 복사
- memset(arr, 0, n): 메모리의 모든 바이트를 특정 값으로 채우기
- memcmp(a, b, n): 메모리 블록을 비교

# 4. <math.h>

### 4-1. 거듭제곱, 제곱근, 제곱
- pow(x, y): x의 y승(거듭제곱) 계산
- sqrt(x): x의 제곱근(루트) 계산
- cbrt(x): x의 세제곱근 계산

### 4-2. 절댓값, 부호, 나머지
- fabs(x): x의 절댓값(실수 전용)
- fmod(x, y): x를 y로 나눈 나머지
- copysign(x, y): x의 절댓값에 y의 부호를 붙임

### 4-3. 반올림, 올림, 내림
- floor(x): x보다 크지 않은 최대 정수(내림)
- ceil(x): x보다 크거나 같은 최소 정수(올림)
- round(x): 가장 가까운 정수로 반올림
- trunc(x): 소수점 이하를 버림(정수 쪽으로)
- 