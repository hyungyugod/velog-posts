# 1. 팩토리 매서드 패턴
- 객체를 대신 생성해주는 공장 -> 객체 만드는 사람을 고용해서 만드는 일을 덜어내고 큰 일에서 머리를 적게 쓰기 위해
### 📌 1-1. 알림 메시지 생성 시스템 만들기 (Simple Factory Pattern)

#### 🔍 핵심 개념 및 주의할 점
- 객체 생성을 별도의 Factory 클래스에서 담당하도록 하여 클라이언트 코드의 의존성을 줄인다.
- 클라이언트는 객체 생성 방식에 대해 알 필요 없이 타입만 전달하면 된다.
- 조건 분기를 통해 객체를 생성하므로, 새로운 타입이 추가될 경우 `Factory` 수정이 필요하다 (Open-Closed Principle 위배 가능성 있음).

#### 🧠 기억해야 할 패턴 또는 로직 흐름
- Notification 인터페이스 정의 → 공통 행동 `send()` 메서드 선언
- 각 알림 타입 클래스 (`EmailNotification`, `SMSNotification`, `PushNotification`)에서 인터페이스 구현
- Factory 클래스에서 `type` 문자열에 따라 각 객체 생성 및 반환
- 클라이언트(`Main`)는 `Factory`만 사용하여 알림 객체 생성 후 `send()` 호출

#### 💻 정답 코드 (Java)
```java
public class Main {
    public static void main(String[] args) {
        NotificationFactory factory = new NotificationFactory();

        factory.createNotification("email").send("hyungyugod@naver.com", "반갑습니다. 현규씨");
        factory.createNotification("push").send("sunghyungyu", "안녕하세요. 현규씨");
    }
}

interface Notification {
    void send(String to, String message);
}


class EmailNotification implements Notification{
    public void send(String to, String message){
        System.out.printf("%s에게 이메일을 전송합니다: %s\n", to, message);
    }
}

class SMSNotification implements Notification{
    public void send(String to, String message){
        System.out.printf("%s에게 문자 메세지를 전송합니다: %s\n", to, message);
    }
}

class PushNotification implements Notification{
    public void send(String to, String message){
        System.out.printf("%s에게 푸시 알림을 전송합니다: %s\n", to, message);
    }
}

class NotificationFactory{   // 팩토리가 객체 리턴을 대리한다.
    Notification createNotification(String type){
        if (type.equalsIgnoreCase("email")){
            return new EmailNotification();
        }

        else if (type.equalsIgnoreCase("sms")){
            return new SMSNotification();
        }

        else if (type.equalsIgnoreCase("push")) {
            return new PushNotification();
        }

        else {
            return null;  // 딱히 리턴할 거 없을때는 null을 리턴
        }
    }

}
```

#### 📌 1-1-2. Simple Factory Pattern 개선 버전

##### 🔍 핵심 개념 및 주의할 점
- `HashMap`과 `Supplier`를 활용해 객체 생성 로직을 동적으로 등록 및 확장할 수 있도록 개선하였다.
- 클라이언트는 단순히 타입명만 등록하고 사용하며, OCP(Open-Closed Principle)를 만족시킨다.
- `Supplier<T>`를 통해 생성자 참조 방식으로 객체 공급이 가능하며, 필요 시 `get()`을 통해 실제 인스턴스를 반환한다.
- 예외 처리는 사용자 정의 `RuntimeException`을 사용해 강제적 `throws` 선언 없이 유연하게 처리한다.

##### 🧠 기억해야 할 패턴 또는 로직 흐름
- `Map<String, Supplier<Notification>>` 구조로 알림 객체 등록
- `register()` 메서드를 통해 생성자 참조 혹은 람다식을 등록
- `createNotification()` 호출 시 `get()`을 통해 객체 반환
- 잘못된 타입 입력 시 `TypeErrorException` 발생

##### 💻  코드 (Java)
```java
class NotificationFactory {
        private HashMap <String, Supplier> registry = new HashMap<>();

        public void register(String type, Supplier <Notification> supplier){ // 새로운 알림 객체를 등록할 수 있도록 함. 
            registry.put(type.toLowerCase(), supplier);
        }

        public Notification createNotification(String type) {
            Supplier <Notification> supplier = registry.get(type.toLowerCase());
            if (supplier != null){
                return supplier.get();
            }

            throw new TypeErrorException("지원하지 않는 알림 타입: " + type);  // throw문을 만나면 해당 예외를 실행함. 여기선 if에서 return으로 끝내줘서 if에 걸리면 아래까지 내려올 일이 없음.
        }
}

class TypeErrorException extends RuntimeException{ // TypeErrorException을 RuntimeException으로 바꾸면 뭐가 좋나 -> throws 선언 안 해도 되고, 호출하는 쪽에서도 try-catch가 필수가 아님.
    public TypeErrorException(String messege){     // Unchecked Exception (언체크 예외) -> 컴파일러가 강제하지 않음. 그냥 에러 메세지 띄우고 넘어감.
        super(messege);
    }
}

public class Main {
    public static void main(String[] args) {
        NotificationFactory factory = new NotificationFactory();

        factory.register("email", EmailNotification::new);
        factory.register("push", PushNotification::new);

        factory.createNotification("email").send("hyungyugod@naver.com", "반갑습니다. 현규씨");
        factory.createNotification("push").send("sunghyungyu", "안녕하세요. 현규씨");
    }
}
```

##### :: 의 활용과 의미
- ::는 함수를 "데이터처럼" 전달하기 위한 문법으로 메서드 이름이나 생성자를 변수처럼 넘겨줄 수 있게 해준다.
- Class::staticMethod: 정적 메서드 참조
- object::instanceMethod: 특정 객체의 메서드 참조
- Class::instanceMethod: 인자를 받아 실행될 인스턴스 메서드 참조
- Class::new: 생성자 참조

- String::toLowerCase: s -> s.toLowerCase()	// 문자열을 소문자로 바꿈
- Integer::parseInt: s -> Integer.parseInt(s)	// 문자열을 int로 변환
- System.out::println: x -> System.out.println(x)	// 콘솔 출력
- Apple::new: () -> new Apple()	// Apple 객체 생성
- String[]::new: n -> new String[n]	// String 배열 생성자 참조

### 1-2. 지역별 캘린더 시스템 만들기 
-### 📌 1-2. 지역별 캘린더 시스템 만들기 (Factory + Supplier 활용)

#### 🔍 핵심 개념 및 주의할 점
- 지역명 문자열만으로 적절한 Calendar 객체를 동적으로 생성할 수 있도록 `Map<String, Supplier<Calendar>>` 구조 사용
- 추상 클래스 `Calendar`를 기반으로 지역별 달력 클래스를 다형성 있게 처리
- 객체 생성 실패 시 사용자 정의 `RuntimeException`을 통해 예외 처리

#### 🧠 기억해야 할 패턴 또는 로직 흐름
- 추상 클래스 `Calendar` 정의 → 지역별 구현 클래스에서 `showInfo()` 및 `getHolidays()` 구현
- `CalendarFactory.register()` 메서드로 지역명-생성자 매핑 등록
- 클라이언트에서 `getInstance()` 호출 시 지역명 기반 객체 생성 및 반환
- 등록되지 않은 지역 요청 시 사용자 정의 `TypeError` 예외 발생

#### 💻 코드 (Java)
```java
public class Main {

    public static void main(String[] args) {
        CalendarFactory.register("korea", KoreaCalendar::new); // 요 3개는 서비스 제공자가 미리 입력해 놓고 들어가야함. -> 이렇게 하면 나라 추가할때 나라 클래스 만들고 객체만 업데이트해두면 끝이다.
        CalendarFactory.register("us", USCalendar::new);
        CalendarFactory.register("ism", IslamicCalendar::new);

        CalendarFactory.getInstance("ism").getHolidays(2025);
    }
}

abstract class Calendar {   // 근데 왜 인터페이스로 제시하지 않고 추상 클래스로 제시했을까 -> 공통 필드 추가가능 (정체성이기 때문 -> 한국 달력은 달력이다. // interface는 기능이므로 한국 달력은 셀 수 있다와같이 기능적인 설명이 들어가야 맞음. )
    public abstract void showInfo();
    public abstract void getHolidays(int year);
    }

class KoreaCalendar extends Calendar{
    @Override
    public void showInfo() {
        System.out.println("한국 캘린더 주 시작: 일요일 / 공휴일: 양력 기준");
    }

    @Override
    public void getHolidays(int year) {
        System.out.printf("%d 한국 휴일 목록\n", year);
    }

    
}

class USCalendar extends Calendar{
    @Override
    public void showInfo() {
        System.out.println("미국 캘린더 주 시작: 일요일 / 공휴일: 대통령의 날 포함");
    }

    @Override
    public void getHolidays(int year) {
        System.out.printf("%d 미국 휴일 목록\n", year);
    }
}

class IslamicCalendar extends Calendar {

    @Override
    public void showInfo() {
        System.out.println("이슬람 캘린더 주 시작: 토요일 / 공휴일: 이슬람력 기준");
    }

    @Override
    public void getHolidays(int year) {
        System.out.printf("%d 이슬람 휴일 목록\n", year);
    }
}

class CalendarFactory {
    private static Map <String, Supplier <Calendar>> registry = new HashMap<>();

    public static void register(String region, Supplier <Calendar> constructor){
        registry.put(region.toLowerCase(), constructor);
    }

    public static Calendar getInstance(String region){ // Calender 클래스의 객체를 리턴 (Calendar 타입의 객체를 리턴)
        Supplier <Calendar> supplier = registry.get(region);
        if (supplier != null){
            return supplier.get();  // supplier는 get을 통해 결과값을 반환한다.
        }

        else {
            throw new TypeError();
        }
        }
    }

class TypeError extends RuntimeException{
    public TypeError(){
        System.out.println("나라 이름을 잘못 입력하셨습니다.");
    }
}
```

### 📌 1-3. 열거형 + 싱글턴 팩토리: 글로벌 캘린더 생성기 (심화 버전)

#### 🔍 핵심 개념 및 주의할 점
- enum은 **서로 관련된 상수들을 타입 안전하게 묶을 수 있는 특수한 클래스**이다.
- 열거형 내부에 **필드, 생성자, 메서드**를 정의할 수 있으며, 이를 활용하면 전략 패턴이나 팩토리 패턴 구현이 가능하다.
- Java의 enum 상수는 **싱글턴 객체로 동작**하며, 각 상수에 대해 메서드를 오버라이드할 수 있다.
- **EnumMap**은 enum을 키로 사용하는 고성능 전용 Map 구조로, 타입 안정성과 성능 면에서 뛰어나다.
- **정적 내부 클래스(Holder 패턴)**를 활용한 싱글턴 구현은 초기화 지연(지연 로딩)과 스레드 안전성을 모두 확보한다.
- 외부에서 캘린더 객체에 접근할 때는 `Region` enum을 통해 캘린더를 식별하고, `CalendarFactory`를 통해 인스턴스를 제공받는다.
- `.java` 파일에는 `public` 클래스나 `enum`이 하나만 가능하므로, enum을 외부에 둘 경우 파일명과 일치해야 한다.
- day.class -> 열거형 Day 클래스에 대한 클래스 정보 객체 (Class<Day>): enummap에서 new enummap<>(day.class);로 배열을 구성하는 클래스의 정보를 넘겨줘야 한다.
-  "입력은 문자열, 내부는 enum" 조합이 가장 실용적이다. 오타를 방지하고 내부 구동에서 효율적이다. 확장성도 더 뛰어나다.

#### 🧠 기억해야 할 패턴 또는 로직 흐름
- `Calendar`라는 추상 클래스를 정의하여 **공통 인터페이스**를 구성한다.
- 각 지역별 캘린더 클래스(KoreaCalendar 등)는 `Calendar`를 상속하고, **정적 내부 Holder 클래스를 통해 싱글턴 객체를 생성**한다.
- `Region` enum은 각 상수(KOREA, US, ISLAMIC)에 대해 `getCalendar()` 메서드를 구현하여 **객체 생성 책임을 위임**한다.
- `CalendarFactory` 클래스는 **EnumMap을 초기화**하여, 각 Region에 해당하는 캘린더 인스턴스를 등록한다.
- 클라이언트(main)는 `CalendarFactory.getCalendar(Region.XXX)` 형태로 글로벌 캘린더를 획득하고, 공통 메서드를 호출한다.


- enum 기본 문법
```java 
public enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}
```
- enum 내부 동작 코드
```java
public final class Day extends Enum<Day> {

    public static final Day MONDAY = new Day("MONDAY", 0);
    public static final Day TUESDAY = new Day("TUESDAY", 1);
    public static final Day WEDNESDAY = new Day("WEDNESDAY", 2);

    private static final Day[] VALUES = { MONDAY, TUESDAY, WEDNESDAY };

    private Day(String name, int ordinal) {
        super(name, ordinal);
    }

    public static Day[] values() {
        return VALUES.clone();
    }

    public static Day valueOf(String name) {
        for (Day d : VALUES) {
            if (d.name().equals(name)) {
                return d;
            }
        }
        throw new IllegalArgumentException("No enum constant " + name);
    }
}
```

#### 💻 글로벌 캘린더 생성기 코드 완성본
```java
public class Main {

    public static void main(String[] args) {
        CalendarFactory.getCalendar(Region.KOREA).getHolidays(2025); // enum 상수로 값에 접근
    }
}

abstract class Calendar { // calander라는 공통 속성을 정의하는 추상 클래스
    public abstract void showInfo();
    public abstract void getHolidays(int year);
}

class KoreaCalendar extends Calendar{
    private KoreaCalendar(){}
    
    private class Holder{
        private static final KoreaCalendar ko = new KoreaCalendar(); // holder는 오직 만드는 역할만만
    }

    public static Calendar getInstance(){ // 얘를 밖에서 부르려면 무조건 class를 통해야 하므로 static으로 해주어야 한다.
        return Holder.ko;
    }

    @Override
    public void showInfo() {
        System.out.println("한국 캘린더 주 시작: 일요일 / 공휴일: 양력 기준");
    }

    @Override
    public void getHolidays(int year) {
        System.out.printf("%d 한국 휴일 목록\n", year);
    }

}

class USCalendar extends Calendar{
    private USCalendar(){}
    
    private class Holder{
        private static final USCalendar ko = new USCalendar(); // holder는 오직 만드는 역할만만
    }

    public static Calendar getInstance(){
        return Holder.ko;
    }


    @Override
    public void showInfo() {
        System.out.println("미국 캘린더 주 시작: 일요일 / 공휴일: 대통령의 날 포함");
    }

    @Override
    public void getHolidays(int year) {
        System.out.printf("%d 미국 휴일 목록\n", year);
    }
}

class IslamicCalendar extends Calendar {
    private IslamicCalendar(){}
    
    private class Holder{
        private static final IslamicCalendar ko = new IslamicCalendar(); // holder는 오직 만드는 역할만만
    }

    public static Calendar getInstance(){
        return Holder.ko;
    }

    @Override
    public void showInfo() {
        System.out.println("이슬람 캘린더 주 시작: 토요일 / 공휴일: 이슬람력 기준");
    }

    @Override
    public void getHolidays(int year) {
        System.out.printf("%d 이슬람 휴일 목록\n", year);
    }
}

enum Region {
    
    KOREA {
        public Calendar getCalendar(){
            return KoreaCalendar.getInstance();
        }
    }, 
    US {
        public Calendar getCalendar(){
            return USCalendar.getInstance();
        }
    },
    ISLAMIC {
        public Calendar getCalendar(){
            return IslamicCalendar.getInstance();
        }
    };

    public abstract Calendar getCalendar(); // 공통 추상 매서드를 선언하고 내부 인자들이 이를 오버라이딩 하게 할 수 있다.
}

class CalendarFactory {
    private static EnumMap <Region, Calendar> box = new EnumMap<>(Region.class); // enummap은 enum을 키값으로 사용한다. enum 전용이기 때문에 성능이 좋고, 타입 안정성도 뛰어나다.

    static {
        for (Region i : Region.values()){
            box.put(i, i.getCalendar());
        }
    }

    public static Calendar getCalendar(Region region){
        return box.get(region);
    }
}
```



