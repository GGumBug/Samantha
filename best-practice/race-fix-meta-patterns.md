[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# Race Fix 메타 패턴 — Unity 부트/씬 전환 race 카탈로그

본 세션 P0급 race fix 12건에서 추출한 메타 패턴. 한 채널만 시뮬레이션하면 시점 race를 못 잡는다.

## 1. 3 채널 시뮬레이션 의무

race 가능성 검토 시 **세 채널을 모두** 머릿속에 그려야 한다 — 한 채널만 보면 race 누락.

| 채널 | 시뮬레이션 내용 |
|------|-----------------|
| 매니저 흐름 | `Awake → OnEnable → Init → 처리` 시점 시퀀스 |
| 외부 API 동작 | Unity 부트, EventSystem 자동 활성, AsyncOperation `isDone` 시점 |
| 호출자 lifecycle | 호출자 OnDestroy가 매니저보다 먼저 발생할 가능성, token 전파 |

**검증**: 세 채널의 시점이 동일 frame에 일어날 때 race 가능성 명시.

## 2. Phase Hook 도입 시 try/finally 책임 모델 재검토

새로운 phase hook(예: `OnPhaseEnter`/`OnPhaseExit`)을 도입할 때 **outer finally가 inner state를 침범**하는 race 패턴 주의.

```csharp
// 안티패턴
try { await OnPhaseEnter(); /* inner state mutation */ }
finally { ResetAllState();   /* inner state까지 reset */ }
```

**처방**: outer try/finally 도입 시 inner phase가 mutate하는 state 범위를 매트릭스로 명시 → outer finally는 outer state만 다룬다.

## 3. 부트 흐름 vs Transition 흐름 시맨틱 차이

Unity **부트 첫 씬은 매니저 외부에서 활성화**된다 — `SceneManager.LoadScene` 같은 transition hook이 부트에는 안 걸림.

| 흐름 | 활성화 시점 | 매니저 hook 발화 |
|------|-------------|--------------------|
| 부트 첫 씬 | Editor Play 또는 빌드 시작 | OnEnable만 (transition hook 미발화) |
| Transition | `LoadSceneAsync` 완료 | OnSceneLoaded + OnEnable |

**처방**: transition 의존 부트 로직은 **별도 entry point** 필요 (예: `Bootstrap.cs` MonoBehaviour 첫 씬 배치).

## 4. 옛 패턴 제거 시 책임 이전 매트릭스 작성 의무

옛 패턴이 갖고 있던 **암묵적 책임**(EventSystem 단일 보장, AudioListener 단일 보장, active scene 의존)을 새 패턴이 자동으로 흡수하지 않는다.

**처방**: 마이그레이션 plan에 책임 매트릭스 첨부:

| 책임 | 옛 패턴 위치 | 새 패턴 위치 | 누락 위험 |
|------|--------------|--------------|-----------|
| EventSystem 단일 | Bootstrap.cs | (?) | High |
| AudioListener 단일 | MainCamera | (?) | High |
| Active scene 추적 | Singleton init | (?) | Medium |

**누락 위험 High** 책임은 새 패턴에 명시적 컴포넌트 배치 또는 매니저 책임 인계.

책임이 아니라 **상태·플래그**를 제거하는 경우의 대응 절차(읽기 지점 전수 + 독자 의미 분류표)는 [implicit-proxy-state-removal.md](implicit-proxy-state-removal.md).

## 5. Unity Additive 씬 Multi-Active 시점 매트릭스

additive 씬 multi-active는 race 다발 영역. 다음 컴포넌트는 **씬당 하나만 active**가 강제 — 두 개 이상 active 시 Unity 경고/오작동:

- `EventSystem` — UI 입력 무반응 또는 중복 처리
- `AudioListener` — 카메라 둘 다 사운드 처리 시 콘솔 경고
- Active scene 의존 (`SceneManager.GetActiveScene()`) — 씬 전환 timing 의존 코드

**처방**:
- additive load/unload hook에서 **`EventSystem.current` 검증 + 단일화 코드** 박제
- AudioListener는 카메라 prefab에서 `enabled=false` 기본값, 활성 카메라가 명시적으로 `true`

## 6. "race 안전" 단정 시 정적 안전성 vs 시간축 안전성 분리 의무

race fix 보고에서 **"race 안전"이라고 단정**하기 전에 두 축을 분리해서 모두 검증한다 — 한 축만 보면 정적 단정의 함정에 빠진다.

| 축 | 검증 내용 | 누락 시 결과 |
|----|----------|-------------|
| **정적 안전성** | null deref 방지, 예외 안전, 가드 존재 | (위반) NRE / 컴파일 오류 — 즉시 탐지 가능 |
| **시간축 안전성** | view OnEnable이 매니저 Awake보다 먼저 실행될 수 있는지 / lazy-init getter가 호출되는지 / Scene 전환 시 인스턴스 교체 발생하는지 | (위반) **부트 race 영구 보존** — 사용자 재현 전까지 미탐지 |

**정적 안전성만으로 "race 안전" 단정 금지.** 시간축 검증 절차:
1. 모든 view OnEnable 시점에 의존 매니저가 부트 완료 상태인가? (Scene 동시 활성화 시 race 가능)
2. `HasInstance` 같은 단순 null 체크 가드가 lazy-init을 트리거 안 하는가? (트리거 안 하면 영구 미부트 보존)
3. 가드 통과 실패 시 fallback / retry 경로가 있는가? (없으면 구독 영구 누락)

(2026-05-12 btnMap race fix 인시던트: Sonny 1차 위임이 BattleManager.IsActive SSOT 신설 + UIGame view-level 구독 + `if (BattleManager.HasInstance)` 가드 적용 후 "race 안전" 단정. 사용자 재현 시 Battle/Boss/Elite 노드 진입에서 btnMap 활성화 실패. root cause: `Singleton<T>.HasInstance`는 단순 null 체크라 lazy-init 미트리거, UIGame.OnEnable 시점 BattleManager 미부트 → 가드 통과 실패 → 구독 영구 누락. Editor.log `[BTNMAP-DIAG] OnEnable enter | HasInstance(before)=False` 로 시간축 race evidence 확정. 헌법 §0-1 Step 4 시니어 판단 의무의 갭 보강)

## 7. Lazy-init Singleton "상태 의존 vs 부트 의존" 컨텍스트 분류

Lazy-init Singleton 사용 시 호출 컨텍스트를 분류해서 가드 적합성을 판정한다 — **컨텍스트 mismatch 시 미러링 무효**.

| 컨텍스트 | 정의 | 권장 패턴 | 함정 |
|---------|------|-----------|------|
| **상태 의존** | 이미 부트된 후 상태 접근 (예: 다른 매니저 update tick 내부에서 BattleManager 상태 조회) | `HasInstance` 가드 OK — null 체크로 충분 | 없음 |
| **부트 의존** | 첫 트리거가 필요한 경우 (예: UIGame.OnEnable 시점 첫 구독) | `Instance` getter 직접 호출 필수 — lazy init 자동 트리거 | `HasInstance` 가드는 **영구 미부트 상태 보존**, 구독 영구 누락 |

**Hwaseo `Singleton<T>` 의미 차이**:
```csharp
// Singleton.cs:12 — 단순 null 체크, lazy init 트리거 안 함
public static bool HasInstance => _instance != null;

// Singleton.cs:14-35 — null 시 FindAnyObjectByType + CreateInstance 자동 실행
public static T Instance {
    get {
        if (_instance == null) {
            _instance = FindAnyObjectByType<T>();
            if (_instance == null) _instance = CreateInstance();
        }
        return _instance;
    }
}
```

**HasInstance 가드 사용 전 컨텍스트 분류 grep 의무**:
1. 호출 시점이 매니저 부트 이후 보장되는가? → 상태 의존, 가드 OK
2. 호출 시점이 부트 race 가능한가? → 부트 의존, getter 직접 호출 필수

(2026-05-12 btnMap race fix: Sonny가 다른 viewer 6곳 `HasInstance` 가드 패턴 미러링 보고했으나 6곳 모두 **상태 의존** 컨텍스트, UIGame.OnEnable만 **부트 의존**이라 미러링 무효 정당화)

## 본 세션 사례 매핑

| 사고 # | 메타 패턴 |
|--------|-----------|
| 1, 2 | §3 부트 vs transition |
| 3, 7 | §1 3 채널 시뮬레이션 (호출자 lifecycle) |
| 4 | §2 try/finally 책임 |
| 5, 8 | §4 책임 이전 매트릭스 |
| 6, 9, 10, 11, 12 | §5 additive multi-active |
| 13 (2026-05-12 btnMap) | §6 정적 vs 시간축 + §7 부트 의존 컨텍스트 |

## 참고

- [external-critique-simulation.md](external-critique-simulation.md) — 외부 비판 시뮬레이션
- [unitask-async-patterns.md](unitask-async-patterns.md) — UniTask 비동기 인시던트
- [.claude/rules/unitask-async.md](../.claude/rules/unitask-async.md) — UniTask 10개 룰
