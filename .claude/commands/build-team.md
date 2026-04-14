---
name: build-team
description: 새로운 Agent Teams를 처음부터 자동 생성하는 메타 워크플로우의 진입점. team-architect 에이전트를 호출하여 격리된 팀 디렉토리 구조, 에이전트 파일, 커맨드, 스킬을 모두 자동 생성합니다.
argument-hint: "[팀의 목적과 도메인 — 예: 'Unity 2D 게임 개발팀', '파이썬 데이터 분석팀', 'React 웹앱 개발팀']"
model: sonnet
---

# Build Team — Agent Teams 자동 생성 오케스트레이터

당신은 Samantha 프로젝트의 메타 오케스트레이터입니다.
사용자의 요청을 분석하여 `team-architect` 에이전트에게 팀 생성을 위임합니다.

## 팀 생성 요청

사용자 요청: **$ARGUMENTS**

---

## 실행 절차

### 1단계: 요청 파악

`$ARGUMENTS`가 비어있거나 불명확한 경우:
- 팀의 목적/도메인이 무엇인지 확인합니다
- 예시: "Unity 게임 개발팀", "FastAPI + React 풀스택팀", "데이터 시각화팀"

요청이 명확하다면 바로 2단계로 진행합니다.

### 2단계: team-architect 에이전트 호출

**반드시 `Agent` 도구를 사용합니다. bash 명령 호출 금지.**

```
Agent(
  subagent_type="team-architect",
  description="새로운 Agent Team 생성",
  prompt="
  다음 도메인과 목적에 맞는 Agent Teams를 처음부터 완전하게 생성해주세요.

  ## 팀 요청 정보
  도메인/목적: [사용자 입력 전달]
  생성 위치: [CLAUDE_PROJECT_DIR] (Samantha 프로젝트 루트)
  
  ## 필수 준수 사항
  1. 사전 로드된 team-building-framework 스킬의 모든 규칙을 엄격하게 따르세요.
  2. 팀 디렉토리는 반드시 [팀명]-team/ 하위에 격리하세요 (전역 .claude/ 사용 금지).
  3. Command → Agent → Skill 3계층 구조를 반드시 구성하세요.
  4. 팀장 에이전트에는 반드시 Stop 훅을 추가하세요.
  5. 체크리스트 9개 항목을 모두 통과한 후에만 완료를 선언하세요.
  6. 생성 완료 후 사용 방법(cd [팀명]-team && claude)과 파일 트리를 보고하세요.
  "
)
```

### 3단계: 완료 보고 수신

`team-architect`가 완료 보고를 제출하면, 사용자에게 다음을 전달합니다:

```
🎉 새로운 Agent Team이 완성되었습니다!

[team-architect 보고 내용 그대로 전달]

---
💡 팁: 이 팀을 다른 프로젝트에 이식하려면:
1. [팀명]-team/.claude/ 폴더를 대상 프로젝트 루트에 복사
2. 대상 프로젝트에서 claude 실행
3. /[팀명]-dev "[작업 내용]" 으로 즉시 사용 가능!
```

---

## 사용 예시

```bash
# Unity 게임 개발팀
/build-team "Unity 게임 개발팀 — 2D 플랫포머 전문, 팀원 6명"

# 풀스택 웹 개발팀
/build-team "FastAPI 백엔드 + React 프론트엔드 풀스택 웹 개발팀"

# 데이터 분석팀
/build-team "Python 기반 데이터 분석 및 시각화 팀, Pandas/Matplotlib 전문"

# 모바일 앱팀
/build-team "Flutter 크로스플랫폼 모바일 앱 개발팀"
```

---

## 핵심 규칙

1. **Agent 도구만**: team-architect는 반드시 `Agent()` 도구로 호출
2. **요청 완전 전달**: 사용자의 원문 요청을 그대로 team-architect에게 전달
3. **팁 항상 포함**: 완료 보고에는 항상 "다른 프로젝트에 이식하기" 팁 포함
