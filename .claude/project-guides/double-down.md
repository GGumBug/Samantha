# Double-Down — 프로젝트 지침

> `C:\Unity_Projects\Double-Down` 전용 지침. 실체는 Samantha 저장소가 관리하고(git 추적), Double-Down 루트의 `CLAUDE.md`가 `.claude/` 정션을 통해 import합니다. **Double-Down 안에서 이 파일을 수정하면 Samantha 워킹트리가 변경됩니다** — 정상 동작이며, 커밋은 Samantha 저장소에서 합니다.

팀 위임 규칙·SOLID/SSOT 헌법·UniTask 룰·검증 정책은 `.claude/rules/*.md`가 파일 종류에 따라 자동 주입하므로 여기 복사하지 않습니다.

## 프로젝트 개요

화투 기반 카드 게임. Unity **6000.3.19f1** / URP 17.3.0 / 2D (Aseprite·PSD·SpriteShape·Tilemap).

## 아키텍처 — Clean Architecture 단방향 의존

의존은 **항상 안쪽으로만** 흐릅니다. asmdef `references`가 이 계약을 컴파일 타임에 강제합니다.

| 어셈블리 | 참조 대상 | 성격 |
|---|---|---|
| `DoubleDown.Domain` | **없음** (`noEngineReferences: true`) | 순수 C#. **UnityEngine 참조 불가** |
| `DoubleDown.Simulation` | Domain | 밸런싱·시뮬레이션 |
| `DoubleDown.Application` | Domain | 유즈케이스·세션·스냅샷 |
| `DoubleDown.Infrastructure` | Application, Domain, Data.Generated | 저장·데이터 어댑터 |
| `DoubleDown.Presentation` | Application, InputSystem, uGUI | **Domain 직접 참조 금지** |
| `DoubleDown.Boot` | 전 계층 + Reflex + GameCore 5모듈 | 조립(Composition Root) 전용 |

**절대 규칙**:

- **Domain에 `using UnityEngine` 금지** — `noEngineReferences: true`라 컴파일 자체가 실패합니다. `Vector2`/`Random`/`Time`/`Debug.Log`가 필요하면 설계가 틀린 것입니다. 이 순수성 덕분에 `Tools/HeadlessSim`이 Unity 없이 Domain을 돌립니다 — 깨뜨리면 헤드리스 시뮬레이션이 죽습니다.
- **Presentation → Domain 직접 참조 금지** — Application의 `BoardSnapshot`/`PresentationVocabulary`를 경유합니다. 뷰가 도메인 타입을 직접 읽으면 경계가 무너집니다.
- **DI 조립은 Boot에서만** — Reflex 컨테이너 등록이 다른 계층으로 새면 Composition Root가 아닙니다.
- 새 어셈블리 참조를 추가하기 전에 **위 표의 방향을 위반하는지 먼저 확인**하고, 위반이면 코드를 쓰기 전에 사용자에게 구조 대안을 제시합니다.

## 패키지 스택

| 패키지 | 버전 | 용도 |
|---|---|---|
| UniTask | 2.5.11 | 모든 비동기 (`.claude/rules/unitask-async.md` 10룰 적용) |
| LitMotion | 2.0.2 | 트윈 — **DOTween 금지** |
| Reflex | 14.3.1 | DI 컨테이너 (Boot 전용) |
| Input System | 1.19.0 | 입력 (단일 액션 자산으로 통합됨 — 카드 26.5) |
| Test Framework | 1.6.0 | NUnit |

## GameCore 패키지

`Packages/com.ggumbug.gamecore` — 프로젝트 간 재사용 모듈. **Pooling / ResourceManagement / Scenes / Ticking / UI** 5개, 각각 Tests 어셈블리 보유.

GameCore 수정은 Double-Down 외 프로젝트에도 영향을 주는 **공용 변경**입니다. 게임 고유 로직을 GameCore에 넣지 말고, 반대로 GameCore 시그니처 변경 시 영향 범위를 명시하세요.

## 테스트

| 어셈블리 | 모드 | 대상 |
|---|---|---|
| `DoubleDown.Domain.Tests` | EditMode (`includePlatforms: ["Editor"]`) | Domain + Simulation |
| `DoubleDown.Application.Tests` | EditMode | Application |
| `DoubleDown.Infrastructure.Tests` | EditMode | Infrastructure |
| `DoubleDown.Integration.Tests` | **PlayMode 가능** (`includePlatforms: []`) | Boot·Infrastructure·Presentation 통합 |
| `GameCore.*.Tests` | 모듈별 | Pooling / Scenes / Ticking / UI |

**모드 판정은 "동기/POCO 여부"가 아니라 내부에서 쓰는 Unity API 기준**입니다 — `Object.Destroy` / `DontDestroyOnLoad` / 씬 API를 쓰면 PlayMode. 판정 전 grep 선행 의무 ([best-practice/unity-test-mode-selection.md](../../best-practice/unity-test-mode-selection.md)).

Domain 로직은 `Tools/HeadlessSim`(.NET 콘솔)으로 Unity 없이 대량 시뮬레이션할 수 있습니다 — 밸런싱·확률 검증은 Editor 재생보다 이쪽이 빠릅니다.

## 데이터 파이프라인

BGDatabase(`Assets/BansheeGz`) → 생성 코드 `DoubleDown.Data.Generated` → Infrastructure에서 소비.

**생성 코드와 그 변경을 유발한 생성 설정·원본 스키마는 같은 커밋**에 포함합니다. 생성물만 커밋하면 재생성이 불가능해집니다.

## 워크플로 — 카드 단위

작업은 **카드 번호** 단위로 진행합니다 (현재 26.5까지 완료). 커밋 메시지는 저장소 형식을 따릅니다:

```
<유형>: <제목> — <세부·근거> (카드 N)
```

유형: `코드` `테스트` `메타` `데이터` `문서` `도구` `설정` `아키텍처` `수정` `회고` `패키지`

- **AI 귀속 표시 절대 금지** — `Co-Authored-By`, "Generated with Claude Code" 등 어떤 형태도 넣지 않습니다
- `git add .` / `-A` 금지 — 경로 명시 후 `git diff --cached`로 범위 검증
- 커밋은 `/commit` 스킬 사용 권장 (저장소 규칙 내장, 격리 컨텍스트에서 실행)
- **신규 `.cs`의 `.meta` 짝 확인** — 에이전트가 만든 `.cs`의 `.meta`는 사용자가 Unity를 연 뒤 생성됩니다

## 검증 루프

1. 구현 에이전트(Jarvis/Sonny/Ava/TARS)가 편집
2. **`unity-reviewer`로 독립 검증** — 구현자와 검증자를 분리합니다
3. Unity 플레이 테스트가 필요하면 `[Prefix][Layer]` 진단 로그 삽입 → 사용자 재현 → `/unity-log-diagnostic <Prefix>`로 판정

`.gitignore`가 `/.claude`·`/CLAUDE.md`·`/AGENTS.md`·`/.codex/`를 무시하므로 이 설정들은 Double-Down 저장소를 오염시키지 않습니다. 설계·플랜 문서는 `C:/AI_Projects/Samantha/reports/`에 쌓입니다.
