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

## 5. Unity Additive 씬 Multi-Active 시점 매트릭스

additive 씬 multi-active는 race 다발 영역. 다음 컴포넌트는 **씬당 하나만 active**가 강제 — 두 개 이상 active 시 Unity 경고/오작동:

- `EventSystem` — UI 입력 무반응 또는 중복 처리
- `AudioListener` — 카메라 둘 다 사운드 처리 시 콘솔 경고
- Active scene 의존 (`SceneManager.GetActiveScene()`) — 씬 전환 timing 의존 코드

**처방**:
- additive load/unload hook에서 **`EventSystem.current` 검증 + 단일화 코드** 박제
- AudioListener는 카메라 prefab에서 `enabled=false` 기본값, 활성 카메라가 명시적으로 `true`

## 본 세션 사례 매핑

| 사고 # | 메타 패턴 |
|--------|-----------|
| 1, 2 | §3 부트 vs transition |
| 3, 7 | §1 3 채널 시뮬레이션 (호출자 lifecycle) |
| 4 | §2 try/finally 책임 |
| 5, 8 | §4 책임 이전 매트릭스 |
| 6, 9, 10, 11, 12 | §5 additive multi-active |

## 참고

- [external-critique-simulation.md](external-critique-simulation.md) — 외부 비판 시뮬레이션
- [unitask-async-patterns.md](unitask-async-patterns.md) — UniTask 비동기 인시던트
- [.claude/rules/unitask-async.md](../.claude/rules/unitask-async.md) — UniTask 9개 룰
