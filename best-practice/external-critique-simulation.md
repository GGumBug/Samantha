[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# 외부 비판 시뮬레이션 — 시니어 자가 검토 강화

시니어 자가 검토 품질은 **외부 비판 압력에 비례**한다. 사용자/리뷰어 비판 채널이 활성화되어 있을수록 race/책임 누락이 사전에 잡힌다. 본 세션 P0급 race fix 12건 중 5건+이 사용자 비판 후 발견 — 자가 검토만으로는 불충분.

대안: **편집 직전 외부 비판자 시점 6 질문**을 박제하여 자가 검토 단계에서 외부 압력을 시뮬레이트.

## 사전 시뮬레이션 체크리스트 (편집 전 의무)

설계/패치 직전 다음 6 질문을 머릿속이 아니라 **명시적으로 답변 후 진행**:

1. **"이 흐름의 어디서 race가 나는가?"** — 시점 가정 검증. 매니저 `OnEnable` vs 호출자 `Awake` 순서, additive 씬 multi-active 시점.
2. **"외부 라이브러리(Unity API 등)가 이 시점에 어떤 동작을 하는가?"** — Unity 부트, EventSystem 자동 활성, AudioListener 충돌, AsyncOperation 라이프사이클.
3. **"호출자 lifecycle이 매니저보다 짧으면 어떻게 되는가?"** — token 전파 race, OnDestroy 후 매니저 콜백 잔존.
4. **"이 시그니처는 호출자가 깜빡 잊을 수 있는 패턴인가?"** — `Func<UniTask>` (token 클로저 의존) vs `Func<CancellationToken, UniTask>` (시그니처 강제).
5. **"이 옛 패턴 제거 시 책임이 어디로 이전됐는가?"** — EventSystem/AudioListener/active scene 의존 컴포넌트 책임 매트릭스.
6. **"사용자 시각에서 이 변경이 visible bug를 일으키는가?"** — 활성 중 언어 토글, 부트 첫 씬 입력 무반응, 시점 차이 hitch.

## 적용 트리거

다음 작업에서 **반드시** 6 질문 통과:

- 라이프사이클 hook 추가/제거 (`OnEnable`/`OnDisable`/`OnDestroy`)
- async 시그니처 변경 (token, return type, callback)
- Unity 부트/씬 전환 흐름 수정
- additive 씬 활성/비활성
- 옛 패턴 → 새 패턴 마이그레이션 (책임 이전 동반)

## 본 세션 사례 (race fix 12건 회고)

| # | 사고 | 사전 6 질문 통과 시 발견 가능 여부 |
|---|------|-------------------------------------|
| 1 | 매니저 `OnEnable` vs 호출자 부트 순서 | Q1 (시점 가정) — Yes |
| 2 | Unity 부트 첫 씬 매니저 외부 활성 | Q2 (외부 동작) — Yes |
| 3 | OnDestroy 후 token 잔존 | Q3 (lifecycle) — Yes |
| 4 | 코루틴→UniTask 시그니처 깜빡 yield | Q4 (시그니처 안전성) — Yes |
| 5 | EventSystem 단일 → multi-active 충돌 | Q5 (책임 이전) — Yes |
| 6 | 활성 중 언어 토글 visible bug | Q6 (사용자 시각) — Yes |

## 헌법과의 관계

- 헌법 §0 메타 원칙 — "원칙대로 했다"가 자체 정당화 안 되도록 외부 시점 보강
- 헌법 §0-1 Step 1 (영향 분석) — 외부 동작 시뮬레이션 항목으로 보강
- 헌법 §0-1 Step 4 (사용자 보고) — 6 질문 답변 결과를 보고 항목에 명시 권장

## 참고

- [race-fix-meta-patterns.md](race-fix-meta-patterns.md) — race 회고 메타 패턴 (3 채널 시뮬레이션 등)
- [refactoring-lessons.md](refactoring-lessons.md) — 일반 리팩토링 교훈
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — Senior Default Mode
