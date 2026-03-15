# 📌 1. Composite Pattern

#### 🔍 핵심 개념 및 주의할 점
- Composite 패턴은 여러 개의 객체를 하나의 객체처럼 다루는 구조이다.
- 트리 구조를 활용하여 폴더 내부의 모든 파일과 폴더에 대해 일괄적인 작업 수행이 가능하다.
- 삭제, 복사와 같은 명령을 하위 폴더 및 파일까지 재귀적으로 적용한다.
- iterator를 활용하여 폴더 내 파일을 탐색하고 삭제하는 방식에 주목해야 한다.
- 출력 시 들여쓰기를 사용하여 트리 구조를 시각적으로 표현한다.

#### 🧠 기억해야 할 패턴 또는 로직 흐름
- 파일과 폴더의 공통 인터페이스로 추상 클래스 `FileSystemNode`를 정의한다.
- 파일 클래스(`File`)와 폴더 클래스(`Folder`)가 공통 인터페이스를 구현한다.
- 폴더 클래스에서는 자식 노드를 리스트로 관리하며, `add()` 메서드로 하위 파일 및 폴더를 추가한다.
- 폴더 내 파일 삭제 시 `Iterator`를 사용하여 순회하며 삭제할 파일을 찾는다.
- `showDetails()` 메서드로 현재 구조를 출력할 때 재귀 호출과 들여쓰기를 활용하여 트리 형태로 출력한다.
- 삭제 명령 시, 폴더는 자식 노드를 순회하며 재귀적으로 삭제 작업을 수행한다.

### 📌 1-1. 운영체제 파일 관리 시스템
- iterator 활용과 들여쓰기를 추가하는 과정을 눈여겨 봐야한다.
```java
public class Main {
    public static void main(String[] args) {
        Folder root = new Folder("root");
            Folder Documents = new Folder("Documents");
            root.add(Documents);
                Documents.add(new File("report.docx"));
                Documents.add(new File("resume.pdf"));
        
            Folder Pictures = new Folder("Pictures");
            root.add(Pictures);
                Pictures.add(new File("vacation.png"));
                Pictures.add(new File("family.jpg"));
        
        root.showDetails(""); // 처음에 빈 문자열 넣고 시작
        System.out.println("총 파일 개수: " + root.countFiles() + "\n");
        
        Pictures.oneFileRemove("family.jpg");
        
        root.showDetails("");
        System.out.println("총 파일 개수: " + root.countFiles());
}
}

// 파일과 폴더의 정체성을 결정하는 component
abstract class FileSystemNode {
    private String name;

    public String getName() { // getter
        return name;
    }

    FileSystemNode(String name){ // 이 추상클래스를 상속받는 친구들은 모두 이름이 있어야한다.
        this.name = name;
    }

    abstract void showDetails(String indent);
    abstract int countFiles();
    abstract void copy();
    abstract void remove();
}

// 파일 클래스
class File extends FileSystemNode {

    File(String name) {
        super(name);
    }

    @Override
    void copy() {
        System.out.printf("[%s] 파일을 복사합니다.\n", getName());
    }

    @Override
    int countFiles() {
        System.out.println("파일은 내부에 속한 파일이 없습니다.");
        return 0;
    }

    @Override
    void remove() {
        System.out.printf("[%s] 파일을 삭제합니다.\n", getName());
        
    }

    @Override
    void showDetails(String indent) {
        System.out.printf("%s- 파일: %s\n", indent, getName()); // 들여쓰기 하고 getName()
    }
    
}

// 폴더 클래스
class Folder extends FileSystemNode {
    private List<FileSystemNode> children = new ArrayList<>();

    Folder(String name){
        super(name);
    }

    void add(FileSystemNode file){   // 폴더에 파일을 담는 매서드
        children.add(file);
        System.out.printf("%s 폴더에 %s 파일을 담았습니다.\n", getName(), file.getName());
    } 

    void oneFileRemove(String fileName) {
        Iterator <FileSystemNode> iterator = children.iterator(); // iterator()가 이미 객체를 만들어서 반환한다.
        while (iterator.hasNext()){ // iterator에 다음값이 있으면 반환
            FileSystemNode i = iterator.next(); // i를 iterator에서 다음값으로 지정
            if (i.getName().equals(fileName)){
                iterator.remove();
                System.out.printf("%s를 삭제하였습니다.\n\n", fileName);
                break;
            }
        }
        
    }

    @Override
    void copy() {
        System.out.printf("[%s] 폴더를 복사합니다.\n", getName());
    }

    @Override
    int countFiles() {
        return children.size();
    }

    @Override
    void remove() {
        System.out.printf("[%s] 폴더의 하위 파일을 모두 삭제합니다.\n", getName());
        children.clear();
    }

    @Override
    void showDetails(String indent) {
        System.out.printf("%s폴더: %s\n", indent, getName());
        for (FileSystemNode i : children) {
            i.showDetails(indent + "    "); // 순회하면서 들여쓰기 하나쓰고 디테일을 출력한다.
        }
    }
    
}
```