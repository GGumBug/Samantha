# Samantha

GameCore Unity 개발에 사용하는 Codex 에이전트·스킬·훅과 실전 엔지니어링 지식을 관리하는 저장소입니다. Hwaseo와 GameCore의 실제 인시던트가 `best-practice/` 지식의 주요 원천입니다. 게임 애플리케이션 소스는 포함하지 않습니다.

## 구조

| 경로 | 설명 |
|---|---|
| [AGENTS.md](AGENTS.md) | Codex 저장소 작업 규칙과 Unity 라우팅 SSOT |
| [.codex/config.toml](.codex/config.toml) | MCP·멀티에이전트·셸 환경 설정 |
| [.codex/agents/](.codex/agents/) | Samantha, Jarvis, Ava, Sonny, TARS, 검증자, 회고 큐레이터 |
| [.codex/hooks.json](.codex/hooks.json) | Codex 라이프사이클 훅 등록 |
| [.agents/skills/](.agents/skills/) | 브라우저, Unity 로그 검증, 회고 스킬 |
| [.claude/rules/](.claude/rules/) | Claude 시절부터 공유하는 상세 엔지니어링 규칙 문서 |
| [best-practice/](best-practice/) | 실제 실패에서 일반화한 설계·디버깅 패턴 |
| [reports/](reports/) | 특정 기능과 리팩터링의 설계·분석 기록 |

`.claude/` 자산은 기존 Claude Code 호환성과 과거 기록을 위해 유지합니다. Codex에서 자동으로 읽히는 SSOT는 `AGENTS.md`, `.codex/`, `.agents/skills/`입니다.

## Codex 팀

| 에이전트 | 역할 |
|---|---|
| Samantha | 복합 Unity 작업 분해·위임·시니어 품질 감독 |
| Jarvis | 아키텍처·성능·ScriptableObject·빌드 |
| Ava | UI/UX·셰이더·VFX·애니메이션 |
| Sonny | 게임 디자인·플레이어·AI·전투·물리 |
| TARS | 레벨·씬·환경·내러티브 |
| Unity Reviewer | 구현과 분리된 읽기 전용 검증 |
| Reflection Curator | 승인 기반 장기 지식 반영 |

## Rules

| 문서 | 설명 |
|---|---|
| [engineering-constitution.md](.claude/rules/engineering-constitution.md) | SOLID·SSOT·패턴 적용 헌법 |
| [l10n-ssot.md](.claude/rules/l10n-ssot.md) | L10n string snapshot 금지 헌법 (§2-0 시리즈 분리본) |
| [unity-delegation.md](.claude/rules/unity-delegation.md) | Unity 작업 위임과 범위 보존 |
| [unitask-async.md](.claude/rules/unitask-async.md) | UniTask 비동기 10개 규칙 |
| [evaluation.md](.claude/rules/evaluation.md) | 평가 주도 검증과 작성자·검증자 분리 |
| [markdown-docs.md](.claude/rules/markdown-docs.md) | Markdown 문서 표준 |

## Best practices

| 문서 | 설명 |
|---|---|
| [asset-migration-sort-consistency.md](best-practice/asset-migration-sort-consistency.md) | 자산 마이그레이션 정렬·대소문자 일관성 |
| [bgdatabase-asset-reference.md](best-practice/bgdatabase-asset-reference.md) | BGDatabase 에셋 참조 관리 |
| [bgdatabase-enum-binding.md](best-practice/bgdatabase-enum-binding.md) | BGDatabase enum 필드 3종·시트 어휘 계약·다형 컬럼 파싱 |
| [caller-driven-assumption-anti-pattern.md](best-practice/caller-driven-assumption-anti-pattern.md) | 호출자 상태를 암묵적으로 가정하는 설계 제거 |
| [cancel-cleanup-bypass.md](best-practice/cancel-cleanup-bypass.md) | 취소 예외의 cleanup 우회와 멱등 토글 |
| [dead-stub-pattern.md](best-practice/dead-stub-pattern.md) | 결과가 무시되는 비동기 stub 제거 |
| [deferred-commit-pattern.md](best-practice/deferred-commit-pattern.md) | Backup → Mutate → Commit/Rollback 패턴 |
| [delegation-truncation-triage.md](best-practice/delegation-truncation-triage.md) | 에이전트 절단 3상태 분류와 재위임 처방 |
| [determinism-hooks.md](best-practice/determinism-hooks.md) | 결정론 RNG 보존 훅 |
| [deterministic-reentry-cache.md](best-practice/deterministic-reentry-cache.md) | 재진입 시 결정론 캐시 |
| [distribution-parity-regression.md](best-practice/distribution-parity-regression.md) | 출력이 정당하게 달라지는 리팩터링의 분포·불변식 회귀 게이트 |
| [dual-meaning-field-split.md](best-practice/dual-meaning-field-split.md) | 사실과 계획을 겸직한 필드의 축 분리 |
| [evidence-based-debugging.md](best-practice/evidence-based-debugging.md) | 증거 기반 디버깅 4단계 프로토콜 |
| [external-critique-simulation.md](best-practice/external-critique-simulation.md) | 외부 시니어 비판자 시뮬레이션 |
| [generation-token-reset.md](best-practice/generation-token-reset.md) | 일괄 리셋의 swap-before-cancel 세대 토큰 |
| [golden-case-gate.md](best-practice/golden-case-gate.md) | 파이프라인 종단값 손계산 동결 게이트 |
| [implicit-proxy-state-removal.md](best-practice/implicit-proxy-state-removal.md) | 상태·접합부 제거 시 읽기 지점 전수 조사 |
| [locale-aware-subclass-extension.md](best-practice/locale-aware-subclass-extension.md) | locale-aware 상속 확장과 base 호출 |
| [measurement-driven-debug.md](best-practice/measurement-driven-debug.md) | 반복 추측 실패 후 측정 도구 전환 |
| [multi-axis-fast-path-guard.md](best-practice/multi-axis-fast-path-guard.md) | 서로 다른 시간축 invariant 합성 가드 |
| [multi-hypothesis-diagnostic.md](best-practice/multi-hypothesis-diagnostic.md) | 한 번의 재현으로 다중 가설 검증 |
| [multilayer-locale-snapshot.md](best-practice/multilayer-locale-snapshot.md) | 다중 레이어 L10n snapshot 제거 |
| [multilayer-state-sync.md](best-practice/multilayer-state-sync.md) | 여러 레이어 상태 동기화 |
| [node-lifecycle-patterns.md](best-practice/node-lifecycle-patterns.md) | 노드 생명주기와 Deferred Commit State Machine |
| [node-persistence-matrix.md](best-practice/node-persistence-matrix.md) | 노드별 저장 타이밍 계약 |
| [overload-semantic-equivalence.md](best-practice/overload-semantic-equivalence.md) | 오버로드 부수효과 의미론 등가성 |
| [paradigm-transition-asymmetry.md](best-practice/paradigm-transition-asymmetry.md) | 코루틴→UniTask 전환 비대칭 안전성 |
| [race-fix-meta-patterns.md](best-practice/race-fix-meta-patterns.md) | Unity 부트·씬 전환 race 메타 패턴 |
| [reflection-protocol.md](best-practice/reflection-protocol.md) | 세션 교훈의 장기 지식 반영 프로토콜 |
| [refactoring-lessons.md](best-practice/refactoring-lessons.md) | 대규모 리팩터링 실전 체크리스트 |
| [runstate-preserve-block-grep.md](best-practice/runstate-preserve-block-grep.md) | 런 상태 보존 블록의 grep 검증 |
| [runtime-contrast-assertion.md](best-practice/runtime-contrast-assertion.md) | 파생 표현 vs 권위 상태 런타임 자기 대조 |
| [second-producer-axis-drift.md](best-practice/second-producer-axis-drift.md) | 타입에 축 추가 시 생산자 전수와 필수 인자 강제 |
| [sentinel-anti-pattern.md](best-practice/sentinel-anti-pattern.md) | sentinel 값 기반 상태 표현의 위험 |
| [sequential-delegation-context-reuse.md](best-practice/sequential-delegation-context-reuse.md) | 동일 에이전트 연속 위임 컨텍스트 재사용 |
| [sheet-batch-readback.md](best-practice/sheet-batch-readback.md) | Google Sheets batch update 후 read-back 검증 |
| [single-composition-point.md](best-practice/single-composition-point.md) | 소유권 교대 제거와 단일 합성 지점 |
| [solid-unity-principles.md](best-practice/solid-unity-principles.md) | SOLID의 Unity 적용 카탈로그 |
| [stale-artifact-false-signal.md](best-practice/stale-artifact-false-signal.md) | 부산물 잔재를 판정자로 쓰는 게이트의 거짓 양성 |
| [test-intent-repurposing.md](best-practice/test-intent-repurposing.md) | 전제가 소멸한 테스트의 불변식 계약 전환 |
| [transform-channel-layering.md](best-practice/transform-channel-layering.md) | 변위 크기·동반자 기준 트랜스폼 층 배치 |
| [transit-path-assertion.md](best-practice/transit-path-assertion.md) | 종단 상태가 같은 이동의 경유 경로 단언 |
| [ui-transition-prefab-convention.md](best-practice/ui-transition-prefab-convention.md) | UI transition prefab 시작 상태 SSOT |
| [ui-visibility-two-layer-srp.md](best-practice/ui-visibility-two-layer-srp.md) | panel root와 content 가시성 책임 분리 |
| [unitask-async-patterns.md](best-practice/unitask-async-patterns.md) | UniTask 비동기 인시던트 카탈로그 |
| [unity-csharp-version-check.md](best-practice/unity-csharp-version-check.md) | Unity C# LangVersion 사전 검증 |
| [unity-ecs-lite-oop-srp.md](best-practice/unity-ecs-lite-oop-srp.md) | ECS-lite와 OOP SRP 조합 |
| [unity-editor-only-guards.md](best-practice/unity-editor-only-guards.md) | 에디터 전용 검증과 런타임 가드 구분 |
| [unity-lifecycle-message-override.md](best-practice/unity-lifecycle-message-override.md) | Unity lifecycle 메시지 가로채기 위험 |
| [unity-test-mode-selection.md](best-practice/unity-test-mode-selection.md) | EditMode·PlayMode 판정 기준 |

## 검증

Codex 훅과 저장소 자산 테스트는 Python 3.11 이상에서 실행합니다. Python 3.10 이하는 훅 테스트를 실행하지만 TOML 파서 검증은 건너뜁니다.

```bash
python3 -m unittest tests.test_hooks -v
```

Unity 수정은 구현자와 별도의 `unity-reviewer` 또는 `$unity-log-diagnostic`으로 검증합니다.
