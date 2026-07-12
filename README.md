# Samantha

GameCore Unity 프로젝트의 Claude Code 작업 자산(에이전트, 스킬, 룰, 모범 사례) 저장소. 개요와 워크플로우는 [CLAUDE.md](CLAUDE.md)를 참고하세요.

## CONCEPTS — best-practice/

| 문서 | 설명 |
|------|------|
| [evidence-based-debugging.md](best-practice/evidence-based-debugging.md) | 증거 기반 디버깅 4단계 프로토콜 + 데이터 layer 격리 |
| [refactoring-lessons.md](best-practice/refactoring-lessons.md) | 대규모 리팩토링 실전 체크리스트 |
| [overload-semantic-equivalence.md](best-practice/overload-semantic-equivalence.md) | 오버로드 의미론 등가성 검증 |
| [deferred-commit-pattern.md](best-practice/deferred-commit-pattern.md) | Backup → Mutate → Commit/Rollback 패턴 |
| [unitask-async-patterns.md](best-practice/unitask-async-patterns.md) | UniTask 비동기 인시던트 카탈로그 |
| [node-lifecycle-patterns.md](best-practice/node-lifecycle-patterns.md) | 상태 머신·노드 생명주기 패턴 |
| [node-persistence-matrix.md](best-practice/node-persistence-matrix.md) | 노드 저장 매트릭스 |
| [solid-unity-principles.md](best-practice/solid-unity-principles.md) | SOLID Unity 적용 카탈로그 |
| [determinism-hooks.md](best-practice/determinism-hooks.md) | 결정론 RNG 훅 |
| [reflection-protocol.md](best-practice/reflection-protocol.md) | 회고 프로토콜 |
| [asset-migration-sort-consistency.md](best-practice/asset-migration-sort-consistency.md) | 자산 마이그레이션 정렬 일관성 (case sensitivity) |
| [sheet-batch-readback.md](best-practice/sheet-batch-readback.md) | Google Sheets batch update sort 트리거 read-back 검증 |
| [multilayer-locale-snapshot.md](best-practice/multilayer-locale-snapshot.md) | 다중 layer L10n caller-driven snapshot 박멸 |
| [locale-aware-subclass-extension.md](best-practice/locale-aware-subclass-extension.md) | ILocaleAware subclass virtual + base 호출 (LSP) |
| [dead-stub-pattern.md](best-practice/dead-stub-pattern.md) | 호출자가 결과 무시하는 비동기 stub은 채우기보다 제거 |
| [external-critique-simulation.md](best-practice/external-critique-simulation.md) | 시니어 자가 검토 외부 비판자 6 질문 시뮬레이션 |
| [race-fix-meta-patterns.md](best-practice/race-fix-meta-patterns.md) | Unity 부트/씬 전환 race 메타 패턴 (3 채널 시뮬레이션 등) |
| [unity-csharp-version-check.md](best-practice/unity-csharp-version-check.md) | Unity C# LangVersion 사전 검증 (record struct/required 등) |
| [paradigm-transition-asymmetry.md](best-practice/paradigm-transition-asymmetry.md) | 코루틴→UniTask 등 패러다임 마이그레이션 비대칭 안전성 |
| [unity-ecs-lite-oop-srp.md](best-practice/unity-ecs-lite-oop-srp.md) | Unity ECS-lite + OOP SRP Composite prefab 정공 |
| [unity-lifecycle-message-override.md](best-practice/unity-lifecycle-message-override.md) | Unity 라이프사이클 메시지(Awake/Start/OnEnable) 가로채기 함정 + Init() Template Method |
| [measurement-driven-debug.md](best-practice/measurement-driven-debug.md) | 같은 영역 2회 추측 fix 실패 시 측정 도구 작성 의무 + PRNG/hash mixing 분포 검증 |
| [ui-transition-prefab-convention.md](best-practice/ui-transition-prefab-convention.md) | UI 트랜지션 prefab=Start SSOT 컨벤션 (CSS slide-from-* 정합) |
| [ui-visibility-two-layer-srp.md](best-practice/ui-visibility-two-layer-srp.md) | 사전 생성 UI 의 가시성 SSOT 2-layer (panel root vs content child) 분리 |
| [multi-axis-fast-path-guard.md](best-practice/multi-axis-fast-path-guard.md) | 시간축 다른 invariant 합성 가드 + caller-callee enabler 협업 |
| [cancel-cleanup-bypass.md](best-practice/cancel-cleanup-bypass.md) | try/catch OperationCanceled cleanup 우회 + 강제 토글 4-state 멱등 |
| [unity-test-mode-selection.md](best-practice/unity-test-mode-selection.md) | EditMode/PlayMode 판정은 "POCO 여부"가 아닌 내부 Unity API grep 기준 |
| [unity-editor-only-guards.md](best-practice/unity-editor-only-guards.md) | 에디터 전용 검증(collectionCheck/Debug.Assert)은 런타임 가드 아님 |
| [generation-token-reset.md](best-practice/generation-token-reset.md) | 일괄 리셋 세대 토큰 — CTS 교체 후 Cancel (swap-before-cancel) |

## RULES — .claude/rules/

| 룰 | 설명 |
|----|------|
| [engineering-constitution.md](.claude/rules/engineering-constitution.md) | SOLID/SSOT/디자인 패턴 헌법 |
| [unity-delegation.md](.claude/rules/unity-delegation.md) | Unity 작업 위임 규칙 |
| [unitask-async.md](.claude/rules/unitask-async.md) | UniTask 비동기 10개 룰 |
| [evaluation.md](.claude/rules/evaluation.md) | 평가 주도 검증 |
| [markdown-docs.md](.claude/rules/markdown-docs.md) | 문서 표준 |
