[← README로 돌아가기](../README.md)

# AudioManager Phase D 백로그 — IDonDestroy + Setup SSOT 재설계

## 0. 개요

| 항목 | 내용 |
|------|------|
| 작성 시점 | 2026-05-12 |
| 트리거 세션 | btnMap race fix + AudioManager NRE Phase A 가드 세션 |
| 우선순위 | **중간** — 현재 visible bug 없음, 잠재 race 잔존 |
| 즉시 진행 부적합 사유 | 본 세션 컨텍스트 누적 + race fix 후 통합 작업 분리 권장 (헌법 §0 메타 원칙) |

## 1. 잔존 SSOT 위반 (백로그 사유)

**현재 상태**: AudioManager 의 Phase A defensive 가드 3곳(PlayEffect/PlayBGM/TryGetSfxClip)이 `Database == null` 상태에서 NRE 를 차단. 그러나 다음 SSOT 위반이 잔존:

1. **자기 초기화 보장 부재**: AudioManager 가 자기 Setup 완료 SSOT 를 보유하지 않음. 호출자(IntroSequenceScene + GameScene LoadStep)가 Setup 책임을 짊어짐.
2. **IDonDestroy 미구현**: 프로젝트 내 10개 Singleton 매니저(InputManager, SceneLoadManager, PlayerManager, ActManager, RelicSystemRoot, UIManager, TimeScaleManager, PlayerDataManager, DialogueManager 등) 모두 IDonDestroy 구현. **AudioManager 만 누락** → Scene 전환 시 destroy + lazy re-init 가능.
3. **Setup 중복 호출**: `IntroSequenceScene.cs:25` + `GameScene.cs:53` 두 곳에서 호출. IDonDestroy 였다면 한 번이면 충분. 중복 호출 자체가 "destroy 됨을 전제한 설계 흔적" 의심.

## 2. evidence (본 세션에서 수집)

진단 로그 `[AUDIO-DIAG]` 5지점으로 InstanceID 추적 결과 (Editor.log 캡쳐):

```
[AUDIO-DIAG] Init (Awake) | InstanceID=-120158
[AUDIO-DIAG] Setup begin   | InstanceID=-120158
[AUDIO-DIAG] Setup complete | Database!=null=True | InstanceID=-120158
[AUDIO-DIAG] PlayBGM(Battle) | Database!=null=True | InstanceID=-120158
[AUDIO-DIAG] PlayEffect(Button) | Database!=null=True | InstanceID=-120158
```

**해석**:
- InstanceID **-120158 단일 일관** → H1 가설(Singleton 인스턴스 교체) **폐기**
- Setup 호출 인스턴스 == PlayEffect 호출 인스턴스 → 현재 세션 race 없음
- 이전에 발생한 NRE는 **일회성 타이밍 race** 또는 prefab OnClick UnityEvent wire 시점 race 추정

## 3. Sub-tasks (Phase D 진행 시 단계)

### D1. IDonDestroy 인터페이스 적용

| 항목 | 내용 |
|------|------|
| 변경 | `public class AudioManager : Singleton<AudioManager>` → `public class AudioManager : Singleton<AudioManager>, IDonDestroy` |
| 영향 | Singleton.cs:88 `if (this is IDonDestroy) DontDestroyOnLoad(gameObject);` 자동 적용 → Scene 전환 시 destroy 차단 |
| 헌법 §0-1 Step 1 grep 의무 | 다른 10개 매니저 IDonDestroy 적용 패턴 + AudioManager 의 Scene 의존성 grep |
| 위험 | DontDestroyOnLoad 적용 시 첫 부트 씬의 AudioManager 인스턴스가 영구 보존 — Setup 1회 호출 보장 가능 |

### D2. Setup 중복 호출 정리

| 항목 | 내용 |
|------|------|
| 변경 | `IntroSequenceScene.cs:25` + `GameScene.cs:53` 중 **한 곳만 유지**. 첫 부트 씬(IntroSequenceScene) 호출 유지 + GameScene 호출 제거 권장 |
| 영향 | D1 적용 후 인스턴스 영구 보존 → Intro 에서 한 번 Setup 하면 GameScene 진입 시 Database 이미 채워진 상태 |
| 헌법 §0-1 Step 1 grep 의무 | Setup 호출 시점이 다른 LoadStep 의존성에 영향 주는지 grep (`AudioManager.Database` / `PlayBGM` / `PlayEffect` 호출 시점이 Setup 완료 전후 어디인가) |
| 위험 | TestBattle.cs:34 / TestRoom.cs:48 의 Setup 호출은 테스트 시나리오 — 별도 정리 또는 유지 |

### D3. (선택) Awake 자동 Setup 

| 항목 | 내용 |
|------|------|
| 변경 | `Init()` (Awake 트리거) 마지막에 `Setup().Forget()` 호출 — 자기 초기화 SSOT 보장 |
| 영향 | 호출자(LoadStep)의 Setup 책임 제거 → AudioManager 가 자기 초기화 SSOT 보유 |
| 헌법 unitask §1 위반 검토 | `async void` 금지 룰. `UniTaskVoid` + `.Forget()` 패턴으로 우회. 단 fire-and-forget 시 try/catch 의무 (§4) |
| 트레이드오프 | "View 가 Manager 부트를 강제" 우회 패턴과 유사한 합리화 위험. D1+D2 만으로 race 해소되면 D3 불필요 — YAGNI 적용 |
| 결정 | D1+D2 적용 후 race 잔재 검증 필요. 잔재 있으면 D3, 없으면 보류 |

## 4. 진행 트리거 조건 (백로그 → 즉시 승격)

다음 중 **하나라도** 발생 시 즉시 승격:

- AudioManager NRE 재발 (어느 시점이든)
- Singleton 인스턴스 교체 race 의심 신호 (InstanceID 추적 필요한 상황)
- Audio 시스템 라이프사이클 변경 작업 (BGM/SFX 추가, 볼륨 시스템 변경 등) 시 동시 처리
- 사용자 명시 요청

## 5. 검증 시나리오 (Phase D 진행 시 의무)

헌법 §0-1 Step 3 표준 검증:

- [ ] **① Intro → Game → Battle 정상 흐름**: Setup 1회 호출 (Intro), Database!=null 유지, NRE 0
- [ ] **② Scene 재로드 (Game → Intro → Game)**: InstanceID 유지 (DontDestroyOnLoad 작동), 중복 Setup 호출 없음
- [ ] **③ Phase A 가드 fallback 유지**: Database null 가드가 여전히 존재 (D1+D2 적용해도 안전망 제거 안 함)
- [ ] **④ 다른 매니저 패턴 일관성**: 10개 IDonDestroy 매니저와 라이프사이클 동일성 확인
- [ ] **⑤ 테스트 씬 회귀 0**: TestBattle/TestRoom 의 Setup 호출 영향 없음

## 6. 헌법 §0-1 Step 4 시니어 판단 의무

진행 시 보고에 명시:

- 합리화 시도 차단 ("이번엔 영향 작음" / "Quick fix" 금지)
- D1+D2+D3 옵션별 트레이드오프 매트릭스 (헌법 §7)
- 패턴 미러링 grep 인용 (다른 10개 매니저 IDonDestroy 구현 형태)
- 진단 결과 evidence-based 판정 (D3 진행 여부는 D1+D2 후 race 잔재 evidence 기반)

## 7. 참고 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §2 SSOT, §5 YAGNI, §7 보고 정책
- [.claude/rules/unitask-async.md](../.claude/rules/unitask-async.md) — §1 async void 금지 (D3 검토 시)
- [.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md) — IDonDestroy 미구현 anti-pattern 검출 시
- 본 백로그 트리거 세션 commit: btnMap race fix + AudioManager Phase A 가드 (2026-05-12)
