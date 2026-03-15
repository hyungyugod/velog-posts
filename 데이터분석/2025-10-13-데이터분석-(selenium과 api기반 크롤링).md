# 📌 1. selenium 동적 크롤링 
### 1-1. 세팅과 테스트
- 아나콘다 내의 주피터 환경에서 진행하는 것이 좋다.
- from selenium.webdriver.common.by import By는 Selenium에서 엘리먼트를 찾을 때 사용하는 방법을 제공하는 클래스이다.
- ID, 클래스 이름, 태그 이름, CSS 셀렉터 등을 BY.으로 지정하여 사용할 수 있다.
```py
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

import time

url = "http://www.naver.com"
driver = webdriver.Chrome()
driver.get(url)
```

### 1-2. 기본 명령
- current_url는 가장 앞에있는 브라우저의 주소 즉 부모의 주소를 반환한다.
- driver.back()는 현재 브라우저에서 뒤로 이동한다.
- driver.forward()는 앞으로 이동한다.
- driver.refresh()는 브라우저를 새로고침한다.
- driver.close()는 현재 브라우저를 닫는다.
- driver.quit()는 모든 브라우저를 닫는다.
```py
driver.current_url
driver.back()
driver.forward()
driver.refresh()
driver.close()
driver.quit()
```

### 1-3. 브라우저에서 검색해보기
- 아래와 같이 할당하면 search는 이제 WebElement 객체가 된다.
- send_keys()는 해당 요소에 키보드 입력을 시뮬레이션하는 메서드이다.
- submit() 메서드는 현재 요소를 폼 제출을 트리거하는 역할을 한다.
```py
search = driver.find_element(By.ID, 'query')
search.send_keys('내일 날씨')
search.submit()
```

### 1-4. 버거킹 동적 크롤링
```py
url = "https://www.burgerking.co.kr/#/home"
# driver = webdriver.Chrome('chromedriver.exe')
driver = webdriver.Chrome()
driver.get(url)
```
```py
# html 소스 가져오기
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
bgk_addrs = soup.find_all("p", class_="txt_addr")

lst_bgk = [i.text.split(" ")[1] for i in bgk_addrs]
len(lst_bgk)

df_bgk = pd.DataFrame({"버거킹위치(구정보)":lst_bgk}).reset_index() # 위치를 기준으로 group by 했을 때 개수를 셀 컬럼이 필요하여서 index를 내린다.

pd.pivot_table(
    df_bgk,
    index = '버거킹위치(구정보)',
    values = 'index',
    aggfunc = 'count'
).sort_values(by='index')
```

### 1-5. 맥도날드 동적 크롤링
- 브라우저를 열고 페이지 버튼을 클릭하면서 정보를 긁어온다. 이때 광클이 발생하지 않도록 중간중간에 기다려주는 것이 중요하다.
- element_to_be_clickable: element_to_be_clickable는 "요소가 클릭 가능한 상태가 될 때까지 기다리는" 조건이다. 요소가 DOM(문서 객체 모델)에 존재하는지와 요소가 화면에서 클릭할 수 있는 상태인지 (즉, 숨겨지지 않고, 비활성화되지 않음) 확인한다.
- until() 메서드는 지정한 조건이 충족될 때까지 대기하게 한다.
- WebDriverWait(driver, 10): driver객체가 최대 10초까지 기다릴 수 있도록 한다.
```py
# fake 브라우저 실행
url = "https://www.mcdonalds.co.kr/kor/store/main"
driver = webdriver.Chrome()
driver.get(url)

page_no = 11
lst_mac = []

for page in range(1, page_no + 1):
    # 페이지 번호 계산
    if page % 5 == 0:
        p = 5
    else:
        p = page % 5  # 페이지 번호에 맞는 버튼 클릭 (1부터 5까지 순차적으로)

    # 페이지 번호 버튼 클릭
    xpath = f"""//*[@id="container"]/section/div[4]/ul/li[{p}]/button"""
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    ).click()
    
    # 페이지가 로드될 때까지 기다리기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "mb-1"))
    )
    
    # 페이지 확인 및 HTML 입수
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # p 태그에서 주소 추출
    mac_addrs = soup.find_all("p", class_="mb-1 text-15 text-gray-text")
    
    for i in mac_addrs:
        # 주소 추출 방식 (split 사용 시 문제가 있을 수 있음)
        text = i.text.strip()  # 텍스트 앞뒤 공백 제거
        if len(text.split()) > 1:  # split()으로 주소가 제대로 나오는지 확인
            lst_mac.append(text.split()[1])  # 주소 추출
    
    # 5 페이지마다 다음 페이지 버튼 클릭
    if page % 5 == 0:
        next_xpath = """//*[@id="container"]/section/div[4]/ul/li[1]/button"""
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, next_xpath))
        ).click()
        time.sleep(1)

# 결과 출력
print(lst_mac)

# 드라이버 종료
driver.quit()
```

# 📌 2. API 기반 자료수집
### 2-1. 네이버 블로그 검색 api
- 검색과 결과에 대한 정보를 바로 활용할 수 있도록 api를 제공한다는것이 흥미롭다.
- 해당 open api 주소에 쿼리스트링으로 검색할 값을 주소에 붙이고 발급받은 키값을 헤더에 실어서 해당 주소로 get요청을 보내면 해당 검색결과에 맞는 정보들을 json으로 반환해준다.
```py
import requests    # URL 정보를 통해 웹 사이트 HTML 입수
from bs4 import BeautifulSoup # HTML 을 parsing 구조화

import pandas as pd
import time

client_id = "발급받은 아이디"
client_secret = "발급받은 시크릿키"

headers = {
    "X-Naver-Client-Id" : client_id,
    "X-Naver-Client-Secret" : client_secret
}

url = "https://openapi.naver.com/v1/search/blog?query="
keyword = "강남역 맛집"
url_blog = url + keyword

req = requests.get(url_blog, headers=headers)
result = req.json()

result['items']
```
- 위의 로직을 함수로 만들어 사용하면 아래와 같다.
```py
def nblog_search(keyword):
    client_id = "VHjMRxxw_mn9rIFMNKtb"
    client_secret = "BXIG_1Eev7"

    headers = {
        "X-Naver-Client-Id" : client_id,
        "X-Naver-Client-Secret" : client_secret
    }   

  url = "https://openapi.naver.com/v1/search/blog?query="
  url_blog = url + keyword
  req = requests.get(url_blog, headers=headers)
  return req.json()['items']
```