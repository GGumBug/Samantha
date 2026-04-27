# 스킬 모범 사례

![Last Updated](https://img.shields.io/badge/Last_Updated-Apr%2013%2C%202026%208%3A02%20PM%20PKT-white?style=flat&labelColor=555) ![Version](https://img.shields.io/badge/Claude_Code-v2.1.101-blue?style=flat&labelColor=555)<br>
[![Implemented](https://img.shields.io/badge/Implemented-2ea44f?style=flat)](../implementation/claude-skills-implementation.md)

Claude Code 스킬 — 프론트매터 필드와 공식 번들 스킬.

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

## 프론트매터 필드 (13개)

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | 아니요 | 표시 이름 및 `/슬래시-명령어` 식별자. 생략 시 디렉토리 이름으로 기본 설정 |
| `description` | string | 권장 | 스킬의 역할. 자동 완성에 표시되고 Claude가 자동 검색에 사용 |
| `argument-hint` | string | 아니요 | 자동 완성 중 표시되는 힌트 (예: `[issue-number]`, `[filename]`) |
| `disable-model-invocation` | boolean | 아니요 | Claude가 이 스킬을 자동으로 호출하지 못하게 하려면 `true` 설정 |
| `user-invocable` | boolean | 아니요 | `/` 메뉴에서 숨기려면 `false` 설정 — 스킬은 에이전트 사전 로드를 위한 배경 지식이 됨 |
| `allowed-tools` | string | 아니요 | 이 스킬이 활성화될 때 권한 프롬프트 없이 허용되는 도구 |
| `model` | string | 아니요 | 이 스킬이 실행될 때 사용할 모델 (예: `haiku`, `sonnet`, `opus`) |
| `effort` | string | 아니요 | 호출 시 모델 노력 수준 재정의 (`low`, `medium`, `high`, `max`) |
| `context` | string | 아니요 | 격리된 서브에이전트 컨텍스트에서 스킬을 실행하려면 `fork`으로 설정 |
| `agent` | string | 아니요 | `context: fork`가 설정되었을 때 서브에이전트 타입 (기본값: `general-purpose`) |
| `hooks` | object | 아니요 | 이 스킬에 범위가 지정된 라이프사이클 훅 |
| `paths` | string/list | 아니요 | 스킬이 자동 활성화되는 조건을 제한하는 글로브 패턴. 쉼표로 구분된 문자열 또는 YAML 목록 허용 — Claude는 일치하는 파일로 작업할 때만 스킬을 로드 |
| `shell` | string | 아니요 | `` !`command` `` 블록의 셸 — `bash` (기본값) 또는 `powershell`. `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` 필요 |

---

## ![Official](../!/tags/official.svg) 공식 스킬 **(5개)**

| # | 스킬 | 설명 |
|---|------|------|
| 1 | `simplify` | 변경된 코드를 재사용, 품질, 효율성 측면에서 검토 — 중복을 제거하기 위해 리팩터링 |
| 2 | `batch` | 여러 파일에 걸쳐 명령어를 일괄 실행 |
| 3 | `debug` | 실패하는 명령어나 코드 문제 디버깅 |
| 4 | `loop` | 반복 간격으로 프롬프트나 슬래시 명령어 실행 (최대 3일) |
| 5 | `claude-api` | Claude API 또는 Anthropic SDK로 앱 빌드 — `anthropic` / `@anthropic-ai/sdk` 임포트 시 트리거 |

참고: 커뮤니티에서 유지 관리하는 설치 가능한 스킬은 [공식 스킬 저장소](https://github.com/anthropics/skills/tree/main/skills)를 참고하세요.

---

## 출처

- [Claude Code 스킬 — 공식 문서](https://code.claude.com/docs/en/skills)
- [모노레포에서의 스킬 검색](../reports/claude-operational-limits.md)
- [Claude Code 변경 이력](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
