# 너비 우선 탐색(breadth first search:BFS)
## 1. 그래프에 대하여
- 그래프는 우리가 흔히 최단 경로 문제에서 보던 정점(node)과 간선(edge)으로 이루어진 도식을 의미한다.
- 정점으로 들어가는 간선의 방향에 따라 들어오는 이웃과 나가는 이웃이 있다. 
  
## 2. 너비 우선 탐색
- 뻗은 그래프에서 1촌부터 전부 탐색하고 이후에 2촌들을 탐색한다. 
- 1촌을 조사하여 만약 추가할 대상이 있다면 우선 후순위로 두고 1촌을 다 돈 후에 탐색하는 것이다.
- A에서 B로 가는 경로가 있는지지 알려줌
- 순회알고리즘: 너비 우선 탐색은 순회 알고리즘으로 모든 정점을 방문한다.

### 큐(queue)
- 너비 우선 탐색은 큐를 통해 이해한다. 큐는 흔히 말하는 대기열로 먼저 들어온 사람이 먼저 나간다. FIFO이다.
- 게임에서 먼저 큐를 잡으면 먼저 게임을 잡을 수 있는 것과 같다. 반대로 스택은 먼저 들어온게 먼저 나가는 LIFO이다.
  
## 3. 그래프의 구현
- 그래프를 해시 테이블로 구현하면 아래와 같다.
```python
graph = {}
graph["you"] = ["alice","bob","claire"]
```
- 그래프에는 방향을 가지는 방향 그래프와 방향을 가지지 않는 무방향 그래프가 있다.
- 너비 우선 탐색을 코드로 구현하면 아래와 같다.
```python
def search(name):
    search_queue = deque()                              # 탐색할 노드를 저장할 double-ended queue를 의미한다. 
                                                        # (정의해두면 양방양에서 모두 요소제거가 가능하다.)
    search_queue += graph[name]                         # 특정 사람으로부터 뻗어나가는 그래프를 큐에 저장한다.
    searched = set()                                    # 이미 탐색한 사람을 두번 탐색하지 않기 위해 사용한다.
    while search_queue:
        person = search_queue.popleft()                 # 제일 앞에 있는 사람을 꺼냄(선입선출)
        if not person in searched:                      # 아직 확인하지 않은 사람만 확인한다.
            if person_is_seller(person):               
                print (person + " is a mango seller!")
                return True

        else:
            search_queue += graph[person]               # 찾는 사람이 아니면 그 사람의 그래프를 대기열에 추가한다.
            searched.add(person)                        # 조사한 사람 목록에 그 사람을 추가한다.
    return False

search("you")
```
## 4. 실행시간
- 보통 O(V+E) 정점의 수 + 간선의 수로 표기한다.

# 트리
## 1. 루트가 있는 트리
- 이 책에선 우선 루트가 있는 트리를 다룬다. 루트란 다른 모든 정점으로 이어지는 하나의 정점인 루트를 포함하고 있다는 뜻이다.(루트 = 뿌리)
- 리프정점(leaf node): 모든 정점은 자식과 부모를 자질 수 있는데 자식이 없는 마지막 정점을 리프정점이리고 한다. (잎사귀)
- 파일 디렉터리: 모두가 매일 다루는 트리이다. 파일 디렉터리를 너비우선 탐색하면 우선 내부 파일은 제쳐두고 모든 폴더 부터 일단 다 열어본다.
- 트리는 연결된 비순환 그래프이다.

### 파일 디렉터리 코드로 구현
- 이 파일 디렉터리는 트리로 구성되어 있으므로 앞에서처럼 중복을 굳이 제거할 필요가 없다.
```python
from os import listdir                              # 디렉터리의 파일과 폴더의 목록을 리스트로 반환한다.
from os.path import isfile, join                    # join은 여러개의 디렉터리와 파일을 연결해준다. (구분자(/ 또는 \)를 자동으로 적용)
from collections import deque                       # 양방향 큐를 가져온다.

def printnames(start_dir):
    search_queue = deque 
    search_queue.append(start_dir)
    while search_queue:
        dir = search_queue.popleft()
        for file in sorted(lustdir(dir)):
            fullpath = join(dir,file)               # 디렉토리의 첫번째 파일의 전체경로를 생성하여 파일이면 출력하고 아니면 전체 경로 대기열에 추가한다.
            if isfile(fullpath):
                print(file)
            else:
                search_queue.append(fullpath)

printnames("pics")
```
- 심볼릭 링크는 사이클을 의도적으로 만들어 트리 내에서도 순환구조를 만들 수 있다.

## 2. 깊이 우선 탐색(depth-first-search:DFS)
- 재귀적인 방법으로 파일 디렉터리를 순회한다. 파일을 발견하면 끝까지 파고들어간다.4
```python
from os import listdir                             
from os.path import isfile, join 

def printnames(dir):
    for file in sorted(listdir(dir)):
        fullpath = join(dir, file)
        if isfile(fullpath):
            print(file)
        else:
            printnames(fullpath)          # 파일이 아니면 방금 연 이 폴더를 대상으로 이 함수를 반복한다.
printnames("pics")
```

## 3. 이진트리(binary tree)
- 한 정점에 왼쪽자식과 오른쪽 자식이 하나씩 있는 트리
- 왼쪽 하위 트리와 오른쪽 하위 트리라고도 한다.

## 4. 허프만 코딩
- 이진트리를 사용한 텍스트 압축 알고리즘의 기초
- 8비트 = 1바이트, 비트는 0또는 1인 숫자를 의미
- 유니코드: 모든 언어를 인코딩 하는 것을 목표로함. (인코딩 - 언어를 이진수로 표현하는 방법)(utf-8이 가장 대중적적)
- 가장 자주 등장하는 문자에는 짧은 코드를, 덜 자주 등장하는 문자에는 긴 코드를 할당하여 데이터를 효율적으로 압축하는 방식이다.
- 가장 적게 등장하는 노드들을 모아 트리를 만들기 시작하여 쌓아나간다.
- 왼쪽은 0, 오른쪽은 1을 할당하여 위에서부터 아래로 내려가며 비트를 부여한다.
- 허프만 코딩은 문자가 리프 정점에만 있는데 끝이 꼭 두갈래로 끝나는 건 아니어서 차등을 둘 수 있다.

# 균형트리
## 1. 균형잡기 (이진탐색트리 BST:binary search tree)
- 이진 트리와 같으나 왼쪽은 자식은 부모보다 작고 오른쪽 자식은 부모보다 크다는 특징이 있다.
- 트리의 높이가 낮아질수록 탐색 속도가 빠르다.

## 2. AVL 트리 (Adelson-Velsky and Landis)
- 일종의 자가 균형 BST 트리이다.
- 균형을 맞추기 위해 특정 높이가 되면 일자 트리가 회전하여 삼각대 형식의 트리가 된다.
- 트리는 균형인숭 맞춰 회전하는데 왼쪽 자식이 높으면 -1 오른쪽이면 1 균형이면 0이 노드에 할당된다.
- 높이가 몇층 높은지에 따라 절댓값이 커진다. h: 높이와, bf: 균형인수가 각 정점에 할당된다.
- 이는 높이가 log n이 되도록 보장한다. 이진 탐색과 같은 형식의 구조를 보장하므로..
- 삽입은 정점 위치를 탐색하고 포인터만 추가하면 돼서 O(1)의 시간이 걸린다.

## 3. 스플레이 트리
- 균형트리(BST)의 다른 버전으로 최근에 조회한 항목이 있으면 속도가 빨라진다.
- 일반적으로 최근에 검색한 정점이 맨위에 다시 모인다.

## 4. B 트리
- 이진 트리의 일반화 형태로 주로 데이터 베이스를 만들때 쓰인다.
- 자식을 두개 이상 가질 수 있고 키값도 두개씩 가지고 있을 수 있다.
- 디스크가 움직이는 시간(탐색시간)을 단축한다.
- 이진 트리보다 많은 자식을 가져 크기가 크고 한번에 여러 정보를 메모리에 저장한다.
- 이또한 BST의 특징을 여전히 따른다.

