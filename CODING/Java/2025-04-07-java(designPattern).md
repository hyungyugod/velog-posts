### 📌 1. Facade Pattern - 스마트 홈기기 제어 시스템

#### 🔍 핵심 개념 및 주의할 점
- 복잡한 여러 기기의 동작을 하나의 인터페이스로 간단히 제어할 수 있도록 구현한다.
- 파사드 패턴은 메서드 실행을 하나로 묶어 편리성을 높이는 데 집중한다.
- 팩토리 패턴이 객체 생성을 자동화하는 반면, 파사드 패턴은 복잡한 기능을 일괄 실행하는 데 사용한다.

#### 🧠 기억해야 할 패턴 또는 로직 흐름
- 추상 클래스(SmartDevice)를 통해 공통 기능 인터페이스를 정의한다.
- 각 기기 클래스(Light, AirConditioner, SecuritySystem)에서 구체적인 동작을 구현한다.
- SmartHomeFacade 클래스에서 기기들을 리스트로 관리하며, 상황(awayMode, homeMode)에 맞춰 일괄적으로 동작을 제어한다.

#### 💻 코드 (Java)
```java
public class Main {
    public static void main(String[] args) {
    SmartHomeFacade smartHomeFacade = new SmartHomeFacade();
        smartHomeFacade.inputDevice(new Light());
        smartHomeFacade.inputDevice(new AirConditioner());
        smartHomeFacade.inputDevice(new SecuritySystem());

        smartHomeFacade.awayMode();
        smartHomeFacade.homeMode();
}
}

// 정체성을 정의하는 추상클래스
abstract class SmartDevice {
    abstract void turnOn();
    abstract void turnOff();
}

// 각자 기기의 클래스
class Light extends SmartDevice{
    public void turnOn(){
        System.out.println("조명이 켜졌습니다.");
    }

    public void turnOff(){
        System.out.println("조명이 꺼졌습니다.");
    }
}

class AirConditioner extends SmartDevice{
    public void turnOn(){
        System.out.println("에어컨이 켜졌습니다.");
    }

    public void turnOff(){
        System.out.println("에어컨이 꺼졌습니다.");
    }
}

class SecuritySystem extends SmartDevice{
    public void turnOn(){
        System.out.println("보안 시스템이 활성화되었습니다.");
    }

    public void turnOff(){
        System.out.println("보안 시스템이 비활성화되었습니다.");
    }
}

// 파사드 클래스
class SmartHomeFacade {
    private List <SmartDevice> list = new ArrayList<>();

    public SmartHomeFacade() {}

    public void inputDevice(SmartDevice smartDevice){
        list.add(smartDevice);
    }

    public void awayMode() {
        System.out.println("외출모드 실행");
        for (SmartDevice i : list){
            if (i instanceof SecuritySystem){
                i.turnOn();
            }
            else {
                i.turnOff();
            }
        }
    }

    public void homeMode() {
        System.out.println("홈 모드 실행");
        for (SmartDevice i : list){
            if (i instanceof SecuritySystem){
                i.turnOff();
            }
            else {
                i.turnOn();
            }
        }
    }
}
