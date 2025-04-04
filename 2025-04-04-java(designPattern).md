# 1.Decorator Pattern
- 데코레이터는 생성자에서 "이전 객체(케이크일때)"를 받아서, 자신의 기능(크림, 초코칩 등)을 추가한다.

### 📌 1-1. 런타임 기능 변환에 대하여
- 기본적으로는 런타임에 기능을 변경할 수 없다. 컴파일 당시에 모든 클래스에 대한 정보와 계획을 알고 있다.
- 다만 객체가 실제로 생성되는 것은 '무조건' 런타임이기 때문에 이를 이용하여 런타임에 기능을 변경할 수 있다.
- **"실행 시점의 객체 간 협력(협력 관계)"**: 런타임에 객체가 new로 생성되면서, '딱딱딱' 연결되는 것
```java
public class Main {
    public static void main(String[] args) {
        Dog dog = new Dog(); // ← 여기서 객체가 "런타임"에 생성됨
        dog.bark();
    }
}
```
- 여기서 new Dog()가 실행되는 시점은 코드가 실행되는 순간, 즉 런타임이며 컴파일할 때는 단지 "Dog 클래스를 new로 만들겠구나" 라는 지시를 남겨두고 코드가 말이되는지만 판단할 뿐이다.
- 만약 static 필드에 new가 있어도 컴파일 시에는 그 명령만 프로그램에 올려둘 뿐 객체가 생성되어서 다른 클래스들에 영향을 주는 것은 아니다.

### 📌 1-2. 데코레이터 패턴이 필요한 이유
- 기능을 추가하는 일반적인 방법인 상속은 컴파일 시에 기능이 다 정해져 있는거라 런타임에 기능을 바꿀 수 없어 딱딱하다.
- 객체를 활용하여 기능을 추가하는 방식이므로 기본타입에 동적으로 기능을 추가할 수 있게된다. 

### 📌 1-3. 커피 주문 시스템

#### 🔍 핵심 개념 및 주의할 점
- 새로운 옵션을 추가할 때 기존 코드를 수정하지 않고 새로 추가되는 종류(아래에선 토핑의 종류) 클래스를 추가하여 확장한다 (OCP 원칙 준수- 확장에는 열려있고 수정에는 닫혀있다.).
- Coffee 인터페이스를 기반으로 기본 컴포넌트와 데코레이터들이 일관된 구조로 구현된다.

#### 🧠 기억해야 할 패턴 또는 로직 흐름
- Coffee 인터페이스 선언 → 기본 커피 클래스 구현
- 옵션 클래스는 CoffeeDecorator 추상 클래스를 상속하고, 기존 커피 객체를 조합한다
- getCost(), getDescription() 메서드를 통해 재귀적으로 가격과 설명을 누적한다

```java
public class Main {
    public static void main(String[] args) {
    printOrder(new Milk(new BasicCoffee()));
    printOrder(new WhippedCream(new BasicCoffee()));
    printOrder(new Syrup(new BasicCoffee()));
    printOrder(new Milk(new Milk(new BasicCoffee())));
}

private static void printOrder(Coffee coffee) {
    System.out.println("주문한 메뉴: " + coffee.getDescription());
    System.out.println("가격: " + coffee.getCost() + "원\n");
}
}

// Component(요소-클래스)
interface Coffee {
    String getDescription();
    int getCost();
}

// Concrete Component (component를 구체화한 실체 클래스)
class BasicCoffee implements Coffee{
    @Override
    public int getCost() {
        return 3000;
    }

    @Override
    public String getDescription() {
        return "기본 커피";
    }
    
}

// 옵션 추가를 위한 추상 클래스 (Component라는 큰 틀은 유지)- 기존 객체를 입력받는 기능을 만들어둠.
abstract class CoffeeDecorator implements Coffee {
    protected Coffee originalCoffee; // 패키지 밖에서도 자식은 호출할 수 있게 프로텍티드

    public CoffeeDecorator(Coffee originalCoffee) {
        this.originalCoffee = originalCoffee;
    }
}

// 옵션 추가를 위한 구체적인 데코레이터 클래스를
class Milk extends CoffeeDecorator {
    public Milk(Coffee originalCoffee) {
        super(originalCoffee);
    }

    @Override
    public int getCost() {
        return originalCoffee.getCost() + 500;
    }

    @Override
    public String getDescription() {
        return originalCoffee.getDescription() + "+ 우유";
    }
}

class WhippedCream extends CoffeeDecorator {
    public WhippedCream(Coffee originalCoffee) {
        super(originalCoffee);
    }

    @Override
    public int getCost() {
        return originalCoffee.getCost() + 700;
    }

    @Override
    public String getDescription() {
        return originalCoffee.getDescription() + " + 휘핑크림";
    }
}

class Syrup extends CoffeeDecorator {
    public Syrup(Coffee originalCoffee) {
        super(originalCoffee);
    }

    @Override
    public int getCost() {
        return originalCoffee.getCost() + 400;
    }

    @Override
    public String getDescription() {
        return originalCoffee.getDescription() + " + 시럽";
    }
}
```

### 📌 1-4. 케릭터 스킬 업그레이드 시스템

#### 🔍 핵심 개념 및 주의할 점
- 데코레이터 패턴을 사용하여 캐릭터의 스킬을 동적으로 조합
- 스킬별 적용 횟수를 `Map`으로 관리하여 중복 스킬 적용이 가능하도록 설계
- 입력된 스킬 횟수만큼 반복하여 데코레이터를 중첩 적용하여 최종 캐릭터를 완성

#### 🧠 기억해야 할 패턴 또는 로직 흐름
- `Map<String, Integer>` 초기화 → 스킬 이름과 적용 횟수 저장
- 스킬 박스에 스킬 추가 → `skillBox` 메서드로 스킬별 누적 관리
- 최종 캐릭터 생성 → `charaterfac` 메서드(팩토리 메서드)에서 Map 순회하며 데코레이터 패턴 적용
- 최종 캐릭터 출력 → 이름, 설명, 공격력 출력
- 
```java
public class Main {
    public static void main(String[] args) {
    Scanner reader = new Scanner(System.in);
    System.out.print("케릭터 이름을 입력하세요: ");
    String name = reader.nextLine();
    Map<String, Integer> box = new HashMap<>();

    System.out.printf("케릭터 이름: %s\n", name);
    box = skillBox(box, 3, "fire");
    box = skillBox(box, 3, "defence");
    box = skillBox(box, 4, "speed");

    printSkillCounts(box); // 스킬별 적용 횟수 출력

    Character c= charaterfac(box);

    System.out.printf("캐릭터 이름: %s\n\n 최종 케릭터: %s\n최종 공격력: %d", name, c.getDescription(), c.getPower());
    
}


// 스킬 카운트 출력
public static void printSkillCounts(Map<String, Integer> box) {
    System.out.println("\n스킬별 적용 횟수:");
    for (Map.Entry<String, Integer> entry : box.entrySet()) {
        System.out.println(entry.getKey() + ": " + entry.getValue() + "회");
    }
}

public static Map <String, Integer> skillBox(Map <String, Integer> box, int x, String skill){
            box.put(skill, box.getOrDefault(skill, 0) + x);
    return box;
}

public static Character charaterfac(Map <String, Integer> box){ //스킬들을 담아서 케릭터를 만드는 메서드
    Character bc = new BasicCaracter();

    for (Map.Entry<String, Integer> entry : box.entrySet()){ // Map.Entry (키,벨류)를 Set으로 가져옴.
        for (int i = 0; i < entry.getValue(); i++) { 
            switch (entry.getKey()) {
                case "fire":
                    bc = new FireSkill(bc);
                    break;

                    case "defence":
                    bc = new DefenseSkill(bc);
                    break;

                    case "speed":
                    bc = new SpeedSkill(bc);
                    break;
            }
    }
    
}
return bc;
}

}


// Component
interface Character {
    String getDescription();
    int getPower();
}

// Concrete Component
class BasicCaracter implements Character {
    private String name;


    @Override
    public String getDescription() {
        return "기본 전사";
    }

    @Override
    public int getPower() {
        return 10;
    }
}

// 옵션 추가를 위한 추상 클래스 -> 추상클래스는 인터페이스를 구현할때 오버라이드 책임을 자식 클래스로 넘길 수 있다.
// + 추상클래스라고 굳이 추상 메서드를 정의하지 않아도 된다.
abstract class SkillBuilder implements Character {
    protected Character originalCharacter;

    public SkillBuilder(Character originalCharacter) {
        this.originalCharacter = originalCharacter;
    }
}
// 옵션 추가를 위한 구체적인 데코레이터 클래스를
class FireSkill extends SkillBuilder {
    public FireSkill(Character originalCharacter) {
        super(originalCharacter);
    }

    @Override
    public String getDescription() {
        return originalCharacter.getDescription() + " + 불 속성 공격";
    }

    @Override
    public int getPower() {
        return originalCharacter.getPower() + 10;
    }
    
}
class DefenseSkill extends SkillBuilder {
    public DefenseSkill(Character originalCharacter) {
        super(originalCharacter);
    }

    @Override
    public String getDescription() {
        return originalCharacter.getDescription() + " + 방어력 강화";
    }

    @Override
    public int getPower() {
        return originalCharacter.getPower() + 10;
    }
}
class SpeedSkill extends SkillBuilder {
    public SpeedSkill(Character originalCharacter) {
        super(originalCharacter);
    }

    @Override
    public String getDescription() {
        return originalCharacter.getDescription() + " + 속도 증가";
    }

    @Override
    public int getPower() {
        return originalCharacter.getPower() + 15;
    }
}
```