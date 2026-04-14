[< back to README](../README.md)

# Harness Engineering (하네스 엔지니어링)

같은 AI 모델을 사용해도, **환경(하네스)**을 어떻게 설계하느냐에 따라 MVP 수준과 프로덕션 수준의 코드 품질 차이가 발생합니다. 마부가 말에게 안장과 고삐를 채우듯, 에이전트에게 방향을 지시하고 행동 반경을 통제하며 작업을 검증하는 시스템을 구축하는 것이 하네스 엔지니어링입니다.

> 참고: [패스트캠퍼스 "하네스 엔지니어링 40분 개념 정리 | 클로드 코드 × 코덱스"](https://fastcampus.co.kr) 내용을 기반으로 이 프로젝트에 맞게 적용한 문서입니다.

## 3가지 핵심 축

### 1. 컨텍스트 엔지니어링 (Context Engineering)

AI의 컨텍스트 윈도우는 한정적이므로, 모든 정보를 한 번에 넣으면 오히려 정확도가 떨어집니다. 가벼운 목차 문서(CLAUDE.md)를 두고, AI가 필요할 때만 상세 문서를 참조하도록 유도해야 합니다.

| 원칙 | Samantha 구현 | 위치 |
|------|--------------|------|
| CLAUDE.md는 목차/링크만 | 200줄 이하 제한, 상세 내용은 `best-practice/`로 분리 | `CLAUDE.md` |
| 토큰 최적화 5계명 | MCP 정리, `/compact`, `/clear`, 캐시 관리 | `CLAUDE.md` > 세션 위생 |
| 실행 계획 보존 | `plansDirectory: "./reports"` 설정으로 계획을 파일로 저장 | `.claude/settings.json` |
| 점진적 공개 | 스킬의 `user-invocable: false` + 에이전트 `skills:` 필드로 필요 시점에만 로드 | `.claude/skills/`, `.claude/agents/` |
| 규칙 분리 | glob 패턴 기반 `.claude/rules/` — 관련 파일 작업 시에만 주입 | `.claude/rules/*.md` |

### 2. 도구 및 환경 설계 (Environment Design)

초기에는 작업마다 개발자가 승인하는 단계를 거치고, 안전성이 확보된 후 자율성을 넓히는 점진적 접근이 필요합니다.

| 원칙 | Samantha 구현 | 위치 |
|------|--------------|------|
| 승인 기반 루프 | `ask` 권한으로 위험 명령어(rm, pip, docker 등) 실행 전 확인 | `.claude/settings.json` > permissions.ask |
| 도구 허용 목록 | 서브에이전트별 `tools:` 필드로 사용 가능 도구 명시적 제한 | `.claude/agents/*.md` |
| 훅을 통한 강제 주입 | SessionStart, PreToolUse 등 25개 라이프사이클 이벤트에 핸들러 연결 | `.claude/settings.json` > hooks |
| 설정 계층 구조 | managed → CLI → local → team → global 5단계 설정 상속 | `.claude/settings.json` 계층 |
| 샌드박스 | `respectGitignore: true`, 위험 명령어 deny/ask 분류 | `.claude/settings.json` |

### 3. 평가 주도 개선 (Evaluation-Driven Improvement)

코드가 잘 짜였는지 감으로 판단하지 않고, 테스트와 검증을 통해 시스템적으로 확인해야 합니다.

| 원칙 | 적용 방법 |
|------|----------|
| 느낌이 아닌 측정 | 코드 변경 후 반드시 관련 테스트 실행, UI 변경은 브라우저에서 직접 확인 |
| 자기 평가의 함정 방지 | 코드 작성 세션과 검증 세션을 분리 — 서브에이전트(`isolation: "worktree"`)로 독립 검증 |
| 교차 검증 | 작성 에이전트와 다른 에이전트가 리뷰 — `/simplify` 스킬 활용 |
| 회귀 방지 | PostToolUse 훅으로 편집 후 자동 검증 트리거 가능 |
| 계획-실행-검증 루프 | `plansDirectory`에 계획 저장 → 실행 → 결과를 계획과 대조 |

## 교차 검증 워크플로우

영상에서 강조하는 **하이브리드 검증** 패턴을 Claude Code 내에서 적용하는 방법:

```
1. 계획 모드 (/plan)로 작업 계획 수립 → reports/ 에 저장
2. 메인 세션에서 1차 코드 작성
3. 서브에이전트(isolation: "worktree")가 독립적으로 코드 리뷰
4. /simplify 로 품질 검증
5. 테스트 실행으로 최종 확인
```

핵심: **작성자와 검증자를 분리**하여 자기 평가 편향을 방지합니다.

## 팀 단위 하네스 운영

| 원칙 | Samantha 구현 |
|------|--------------|
| 팀 공통 규칙 공유 | `.claude/settings.json` (git 추적), `.claude/rules/` |
| 개인 재정의 | `.claude/settings.local.json` (gitignore), `hooks-config.local.json` |
| 강제 규칙 주입 | SessionStart 훅 + `.claude/rules/` glob 매칭으로 자동 적용 |
| 문서 안 읽기 방지 | 훅과 rules를 통한 시스템적 강제 (단순 문서화에 그치지 않음) |
