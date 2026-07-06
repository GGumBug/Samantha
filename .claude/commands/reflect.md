---
name: reflect
description: 현재 세션에서 축적된 인사이트/패턴/방법론을 Samantha 저장소(.claude/, best-practice/)에 반영할지 사용자에게 확인 후 CLAUDE.md 정책 준수하며 적용
argument-hint: [optional-focus-keyword]
---

# /reflect — 세션 인사이트 반영 워크플로우

이 명령어는 현재 Claude Code 세션에서 **AI 프로젝트 발전에 기여할 수 있는 인사이트**를 식별하고, 사용자 승인 후 Samantha 저장소에 반영합니다.

## 실행 절차

### 1단계: reflection-curator 서브에이전트 호출

Agent 도구로 다음 에이전트를 호출:

```
Agent(
  subagent_type="reflection-curator",
  description="세션 인사이트 반영 제안",
  prompt="현재 Claude Code 세션을 리뷰하고 반영 가치 있는 인사이트를 식별하세요.
  
  $ARGUMENTS가 비어있지 않으면 해당 키워드 관련 인사이트에만 집중.
  
  Phase 1(제안 목록 출력) → 사용자 Y/N 응답 대기 → Phase 3(승인분 적용) → Phase 4(최종 보고) 순서로 진행.
  
  CLAUDE.md 정책 준수 필수: 200줄 한도, 파일 구조 규칙, 상대 링크, README 업데이트."
)
```

### 2단계: 사용자 검토

서브에이전트가 Phase 1 포맷으로 제안 N개를 출력:
```
제안 1/N:
  대상: [경로]
  유형: [분류]
  변경 요약: [2~4줄]
  재사용성: [0~3점] — [도메인 specific / 부분 일반화 / 광범위 적용]
  줄수: X → Y (200줄 정책 체크)
  [재사용성 ≤ 1 시: "⚠️ 스킵 권장 — 도메인 specific" 명시]
  [Y] 승인 / [N] 스킵 / [L] 상세
```

재사용성은 **단독 거부 권한** — 1점 이하면 다른 기준 무관 스킵 권장. 자세한 점수 기준은 [reflection-curator.md](../agents/reflection-curator.md#재사용성-점수화-03).

### 3단계: 적용

사용자가 각 제안을 승인/스킵. 서브에이전트가 승인분만 실제 편집 + 최종 보고.

**일괄 명령 옵션** (서브에이전트 자동 인식):
- "재사용성 낮은 것 제외" / "특정 상황만 도움 되는 것 제외" → 재사용성 ≤ 1 자동 스킵
- "전부 적용" / "Y all" → 재사용성 무관 일괄 진행

## 사용 예

- `/reflect` — 전체 세션 리뷰
- `/reflect encounter` — Encounter 관련 인사이트만
- `/reflect SOLID` — SOLID 원칙 관련
- `/reflect refactoring` — 리팩토링 교훈만

## 자동 호출 조건 (훅에서)

Stop 훅이 세션 종료 시점에 다음 조건이면 이 명령어 제안:
- `git status`에 `.claude/` 또는 `best-practice/` 변경 있음
- Unity C# 파일 여러 개 수정 (아키텍처 작업 시그널)

## 정책 (자동 준수 — 서브에이전트 담당)

- 파일당 200줄 이하 — 초과 시 신규 파일 분리
- `best-practice/`, `implementation/`, `reports/`, `tips/` 배치 규칙
- 상대 링크 (`../best-practice/...`) — GitHub URL 금지
- 뒤로 가기 링크 포함 (best-practice 문서 상단)
- README.md CONCEPTS/REPORTS 표 업데이트 (해당 시)

## 금지 사항

- 사용자 승인 없는 자동 반영 금지
- 이번 세션 외 내용 반영 금지
