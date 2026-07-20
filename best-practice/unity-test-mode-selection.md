[← README로 돌아가기](../README.md)

# Unity 테스트 모드 판정 — EditMode vs PlayMode

"순수 동기 POCO + 외부 의존 0"은 EditMode 판정 근거가 아니다. 판정 기준은 **대상 코드가 내부에서 호출하는 Unity API**다. 클래스 구조(동기/비동기, POCO 여부, 의존성 개수)만 보고 판정하면 내부 API 함정을 놓친다.

## 인시던트 (2026-07-08 GameCore PoolService)

- 설계 단계에서 PoolService를 "순수 동기 POCO + 외부 의존 0 → EditMode 테스트 최저비용"으로 판정
- 실제 내부 구현은 `Object.Destroy`(에디트 모드에서 에러 — `DestroyImmediate` 필요)와 `DontDestroyOnLoad`(플레이 모드 전용)를 사용
- PlayMode 테스트로 정정 — 판정 프레임이 "동기/POCO 여부"였던 것이 원인

## 판정 프레임 비교

| 프레임 | 질문 | 결과 |
|--------|------|------|
| 잘못됨 | "동기인가? POCO인가? 외부 의존 0인가?" | 클래스 구조만 보고 내부 Unity API 누락 |
| 올바름 | "내부에서 어떤 Unity API를 호출하는가?" | grep으로 실제 사용 API 전수 확인 후 판정 |

## API → 모드 매핑 표

| Unity API | EditMode 동작 | 판정 |
|-----------|--------------|------|
| `Object.Destroy` | 에러 ("Destroy may not be called in edit mode") | PlayMode (또는 Destroy 경로 추상화) |
| `Object.DontDestroyOnLoad` | 플레이 모드 전용 — 에디트 모드 호출 무효/에러 | PlayMode |
| `SceneManager.LoadScene*` | 에디트 모드 제약 (`EditorSceneManager` 별도) | PlayMode |
| `StartCoroutine` / `Update` 루프 의존 | 플레이어 루프 없음 | PlayMode (`[UnityTest]`) |
| `Time.deltaTime` / `Time.time` 진행 | 플레이어 루프 없음 — 시간 정지 | PlayMode 또는 시간 추상화 |
| `new GameObject()` / `AddComponent` | 에디트 모드에서도 동작 | EditMode 가능 (정리는 `DestroyImmediate`) |
| 순수 C# 연산 / 컬렉션 / 이벤트 | Unity 무관 | EditMode |

## 판정 전 grep 선행 의무

테스트 전략(EditMode/PlayMode) 판정 전에 대상 클래스와 내부 호출 사슬에 대해 실행:

```bash
grep -nE "Object\.Destroy|DestroyImmediate|DontDestroyOnLoad|SceneManager\.|StartCoroutine|Time\.(deltaTime|time)" <대상 파일들>
```

- 매칭 0건 + `MonoBehaviour` 비의존 → EditMode 후보
- `Destroy` / `DontDestroyOnLoad` / 씬 API 매칭 → PlayMode (또는 해당 API를 boundary로 추상화한 뒤 EditMode)

grep 없이 "POCO니까 EditMode" 단정은 헌법 §0 합리화 회피 위반 ("코드 형태로 단정" 계열).

## 관련 룰

- [.claude/rules/evaluation.md](../.claude/rules/evaluation.md) — 평가 주도 검증
