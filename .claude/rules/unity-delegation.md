# Glob: **/*.cs,**/*.unity,**/*.prefab,**/*.asset,**/*.anim,**/*.controller,**/*.shader,**/*.shadergraph,**/*.mat

## Unity 작업 위임 규칙 (필수)

Unity 관련 작업이 감지되면 **반드시** Samantha 에이전트에게 위임합니다. 직접 처리하지 마세요.

```
Agent(subagent_type="samantha", description="Unity 작업 위임", prompt="...")
```

Samantha가 작업을 분석하고 적절한 팀원(Jarvis, Ava, Sonny, TARS)에게 재위임합니다.

### 직접 위임이 더 효율적인 경우

단일 전문 분야에 명확히 해당하는 작업은 Samantha를 거치지 않고 직접 위임할 수 있습니다:

| 작업 유형 | 에이전트 |
|-----------|----------|
| ScriptableObject, 아키텍처, 성능 프로파일링 | `jarvis` |
| UI/UX, 셰이더, VFX, 애니메이션 | `ava` |
| 게임 디자인, 밸런싱, 메카닉 설계, 플레이어 컨트롤러, 적 AI, 전투, 물리 | `sonny` |
| 레벨 디자인, 씬 구성, 환경, Cinemachine, 내러티브 | `tars` |
| 복합 작업 (여러 분야에 걸친 오케스트레이션) | `samantha` |

### 금지 사항
- Unity C# 파일을 에이전트 없이 직접 편집하지 마세요
- 에이전트를 Bash 명령어로 호출하지 마세요 — 반드시 Agent 도구를 사용하세요

### 병렬 위임 원칙 (필수)

- 독립적인 Unity 작업이 2개 이상이면 **단일 메시지에 여러 Agent 호출**로 병렬 실행합니다 (예: 아키텍처 리팩토링 + UI 색상 수정 → Jarvis + Ava 병렬)
- **Samantha 우회**: 서브에이전트는 내부에서 Agent/Task 도구를 쓸 수 없으므로, 병렬 위임이 명확한 복합 작업이라면 Samantha를 거치지 말고 상위 세션에서 Jarvis/Ava/Sonny/TARS를 직접 병렬 호출합니다. Samantha는 작업 분석이 모호하거나 순차적 오케스트레이션이 필요할 때만 사용합니다. (2026-04-15 Shop 노드 통합에서 Jarvis+Ava+Sonny 병렬 3호출로 약 2.3배 속도 향상 검증)
- **단일 에이전트 5개 항목 한계**: 한 에이전트 호출에 독립 항목을 5개 초과 몰아주면 `maxTurns: 25` 제한에 걸려 보고가 잘리고 일부 항목이 누락됩니다. 5개 초과면 ① 병렬로 분할 또는 ② 순차 호출(1차 → 검증 → 2차).

### 시각 버그 위임 우선순위 (Ava)

UI 미표시·반투명·색상 이상 등 Unity 시각 버그는 **코드/asset 수정 전에 Inspector 확인을 우선**합니다. Ava 위임 프롬프트에 반드시 명시: "Button.Disabled Color, SerializeField 할당, CanvasGroup.alpha를 코드 수정 전에 먼저 의심하고, 같은 가설 2회 실패 시 사용자에게 Inspector 확인을 요청하라".

### 리팩토링 위임 체크리스트

심볼 제거·시그니처 변경·인라인 추출 위임 시 프롬프트에 명시:

- [ ] 제거 대상 심볼을 `\.MethodName\(` 같이 **메서드 이름만 grep**하고 괄호 안은 육안 검토 (파라미터 값 기준 grep은 누락 유발)
- [ ] 사용처를 목록화한 후 **모든 수정을 한 번에** 위임 (분산하면 컴파일 에러)
- [ ] 인라인→유틸 추출이라면 **추출 전 책임 목록화 + 추출 후 책임 매핑**을 프롬프트에 명시하고 "기능 동등성 보존" 명시적 요구
- [ ] 기대 시나리오 1-2개 명시 (예: "minFloor=6 LocationType은 actLevel=3에서 추첨되지 않아야 함")

상세: [best-practice/refactoring-lessons.md](../../best-practice/refactoring-lessons.md)
