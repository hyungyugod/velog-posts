# 📌 1. Bridge Pattern
- 한 클래스를 (기능 계층)과 (구현 계층)으로 분리하여, 서로 독립적으로 확장 가능하도록함.
- 구현 계층은 기능 계층을 사용 (has-A) 해야 한다. 
- 즉 구현체는 기능을 스스로 정의하지 않고 기능 계층과 합쳐져서 기능을 구현하는 것이다.

---

### 📌 1-1. 참고 (다이어그램 화살표 의미)
| **기호** | **의미**                      | **예시**                |
|----------|-------------------------------|-------------------------|
| ◇        | 집합 관계 (Aggregation)        | 학교 ◇──▶ 학생          |
| ▶        | 포함 방향                     | 포함하는 쪽 → 포함되는 쪽 |
| "포함"   | 관계 설명 (텍스트 라벨)        | "학교는 학생을 포함한다" |

---

### 📌 1-2. 스마트 가전 리모컨 시스템
- 브릿지 패턴을 사용하여 리모컨 기능과 해당 장치를 분리하였다.
- has-A 관계로 기능이 장치를 넣을 수 있도록 하여 동적으로 조합을 변경할 수 있도록 하였다.
- 아래 예시에서는 다양한 제품들은 기본적인 기능이 필요하다고 인터페이스에 정의만 해두고 각자의 특성으로 분기된다.
- 구체적 조작은 RemoteControl 객체에 제품을 연동하여 최종 기능을 구현한다.

```java
public class Main {
    public static void main(String[] args) {
        BasicRemote b1 = new BasicRemote(new SamsungTV());
        b1.powerOn();
        b1.powerOff();
        b1.volumeUp();
        b1.volumeDown();

        AdvancedRemote a1 = new AdvancedRemote(new LgAirConditioner());
        a1.powerOn();
        a1.powerOff();
        a1.volumeUp();
        a1.volumeDown();
        a1.mute();
}
}

// 구현 계체
interface Device {
    void turnOn();
    void turnOff();
    void volumeUp();
    void volumeDown();
    int getVolume(); // getter도 필요하면 인터페이스에서 만들어둬야한다.
}

// 구상 구현 -> 플렛폼 별 맞춤형 코드
class SamsungTV implements Device {
    private int volume = 50;

    public int getVolume() {
        return volume;
    }

    @Override
    public void turnOff() {
        System.out.println("삼성 tv의 전원을 끕니다.");
    }

    @Override
    public void turnOn() {
        System.out.println("삼성 tv의 전원을 켭니다.");
    }

    @Override
    public void volumeDown() {
        volume += 5;
        System.out.printf("삼성 tv의 볼륨을 %d로 증가시킵니다.\n", volume);
    }

    @Override
    public void volumeUp() {
        volume = Math.max(0, volume - 5); // 최소 0까지 -> 이런식으로 볼륨의 최솟값을 명시해줄 수 있다.
        System.out.printf("삼성 tv의 볼륨을 %d로 감소시킵니다.\n", volume);
    }
    
}
class LgAirConditioner implements Device {
    private int volume = 50;

    public int getVolume() {
        return volume;
    }

    @Override
    public void turnOff() {
        System.out.println("LG 공기 청정기의 전원을 끕니다.");
    }

    @Override
    public void turnOn() {
        System.out.println("LG 공기 청정기의 전원을 켭니다.");
    }

    @Override
    public void volumeDown() {
        volume = Math.max(0, volume - 10); // 최소 0까지 -> 이런식으로 볼륨의 최솟값을 명시해줄 수 있다.
        System.out.printf("LG 공기 청정기의 볼륨을 %d로 감소시킵니다.\n", volume);
    }

    @Override
    public void volumeUp() {
        volume += 10;
        System.out.printf("LG 공기 청정기의 볼륨을 %d로 증가시킵니다.\n", volume);
    }
    
}
class PhilipsLight  implements Device {
    private int volume = 50;

    public int getVolume() {
        return volume;
    }

    @Override
    public void turnOff() {
        System.out.println("필립스 전등의 전원을 끕니다.");
    }

    @Override
    public void turnOn() {
        System.out.println("필립스 전등의 전원을 켭니다.");
    }

    @Override
    public void volumeDown() {
        volume = Math.max(0, volume - 15); // 최소 0까지 -> 이런식으로 볼륨의 최솟값을 명시해줄 수 있다.
        System.out.printf("필립스 전등의 볼륨을 %d로 감소시킵니다.\n", volume);
    }

    @Override
    public void volumeUp() {
        volume += 15;
        System.out.printf("필립스 전등의 볼륨을 %d로 증가시킵니다.\n", volume);
    }
}

// 추상화 (기능 개체) -> 리모트 컨트롤 기능의 기본을 정의함.
abstract class RemoteControl {
    private Device device; // 기본적인 기능을 갖춘 기기를 속성으로 갖고 상위 기능을 구현한다.

    public RemoteControl(Device device){
        this.device = device;
    }

    public void powerOn() { // 연결된 구현체의 기본 기능 구현
        device.turnOn();
    }

    public void powerOff() {
        device.turnOff();
    }

    public void volumeUp(){  //  연결된 구현체의 특정 메서드를 구체화함.
        device.volumeUp(); // 볼륨을 각 구현체에서 구현된 매서드를 통해 내린다.
    }

    public void volumeDown(){
        device.volumeDown(); // 볼륨을 각 구현체에서 구현된 매서드를 통해 올린다.
    }

    public Device getDevice() { // getter 생성
        return device;
    }

    
}

// 기능 개체의 여러 버전 추상화를 상속받아서 기능에 변화를 준다.
class BasicRemote extends RemoteControl {
    
    public BasicRemote(Device device){ // 기본 기능만 가지고 있는 basic 리모컨
        super(device);
    }

}
class AdvancedRemote  extends RemoteControl {
    
    public AdvancedRemote(Device device){ // 기본 기능만 가지고 있는 basic 리모컨
        super(device);
    }

    public void mute(){
        while (getDevice().getVolume() > 0) {
            getDevice().volumeDown();
        }
        System.out.println("음소거 되었습니다.");
    }
}
```

---
