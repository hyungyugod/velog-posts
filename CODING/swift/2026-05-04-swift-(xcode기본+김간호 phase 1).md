# 📌 1. Spring 개발자가 처음 만나는 Swift·iOS 앱 개발

## 1-1. Spring과 Swift 앱 구조 비교
> 💡 폴더 이름은 비슷하게, 내부 동작은 완전히 다르게

### 1) 핵심 매핑
- `controllers/` → `Scenes/` (요청 받는 화면 단위)
- `services/` → `Systems/` (도메인 로직)
- `mappers/` → `Repositories/` (외부 데이터 접근)
- `models/` → `Models/` (값 객체, struct 우선)

```swift
// Spring controllers → iOS Scenes
GanhoMusic Shared/
├── Scenes/         ← controllers/
├── Systems/        ← services/
├── Repositories/   ← mappers/
└── Config/         ← config/
```

---

## 1-2. 진입점 어노테이션
> 💡 `@main`은 `@SpringBootApplication`과 같은 "여기가 시작점" 표시

### 1) `@main`의 역할
- Swift 컴파일러에게 프로그램 진입점을 알리는 어노테이션
- Spring의 `main()` + `@SpringBootApplication`을 한 줄로 압축한 것
- 진입점은 앱 전체에서 단 하나만 존재 가능

```swift
@main
class AppDelegate: UIResponder, UIApplicationDelegate { }
```

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### 2) 콜론(`:`)의 이중 의미
- Java의 `extends` + `implements`를 콜론 하나로 통합
- 첫 번째 = 부모 클래스(상속), 나머지 = 프로토콜(구현)
- 단일 상속 + 다중 프로토콜 채택 원칙은 Java와 동일

```swift
class AppDelegate: UIResponder, UIApplicationDelegate { }
//                 ↑상속      ↑프로토콜 채택
```

---

## 1-3. Swift 함수 시그니처 문법
> 💡 외부 레이블과 내부 변수명을 분리해 호출부 가독성을 높임

### 1) 외부 레이블 vs 내부 변수명
- 형식: `func 함수명(외부레이블 내부변수명: 타입)`
- 외부 레이블 = 호출할 때 보이는 이름
- 내부 변수명 = 함수 본문에서 쓰는 이름
- 둘이 같으면 하나로 축약, `_`를 쓰면 외부 레이블 생략

```swift
// 분리형
func application(_ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [...]) -> Bool {
    return true
}
```

### 2) `didFinishLaunching`의 의미
- 프레임워크가 앱 실행 시점에 자동 호출하는 콜백
- 인자는 시스템이 자동 주입 (Spring `@Autowired` 비슷한 IoC)
- Spring이 `@PostConstruct` 호출하는 것과 동일한 라이프사이클 훅

---

## 1-4. Scene과 HTTP Session
> 💡 Scene = 앱 화면의 세션 단위. Spring HTTP Session과 같은 위치

### 1) Scene 생명주기
- `configurationForConnecting`: Scene 생성 시 설정 주입
- `didDiscardSceneSessions`: Scene 종료 시 리소스 해제
- 멀티 윈도우(iPad) 지원을 위해 도입된 개념

```swift
func application(_ application: UIApplication,
    didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
    // Scene 종료 시 정리
}
```

---

## 1-5. Optional 안전 언래핑 (`guard let as?`)
> 💡 Java의 `instanceof` + early return을 한 문법에 압축

### 1) `guard let as?` 패턴
- `as?`: 다운캐스팅 시도, 실패하면 nil 반환
- `guard let`: nil이면 즉시 함수 탈출(early return)
- 강제 언래핑(`!`) 금지 원칙의 핵심 도구

```swift
guard let skView = self.view as? SKView else {
    assertionFailure("Root view must be SKView.")
    return
}
```

```java
public void process(Object obj) {
    if (!(obj instanceof SKView)) return;
    SKView skView = (SKView) obj;
}
```

---

## 1-6. SpriteKit 어휘
> 💡 Sprite(라틴어 spiritus, 영혼) + Kit(도구 묶음) = 2D 게임 객체 도구상자

### 1) 어원 풀이
- **Sprite**: 라틴어 *spiritus*(영혼·정령) → 화면 위 떠다니는 2D 이미지로 의미 확장
- **Kit**: 영어 toolkit → 도구 묶음
- SpriteKit = Apple 공식 2D 게임 프레임워크

### 2) 노드 계층 구조
- `SKView` = 렌더링 엔진(브라우저 역할)
- `SKScene` = 한 화면 단위(HTML 페이지)
- `SKSpriteNode` = 이미지 객체(`<img>`)
- `SKLabelNode` = 텍스트(`<p>`)

```swift
SKView
 └── SKScene
      ├── SKSpriteNode  // 캐릭터·적·음표
      ├── SKLabelNode   // 점수·타이머
      └── SKShapeNode   // 도형
```

---

## 1-7. Apple 프레임워크 지도
> 💡 목적별로 분리된 도구 묶음 — 필요한 것만 import

### 1) 주요 프레임워크
- `UIKit`: 일반 앱 UI(버튼·레이아웃)
- `SpriteKit`: 2D 게임 / `SceneKit`: 3D 게임
- `CoreData`: ORM (JPA 포지션) / `Foundation`: 자료형·네트워크 (java.lang 포지션)
- `SwiftUI`: 선언형 UI (React 포지션)

---

## 1-8. enum을 네임스페이스로 쓰기
> 💡 case 없는 enum = 인스턴스화 불가능한 정적 상수 컨테이너

### 1) 설계 의도
- Java의 `private constructor` + `final class` 트릭을 컴파일러가 강제
- case가 없으니 인스턴스 생성 자체가 불가능
- 상수 모음에는 struct/class보다 enum이 관용적

```swift
enum GameConfig {
    static let gameDuration: TimeInterval = 45
    static let playerSpeed: CGFloat = 200
}
```

### 2) Java 비교
```java
public final class GameConstants {
    private GameConstants() {}
    public static final double GAME_DURATION = 45.0;
}
```

---

## 1-9. struct vs class
> 💡 값 타입(복사) vs 참조 타입(공유) — 정체성 유무로 결정

### 1) 선택 기준
- 데이터만 담는 작은 객체 → `struct` (값 복사, Java 14+ `record`와 유사)
- 정체성·생명주기가 있는 객체 → `class` (참조)
- `SKNode` 상속 객체는 SpriteKit 요구상 무조건 `class`

```swift
struct PhysicsCategory {
    static let player: UInt32 = 0b0001
    static let note:   UInt32 = 0b0010
    static let enemy:  UInt32 = 0b0100
}
```

---

## 1-10. extension으로 타입 확장
> 💡 내가 만들지 않은 타입에 외부에서 멤버를 추가하는 문법

### 1) Kotlin extension function과 유사
- 원본 타입 코드를 건드리지 않고 멤버 추가
- Java에는 없는 기능 — 유틸 클래스로 우회해야 함

```swift
extension UIColor {
    static let brandCoral = UIColor(red: 0.77, green: 0.52, blue: 0.48, alpha: 1.0)
}
view.backgroundColor = .brandCoral
```

---

## 1-11. 비트마스크 충돌 시스템
> 💡 2의 거듭제곱으로 카테고리 분리, OR 연산으로 권한 조합

### 1) 설계 원리
- 각 카테고리는 비트 자리 하나씩 차지(`0b0001`, `0b0010`, `0b0100`)
- `categoryBitMask`: 나는 누구인가
- `contactTestBitMask`: 누구와 충돌 이벤트를 받을 것인가
- `collisionBitMask`: 누구에게 물리적으로 막힐 것인가

```swift
player.physicsBody?.categoryBitMask    = PhysicsCategory.player
player.physicsBody?.contactTestBitMask = PhysicsCategory.note | PhysicsCategory.enemy
player.physicsBody?.collisionBitMask   = PhysicsCategory.wall
```

---

## 1-12. SpriteKit 좌표계
> 💡 UIKit과 반대 — 좌하단이 (0, 0)인 수학 좌표계

### 1) 좌표 차이
- UIKit: 좌상단 (0, 0)
- SpriteKit: 좌하단 (0, 0), Y축 위로 증가
- Scene 전환·노드 배치 시 헷갈리는 1순위 지점
