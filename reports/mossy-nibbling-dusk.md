# MainScene RNG 스모크 테스트 환경 구축 계획

## Context

카드 4(시드 기반 결정론 RNG)가 커밋됐고(`d75924e`, `297e025`) NUnit EditMode 테스트는 전부 그린이다. 사용자는 보드 진행(카드 4.5 승인)에 앞서 **실제 씬 런타임에서 RNG가 잘 작동하는지 직접 확인**하길 원한다 — 특히 "동일한 시드에서 동일한 난수 시퀀스가 나오는지"를 Debug.Log로 검증. 이를 위해 `MainScene`을 새로 만들고 그 안에 RNG 테스트 환경을 구성한다.

핵심 검증 목표: NUnit이 증명 못 하는 **런타임 배선** — Reflex 루트 컨테이너 lazy 빌드 → 씬 주입 → `IRandomFactory` 해석 → 실제 Play 모드에서의 결정론 재현.

## 탐색으로 확정된 사실 (재조사 불필요)

- **씬 필수 규약**: 씬에 `Reflex.Core.ContainerScope` 컴포넌트 GameObject **정확히 1개** (스크립트 GUID `5312032623c34414a54ea00e35a7eb8e`). 이게 루트 컨테이너 lazy 빌드 + 씬 전체 MonoBehaviour 자동 `[Inject]` 주입의 진입점. [SampleScene.unity](Assets/Scenes/SampleScene.unity)의 "SceneScope" 오브젝트가 참조 패턴.
- **주입**: Reflex 14.3.1은 씬 로드 시 모든 루트 GameObject에 `AttributeInjector` 자동 실행 — 하네스는 `[Inject]` 필드만으로 `IRandomFactory`를 받는다. 별도 컴포넌트 불요.
- **DI 등록**: [ProjectInstaller.cs](Assets/Scripts/Boot/ProjectInstaller.cs)에 `IRandomFactory → Pcg32RandomFactory` Singleton/Lazy 등록 완료. `RootSeed`는 DI에 없음 — **호출자가 값으로 생성**하는 파라미터.
- **RNG API**: `factory.DeriveSeedContext(RootSeed, OpponentId, MatchIndex, RoundIndex)` → `factory.CreateStream(ctx, RandomStreamKey.{Seon|Deal|AI}, ReplayCompatibilityVersions)` → `stream.NextUInt32() / NextInt(min,max) / Shuffle(list) / DrawCount / ReplayMetadata`.
  - 주의: `OpponentId`는 소문자 ASCII `[a-z0-9._-]` 1~64자만 허용, `ReplayCompatibilityVersions`는 non-empty 2개 문자열 필수, `RandomSeedContext` 생성자는 internal(팩토리 경유만).
- **asmdef**: `DoubleDown.Presentation`은 Domain·Reflex 미참조라 부적합. Boot는 가능하나 합성 루트 순수성 훼손. → **별도 DevSandbox asmdef 신설**.
- **씬 환경**: URP 2D (Main Camera + `UniversalAdditionalCameraData`, Global Light 2D). GameCore 서비스 6종은 이 테스트에 불필요. EventSystem은 런타임 자동 생성이라 씬에 불요.
- Unity Editor가 현재 열려 있음 — batchmode 불가, 파일 추가 시 포커스만 하면 자동 임포트.

## 구현 (2단계 — 스크립트 GUID 의존 때문에 순서 고정)

### Stage 1 — DevSandbox 어셈블리 + 테스트 하네스 (신규 2파일)

**`Assets/Scripts/DevSandbox/DoubleDown.DevSandbox.asmdef`** (신규)
- references: `DoubleDown.Domain`, `Reflex`. 엔진 참조 on (MonoBehaviour 필요).
- 근거: Boot 순수성 유지 + Slice A 종료 시 폴더째 삭제 가능(헌법 §4 삭제 용이성). 개발 전용 스모크 하네스 = 헌법 Escape Hatch(프로토타입) 적용.

**`Assets/Scripts/DevSandbox/RngSmokeTest.cs`** (신규, MonoBehaviour 1개)
- `[Inject] private IRandomFactory _factory;` (필드 주입)
- Inspector 필드: `ulong _rootSeed = 12345`, `bool _autoRunOnStart = true`
- **자동 검증 3종** (Start 시 실행, 각각 `[RngSmoke][Check]` 로그 + PASS/FAIL):
  1. **골든 벡터**: PCG32 공식 레퍼런스 6개 값 대조 (NUnit과 동일 기대값 — 런타임 재확인)
  2. **동일 시드 재현성** (사용자 핵심 요구): 같은 RootSeed로 시드 파생 2회 → MatchSeed/RoundSeed hex 일치 로그 + 같은 컨텍스트·키로 스트림 2개 생성 → 16 draw 시퀀스 완전 일치
  3. **스트림 독립성**: AI 스트림 기준선 16 draw → Deal/Seon에 임의 draw 끼워넣고 AI 재생성 → 기준선과 일치
- **인터랙티브** (`[ContextMenu]` — Play 중 Inspector에서 실행, UI 에셋 0개):
  - `Run All Checks` / `Rerun With Same Seed`(재현성 육안 대조용 동일 로그 재출력) / `Randomize Seed`(새 시드로 전환 후 전체 재실행) / `Deal Preview`
- **분배 미리보기** (`Deal Preview`): 48장 인덱스 리스트를 Deal 스트림으로 `Shuffle` → Ruleset 분할(플레이어 10·선수 10·바닥 8·더미 20) 로그 + `DrawCount`·`ReplayMetadata` 요약 로그. 카드 7(판 상태 분배)의 사전 검증 겸용.
- 로그 형식: `[RngSmoke][Check|Seed|Deal] ...` — `/unity-log-diagnostic RngSmoke`로 자동 판정 가능하게 구조화. 실패 시 `Debug.LogError`.
- 도메인 값 예시: `new OpponentId("smoke.dummy")`, `new ReplayCompatibilityVersions("slice-a-ruleset-v0.1", "dev")`.

### 체크포인트 A — 사용자: Unity 포커스 → 컴파일 확인
Unity가 새 스크립트를 임포트해 `.cs.meta` GUID를 발급해야 Stage 2 진행 가능 (수동 .meta 생성 금지 — CLAUDE.md GUID 재발급 리스크 룰).

### Stage 2 — MainScene 작성 (신규 1파일)

**`Assets/Scenes/MainScene.unity`** (신규)
- [SampleScene.unity](Assets/Scenes/SampleScene.unity) 구조 미러링: Main Camera(+URP cam data) / Global Light 2D / SceneScope(ContainerScope) — 씬 내 fileID만 신규 발급, 스크립트 GUID는 패키지 고정값이라 그대로 사용.
- 추가: `RngSmokeTest` GameObject + Stage 1에서 Unity가 발급한 `RngSmokeTest.cs.meta` GUID로 컴포넌트 참조.
- 씬 `.meta`는 Unity 자동 생성에 맡김. EditorBuildSettings 등록은 보류 — Editor Play에는 불필요, 카드 26(정식 판 씬)에서 씬 구성 확정 시 재검토.

### 실행 방식
Unity C# 다파일 신설이므로 위임 규칙에 따라 **Jarvis에게 위임** (Stage 1 → 체크포인트 → Stage 2를 한 위임 안에서 순차 진행, 범위 외 수정 금지 명시). 기존 파일 수정 0건이 목표.

## 검증 (Evaluation-Driven)

1. 사용자: MainScene 열고 **Play 진입** → Console에서 `[RngSmoke]` 로그 확인
2. Claude: **`/unity-log-diagnostic RngSmoke`** 로 Editor.log 자동 판정
3. 합격 기준:
   - `[RngSmoke][Check]` 3종 모두 PASS (골든 벡터·동일 시드 재현·스트림 독립성)
   - 같은 RootSeed로 `Rerun With Same Seed` 실행 시 MatchSeed/RoundSeed hex와 분배 결과가 이전 실행과 동일
   - `Randomize Seed` 시 다른 시퀀스 + 여전히 검증 3종 PASS
   - Console 예외·에러 0건 (주입 실패 시 NullReference가 첫 신호)
4. 회귀 가능 영역: 없음 (기존 파일 무수정, 신규 씬은 빌드 목록 미등록)

## 범위 외 (이번에 안 함)

- TMP Canvas UI (사용자가 Debug.Log 방식 선택)
- EditorBuildSettings 등록, 정식 판 씬(카드 26), 카드 4.5 이벤트 계약 커밋(별도 승인 대기 중)
- 워킹트리의 ES3Defaults.asset·카드 4.5 계약 파일 7개는 이 작업과 무관 — 건드리지 않음
