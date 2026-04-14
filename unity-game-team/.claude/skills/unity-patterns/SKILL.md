---
name: unity-patterns
description: Unity C# 코딩 패턴 참조 지식. Sonny(프로그래밍)와 TARS(시스템)에 사전 로드됩니다. MonoBehaviour 패턴, 이벤트 시스템, 오브젝트 풀링 등 Unity 모범 사례를 담고 있습니다.
user-invocable: false
---

# Unity C# 패턴 참조

이 스킬은 Unity 게임 개발에서 사용하는 핵심 코딩 패턴과 모범 사례를 정의합니다.

---

## 1. MonoBehaviour 생명주기 순서

```
Awake() → OnEnable() → Start() → FixedUpdate() (물리, 50fps)
                                → Update() (매 프레임)
                                → LateUpdate() (카메라 follow 등)
                     ← OnDisable() ← OnDestroy()
```

**규칙**:
- `Awake()`: 컴포넌트 캐싱, Singleton 초기화
- `Start()`: 다른 컴포넌트 참조, 초기값 설정 (Awake 이후 보장)
- `Update()`: 입력 처리, 상태 확인
- `FixedUpdate()`: Rigidbody 물리 연산

---

## 2. Singleton 패턴 (Unity용)

```csharp
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }
}
```

---

## 3. ScriptableObject 이벤트 패턴

```csharp
// GameEventSO.cs — 이벤트 정의
[CreateAssetMenu(menuName = "Game/Events/Game Event")]
public class GameEventSO : ScriptableObject
{
    private readonly List<GameEventListenerSO> _listeners = new();
    public void Raise() => _listeners.ForEach(l => l.OnEventRaised());
    public void Register(GameEventListenerSO l) => _listeners.Add(l);
    public void Unregister(GameEventListenerSO l) => _listeners.Remove(l);
}

// GameEventListenerSO.cs — 리스너
public class GameEventListenerSO : MonoBehaviour
{
    [SerializeField] private GameEventSO _event;
    [SerializeField] private UnityEvent _response;

    private void OnEnable() => _event.Register(this);
    private void OnDisable() => _event.Unregister(this);
    public void OnEventRaised() => _response.Invoke();
}
```

---

## 4. 오브젝트 풀링 패턴

```csharp
public class GenericPool<T> where T : MonoBehaviour
{
    private readonly Queue<T> _inactive = new();
    private readonly T _prefab;
    private readonly Transform _parent;

    public GenericPool(T prefab, int initialSize, Transform parent = null)
    {
        _prefab = prefab;
        _parent = parent;
        for (int i = 0; i < initialSize; i++)
            ReturnToPool(CreateNew());
    }

    public T Get(Vector3 position, Quaternion rotation)
    {
        T obj = _inactive.Count > 0 ? _inactive.Dequeue() : CreateNew();
        obj.transform.SetPositionAndRotation(position, rotation);
        obj.gameObject.SetActive(true);
        return obj;
    }

    public void ReturnToPool(T obj)
    {
        obj.gameObject.SetActive(false);
        _inactive.Enqueue(obj);
    }

    private T CreateNew() => Object.Instantiate(_prefab, _parent);
}
```

---

## 5. 상태 머신 패턴 (Enemy AI 등)

```csharp
public interface IState
{
    void Enter();
    void Update();
    void Exit();
}

public class StateMachine
{
    private IState _currentState;

    public void ChangeState(IState newState)
    {
        _currentState?.Exit();
        _currentState = newState;
        _currentState?.Enter();
    }

    public void Update() => _currentState?.Update();
}

// 사용 예
public class EnemyPatrolState : IState
{
    private readonly EnemyController _enemy;
    public EnemyPatrolState(EnemyController enemy) => _enemy = enemy;
    public void Enter() { /* 순찰 시작 */ }
    public void Update() { /* 순찰 로직 */ }
    public void Exit() { /* 정리 */ }
}
```

---

## 6. 입력 시스템 (New Input System)

```csharp
// InputHandler.cs
public class InputHandler : MonoBehaviour
{
    private PlayerInputActions _inputActions;

    // 읽기 전용 프로퍼티로 노출
    public Vector2 MoveInput { get; private set; }
    public bool JumpPressed { get; private set; }

    private void Awake()
    {
        _inputActions = new PlayerInputActions();
    }

    private void OnEnable()
    {
        _inputActions.Enable();
        _inputActions.Player.Jump.performed += OnJumpPerformed;
    }

    private void OnDisable()
    {
        _inputActions.Player.Jump.performed -= OnJumpPerformed;
        _inputActions.Disable();
    }

    private void Update()
    {
        MoveInput = _inputActions.Player.Move.ReadValue<Vector2>();
        JumpPressed = false; // Update에서 초기화
    }

    private void OnJumpPerformed(InputAction.CallbackContext ctx)
    {
        JumpPressed = true;
    }
}
```

---

## 7. Inspector 노출 규칙

```csharp
// ✅ 올바른 패턴
[Header("이동 설정")]
[SerializeField] private float _moveSpeed = 5f;
[SerializeField, Range(0f, 20f)] private float _jumpForce = 10f;
[SerializeField, Tooltip("초당 가속도")] private float _acceleration = 15f;

// ✅ 읽기 전용 상태 (Inspector에서 확인만 가능)
[field: SerializeField, HideInInspector]
public float CurrentSpeed { get; private set; }

// ❌ 금지: public 필드 (Inspector 노출이지만 캡슐화 없음)
public float moveSpeed = 5f;
```

---

## 8. 씬 객체 네이밍 컨벤션

```
[씬 루트]
├── _Managers/          ← 밑줄(_)로 시작 = 관리 오브젝트
│   ├── GameManager
│   └── AudioManager
├── Environment/        ← PascalCase
│   ├── Ground
│   └── Platforms
└── Player              ← 단수형, 태그와 일치
```

---

## 9. 성능 금지 목록 (Update 내부)

| 금지 패턴 | 대안 |
|---------|------|
| `GetComponent<T>()` | Awake에서 캐싱 |
| `FindObjectOfType<T>()` | Singleton 또는 직접 참조 |
| `Camera.main` | 캐싱 (`_camera = Camera.main`) |
| `new List<T>()` | 재사용 가능한 List 미리 할당 |
| `.ToString()` on numbers in UI | 이벤트 기반 갱신 |
| `string concatenation` | StringBuilder 또는 보간 ($) |

---

## 10. 레이어 매트릭스 표준

```
레이어 정의:
0: Default
3: Player
6: Enemy
7: Ground
8: Platform
9: Trigger
10: UI
11: Projectile

충돌 규칙:
- Player ↔ Ground: ✅
- Player ↔ Enemy: ✅
- Player ↔ Projectile(Enemy): ✅
- Enemy ↔ Ground: ✅
- Enemy ↔ Enemy: ❌ (성능 최적화)
- Projectile ↔ Projectile: ❌
```

---

## ⚠️ Gotchas — Claude가 자주 빠지는 함정 (반드시 숙지)

> 이 섹션은 Claude가 Unity 코드 작성 시 반복적으로 실수하는 패턴 목록입니다.
> 코드 작성 전에 반드시 확인하세요.

### G1. 이벤트 리스너 해제 누락
```csharp
// ❌ 자주 하는 실수: 구독만 하고 해제를 빠뜨림
private void OnEnable()
{
    GameEvents.OnPlayerDied += HandlePlayerDied;
}
// OnDisable에서 해제 없음 → 메모리 누수, 중복 호출

// ✅ 올바른 방법
private void OnEnable()  => GameEvents.OnPlayerDied += HandlePlayerDied;
private void OnDisable() => GameEvents.OnPlayerDied -= HandlePlayerDied;
```

### G2. Awake/Start 실행 순서 의존성
```csharp
// ❌ 위험: 다른 MonoBehaviour의 Awake가 먼저 실행됐다고 가정
private void Awake()
{
    // GameManager.Instance가 아직 null일 수 있음!
    _score = GameManager.Instance.CurrentScore;
}

// ✅ 올바른 방법: Start에서 다른 컴포넌트 참조
private void Start()
{
    _score = GameManager.Instance.CurrentScore; // 모든 Awake 완료 후 보장
}
```

### G3. new GameObject()로 프리팹 생성 금지
```csharp
// ❌ 금지: new 로 직접 생성
var enemy = new GameObject("Enemy");
enemy.AddComponent<EnemyController>();

// ✅ 반드시 프리팹을 Instantiate
var enemy = Instantiate(_enemyPrefab, spawnPos, Quaternion.identity);
```

### G4. Unity .meta 파일 절대 수동 삭제/수정 금지
- `.meta` 파일은 GUID 포함 — 삭제하면 에셋 참조 전체 깨짐
- 파일 이동/이름 변경은 반드시 **Unity Editor 내에서** 수행
- bash로 `mv`, `cp`, `rm` 으로 에셋 파일 조작 금지

### G5. Update에서 코루틴 남용
```csharp
// ❌ Update에서 매 프레임 코루틴 시작
private void Update()
{
    StartCoroutine(CheckHealth()); // 매 프레임 새 코루틴 생성!
}

// ✅ 상태 변화 시에만 시작
private void OnHealthChanged(float newHealth)
{
    StartCoroutine(FlashHealthBar());
}
```

### G6. Coroutine vs async/await 혼용 주의
- Unity 메인 스레드에서만 Transform, GameObject 조작 가능
- `async Task` 사용 시 `await` 후 Unity 객체 접근은 **항상 메인 스레드 여부 확인**
- 가능하면 Unity 전용 코루틴(`IEnumerator`) 사용 권장

### G7. ScriptableObject를 런타임에 직접 수정 금지
```csharp
// ❌ SO 에셋 직접 수정 → 에디터 플레이 중이면 영구 변경됨!
_gameConfigSO.maxHealth = 50;

// ✅ SO는 읽기 전용으로 사용, 런타임 데이터는 별도 클래스로
_runtimeData.maxHealth = _gameConfigSO.maxHealth;
_runtimeData.maxHealth = 50;
```
