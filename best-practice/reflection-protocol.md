[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# Reflection Protocol — 세션 인사이트 반영 프로토콜

`/reflect` 명령어 + `reflection-curator` 서브에이전트 + `reflection-reminder.py` 훅 3중 구조의 동작 규약.

## 목적

Claude Code 세션 중 축적된 실전 교훈을 **Samantha 저장소에 체계적으로 반영**하여 다음 세션의 agent/skill/hook이 즉시 활용할 수 있도록 함. 자동 반영이 아닌 **사용자 승인 기반**.

## 3중 구조

### 1. 수동 트리거 — `/reflect` 명령어
사용자가 세션 정리 시 입력. `.claude/commands/reflect.md` 참조.

### 2. 자동 탐지 — `reflection-reminder.py` 훅
Stop 이벤트에서 파일 mtime 변경을 감지하여 필요 시 `/reflect` 사용을 제안. 자동 반영 X, 제안만.

### 3. 실제 분석·적용 — `reflection-curator` 에이전트
사용자 승인 후 CLAUDE.md 정책 준수하며 실제 파일 편집. `.claude/agents/reflection-curator.md` 참조.

## 반영 가치 판정 (5가지 기준)

인사이트가 다음 중 **2개 이상 충족** 시 반영 후보:

1. **재사용성** — 다른 도메인/작업에도 적용 가능
2. **반복 빈도** — 같은 실수/패턴이 2회 이상 발생
3. **자동화 가치** — 매 프롬프트 상기 없이 기본 행동으로 박을 수 있음
4. **일반화 가능** — 구체 사례를 넘어 규칙으로 추상화 가능
5. **인시던트 증거** — 과거 실패 사례로 경고 가치 높음

## 반영 위치 매핑

| 인사이트 유형 | 반영 위치 |
|-------------|---------|
| 재사용 설계 패턴 | `best-practice/*.md` (기존 섹션 또는 신규 파일) |
| 안티패턴 경고 | `.claude/rules/engineering-constitution.md` 또는 `best-practice/*.md` |
| 에이전트 기본 행동 개선 | `.claude/agents/<name>.md` |
| 위임 전략 업데이트 | `.claude/rules/web-delegation.md` |
| 반복 리팩토링 교훈 | `best-practice/refactoring-lessons.md` |
| 증거 기반 디버깅 패턴 | `best-practice/evidence-based-debugging.md` |
| 새 워크플로우 | `.claude/commands/<name>.md` |
| 자동 감지 로직 | `.claude/hooks/scripts/*.py` + `settings.json` |

## CLAUDE.md 정책 준수 (자동)

- 파일당 **200줄 이하** — `wc -l`로 사전/사후 확인
- 하나의 주제에 집중 — 200줄 접근 시 **신규 파일 분리**
- `best-practice/` / `implementation/` / `reports/` / `tips/` / `changelog/` 배치
- **상대 링크** (`../best-practice/...`) — GitHub URL 금지
- 뒤로 가기 링크 상단 포함 (best-practice 문서)
- README.md CONCEPTS/REPORTS 표 업데이트 (해당 시)

## 프로세스 (Phase 1~4)

### Phase 1 — 제안 (사용자 검토)
reflection-curator가 세션을 리뷰하고 각 인사이트를 다음 포맷으로 나열:

```
제안 N/전체:
  대상: [정확한 파일 경로]
  유형: [분류 — 예: 에이전트 기본 행동 개선]
  변경 요약: [2~4줄 핵심 내용]
  줄수: 현재 X → 예상 Y (200줄 정책 [OK / 주의 / 초과])
  [Y] 승인 / [N] 스킵 / [L] 상세 보기
```

### Phase 2 — 사용자 응답 대기
각 제안에 대한 Y/N 확인. 미승인은 파일 변경 없음.

### Phase 3 — 적용
승인분만 `Edit`/`Write`로 반영. 수정 직후 `wc -l` 재확인. 200줄 초과 시 **즉시 롤백 + 분리안 재제시**.

### Phase 4 — 최종 보고
각 수정 파일의 diff 요약 + 최종 줄수. 커밋은 사용자 별도 요청 시만.

## 금지 사항

- 사용자 승인 없는 자동 반영 금지
- 현 세션 외 내용 반영 금지
- 중복 반영 금지 — 기존 문서에 있는 내용은 생략
- 200줄 초과 편집 금지 — 위반 시 즉시 롤백
