# AGENTS.md

이 저장소는 GameCore Unity 프로젝트에서 사용하는 Codex 작업 자산과, Hwaseo·GameCore 운영 중 얻은 재사용 가능한 엔지니어링 지식을 관리합니다. 게임 애플리케이션 소스가 아니라 에이전트·스킬·훅·규칙·사례 문서의 참조 저장소입니다.

## Codex 구성 SSOT

- `AGENTS.md`: 저장소 전체에 지속 적용되는 작업 규칙
- `.codex/config.toml`: 프로젝트 MCP, 멀티에이전트, 셸 환경 설정
- `.codex/agents/*.toml`: 프로젝트 전용 커스텀 에이전트
- `.codex/hooks.json`, `.codex/hooks/`: 라이프사이클 훅과 음성 알림
- `.agents/skills/*/SKILL.md`: 저장소 공유 스킬
- `.claude/rules/*.md`: Claude 시절부터 공유하는 상세 엔지니어링 규칙 문서. 디렉터리 이름은 레거시이지만 Codex에서도 참조 문서로 사용
- `best-practice/`: 실제 인시던트에서 일반화한 패턴과 안티패턴
- `reports/`: 특정 기능·리팩터링의 설계 및 분석 기록

Codex 설정 형식이나 경로를 변경할 때는 추측하지 말고 현재 공식 Codex 문서를 먼저 확인합니다. 저장소 안의 운영 모범 사례 질문은 `best-practice/`, `reports/`, `README.md`를 먼저 검색합니다.

## Unity 작업 라우팅

Unity 코드·에셋 작업은 전문 에이전트에게 위임합니다.

| 범위 | 에이전트 |
|---|---|
| 여러 전문 분야가 얽힌 복합 작업, 분해·일정·품질 감독 | `samantha` |
| 아키텍처, ScriptableObject, 성능, 빌드 파이프라인 | `jarvis` |
| UI/UX, 셰이더, VFX, 애니메이션 | `ava` |
| 게임 디자인, 밸런싱, 플레이어, 적 AI, 전투, 물리 | `sonny` |
| 레벨, 씬, 환경, Cinemachine, 내러티브 배치 | `tars` |
| 구현 후 독립 검증, 회귀·테스트 누락 점검 | `unity-reviewer` |

- 단일 전문 분야는 해당 전문가에게 직접 위임합니다.
- 복합 작업만 Samantha에게 맡깁니다. Samantha는 `.codex/config.toml`의 `agents.max_depth = 2` 범위에서 전문가에게 한 단계 재위임할 수 있습니다.
- 전문가 에이전트는 추가 위임하지 않고 맡은 범위만 수행합니다.
- 서로 독립된 파일은 병렬 처리할 수 있지만, 공통 허브·SSOT 파일을 공유하면 직렬 처리합니다.
- 위임 프롬프트에는 작업 파일, 금지 파일, 기대 시나리오, 검증 방법을 명시합니다.
- 같은 파일의 1~3줄 오타·진단 로그처럼 로직과 API를 바꾸지 않는 수정은 직접 처리할 수 있습니다.

상세 기준은 [.claude/rules/unity-delegation.md](.claude/rules/unity-delegation.md)를 따르되, 에이전트 호출 방식과 경로가 충돌하면 이 `AGENTS.md`의 Codex 규칙이 우선합니다.

## 구현과 검증

- 비단순 변경은 구현 전에 `rg`로 영향 범위와 호출부를 전수 확인합니다.
- 코드 작성 후 관련 테스트·정적 검사·브라우저 확인 또는 Unity 플레이 테스트로 검증합니다.
- 구현자와 최종 검증자를 분리합니다. 구현 에이전트가 완료를 선언한 것만으로 성공 판정하지 않습니다.
- Unity 검증은 `unity-reviewer` 또는 `$unity-log-diagnostic`을 사용하고, 실행 결과를 근거로 판정합니다.
- 같은 가설로 두 번 실패하면 추측 수정을 중단하고 다중 가설 진단 로그를 설계합니다.
- 작업 종료 전 `git status --short`와 `git diff --stat`으로 범위 밖 변경을 확인합니다.

상세 규칙:

- [.claude/rules/evaluation.md](.claude/rules/evaluation.md)
- [.claude/rules/engineering-constitution.md](.claude/rules/engineering-constitution.md)
- [.claude/rules/unitask-async.md](.claude/rules/unitask-async.md)
- [best-practice/refactoring-lessons.md](best-practice/refactoring-lessons.md)
- [best-practice/race-fix-meta-patterns.md](best-practice/race-fix-meta-patterns.md)

## 문서와 지식 반영

- Markdown은 [.claude/rules/markdown-docs.md](.claude/rules/markdown-docs.md)를 따릅니다.
- 지침 파일은 200줄 이하로 유지하고 상세 설명은 `best-practice/` 또는 `reports/`로 분리합니다.
- 재사용 가능한 교훈을 반영할 때는 `$reflect`를 사용합니다. Reflection Curator는 먼저 제안만 만들고 사용자 승인분만 편집합니다.
- 새 best-practice 문서는 README 인덱스에 추가하고 상단에 README 복귀 링크를 둡니다.
- 특정 프로젝트·한 번의 세션에만 유효한 교훈은 전역 규칙으로 승격하지 않습니다.

## 작업 범위와 Git

- 기존 워킹트리 변경은 사용자 작업으로 간주하고 보존합니다.
- 범위 밖 문제는 보고만 하고 사용자의 승인 없이 함께 수정하지 않습니다.
- 파괴적 Git 명령을 사용하지 않습니다.
- 커밋을 요청받으면 파일별로 개별 커밋합니다. 한 커밋에 여러 파일을 묶지 않습니다.
- `git add .`와 `git add -A`를 사용하지 않고 파일 경로를 명시합니다.
- 커밋·PR·이슈에 AI 공동 작성자, 생성 표시, `Co-Authored-By`를 넣지 않습니다.

## 세션 위생

- 사용하지 않는 MCP는 활성화하지 않습니다.
- 주제가 완전히 바뀌면 새 task 또는 `/clear`를 사용합니다.
- 긴 작업은 실행 계획과 작은 검증 단위로 나눕니다.
- 장시간 명령은 중간 출력을 확인할 수 있게 실행하고, 60초 이상 사용자에게 진행 상황을 숨기지 않습니다.
