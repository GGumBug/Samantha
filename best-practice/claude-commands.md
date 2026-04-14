# 명령어 모범 사례

![Last Updated](https://img.shields.io/badge/Last_Updated-Apr%2013%2C%202026%208%3A00%20PM%20PKT-white?style=flat&labelColor=555) ![Version](https://img.shields.io/badge/Claude_Code-v2.1.101-blue?style=flat&labelColor=555)<br>
[![Implemented](https://img.shields.io/badge/Implemented-2ea44f?style=flat)](../implementation/claude-commands-implementation.md)

Claude Code 명령어 — 프론트매터 필드와 공식 내장 슬래시 명령어.

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
| `description` | string | 권장 | 명령어의 역할. 자동 완성에 표시되고 Claude가 자동 검색에 사용 |
| `argument-hint` | string | 아니요 | 자동 완성 중 표시되는 힌트 (예: `[issue-number]`, `[filename]`) |
| `disable-model-invocation` | boolean | 아니요 | Claude가 이 명령어를 자동으로 호출하지 못하게 하려면 `true` 설정 |
| `user-invocable` | boolean | 아니요 | `/` 메뉴에서 숨기려면 `false` 설정 — 명령어는 배경 지식이 됨 |
| `paths` | string/list | 아니요 | 이 스킬이 활성화되는 조건을 제한하는 글로브 패턴. 쉼표로 구분된 문자열 또는 YAML 목록 허용. 설정 시 Claude는 패턴과 일치하는 파일로 작업할 때만 스킬을 자동으로 로드 |
| `allowed-tools` | string | 아니요 | 이 명령어가 활성화될 때 권한 프롬프트 없이 허용되는 도구 |
| `model` | string | 아니요 | 이 명령어가 실행될 때 사용할 모델 (예: `haiku`, `sonnet`, `opus`) |
| `effort` | string | 아니요 | 호출 시 모델 노력 수준 재정의 (`low`, `medium`, `high`, `max`) |
| `context` | string | 아니요 | 격리된 서브에이전트 컨텍스트에서 명령어를 실행하려면 `fork`으로 설정 |
| `agent` | string | 아니요 | `context: fork`가 설정되었을 때 서브에이전트 타입 (기본값: `general-purpose`) |
| `shell` | string | 아니요 | `` !`command` `` 블록의 셸 — `bash` (기본값) 또는 `powershell` 허용. `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` 필요 |
| `hooks` | object | 아니요 | 이 명령어에 범위가 지정된 라이프사이클 훅 |

---

## ![Official](../!/tags/official.svg) 공식 명령어 **(69개)**

| # | 명령어 | 태그 | 설명 |
|---|--------|------|------|
| 1 | `/login` | ![Auth](https://img.shields.io/badge/Auth-2980B9?style=flat) | Anthropic 계정에 로그인 |
| 2 | `/logout` | ![Auth](https://img.shields.io/badge/Auth-2980B9?style=flat) | Anthropic 계정에서 로그아웃 |
| 3 | `/setup-bedrock` | ![Auth](https://img.shields.io/badge/Auth-2980B9?style=flat) | 인터랙티브 마법사를 통해 Amazon Bedrock 인증, 리전, 모델 핀 설정. `CLAUDE_CODE_USE_BEDROCK=1`이 설정된 경우에만 표시. 첫 Bedrock 사용자는 로그인 화면에서도 마법사 접근 가능 |
| 4 | `/setup-vertex` | ![Auth](https://img.shields.io/badge/Auth-2980B9?style=flat) | 인터랙티브 마법사를 통해 Google Vertex AI 인증, 프로젝트, 리전, 모델 핀 설정. `CLAUDE_CODE_USE_VERTEX=1`이 설정된 경우에만 표시 |
| 5 | `/upgrade` | ![Auth](https://img.shields.io/badge/Auth-2980B9?style=flat) | 더 높은 플랜으로 전환하기 위한 업그레이드 페이지 열기 |
| 6 | `/color [color\|default]` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | 현재 세션의 프롬프트 바 색상 설정. 사용 가능한 색상: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. 초기화하려면 `default` 사용 |
| 7 | `/config` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | 테마, 모델, 출력 스타일 등 설정 인터페이스 열기. 별칭: `/settings` |
| 8 | `/keybindings` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | 키바인딩 설정 파일 열기 또는 생성 |
| 9 | `/permissions` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | 도구 권한에 대한 허용/요청/거부 규칙 관리. 별칭: `/allowed-tools` |
| 10 | `/privacy-settings` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | 개인 정보 설정 보기 및 업데이트. Pro 및 Max 플랜 구독자만 사용 가능 |
| 11 | `/sandbox` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | 샌드박스 모드 전환. 지원되는 플랫폼에서만 사용 가능 |
| 12 | `/statusline` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | Claude Code의 상태 표시줄 설정. 원하는 것을 설명하거나 인수 없이 실행하면 셸 프롬프트에서 자동 설정 |
| 13 | `/stickers` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | Claude Code 스티커 주문 |
| 14 | `/terminal-setup` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | Shift+Enter 및 기타 단축키에 대한 터미널 키바인딩 설정. VS Code, Alacritty, Warp 등 필요한 터미널에서만 표시 |
| 15 | `/theme` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | 색상 테마 변경. 라이트/다크 변형, 색약자용(달톤화) 테마, 터미널 색상 팔레트를 사용하는 ANSI 테마 포함 |
| 16 | `/voice` | ![Config](https://img.shields.io/badge/Config-F39C12?style=flat) | 푸시-투-토크 음성 받아쓰기 전환. Claude.ai 계정 필요 |
| 17 | `/context` | ![Context](https://img.shields.io/badge/Context-8E44AD?style=flat) | 현재 컨텍스트 사용량을 색상 그리드로 시각화. 컨텍스트 과부하 도구, 메모리 팽창, 용량 경고에 대한 최적화 제안 표시 |
| 18 | `/cost` | ![Context](https://img.shields.io/badge/Context-8E44AD?style=flat) | 토큰 사용 통계 표시 |
| 19 | `/extra-usage` | ![Context](https://img.shields.io/badge/Context-8E44AD?style=flat) | 속도 제한에 도달했을 때 작업을 계속하기 위한 추가 사용량 설정 |
| 20 | `/insights` | ![Context](https://img.shields.io/badge/Context-8E44AD?style=flat) | Claude Code 세션을 분석하여 프로젝트 영역, 상호작용 패턴, 마찰 지점을 포함한 보고서 생성 |
| 21 | `/stats` | ![Context](https://img.shields.io/badge/Context-8E44AD?style=flat) | 일일 사용량, 세션 이력, 연속 사용 일수, 모델 선호도 시각화 |
| 22 | `/status` | ![Context](https://img.shields.io/badge/Context-8E44AD?style=flat) | 버전, 모델, 계정, 연결 상태를 보여주는 설정 인터페이스 열기. Claude가 응답 중에도 현재 응답 완료를 기다리지 않고 작동 |
| 23 | `/usage` | ![Context](https://img.shields.io/badge/Context-8E44AD?style=flat) | 플랜 사용 한도 및 속도 제한 상태 표시 |
| 24 | `/doctor` | ![Debug](https://img.shields.io/badge/Debug-E74C3C?style=flat) | Claude Code 설치 및 설정 진단 및 검증 |
| 25 | `/feedback [report]` | ![Debug](https://img.shields.io/badge/Debug-E74C3C?style=flat) | Claude Code에 대한 피드백 제출. 별칭: `/bug` |
| 26 | `/help` | ![Debug](https://img.shields.io/badge/Debug-E74C3C?style=flat) | 도움말 및 사용 가능한 명령어 표시 |
| 27 | `/powerup` | ![Debug](https://img.shields.io/badge/Debug-E74C3C?style=flat) | 애니메이션 데모가 있는 빠른 인터랙티브 레슨을 통해 Claude Code 기능 탐색 |
| 28 | `/release-notes` | ![Debug](https://img.shields.io/badge/Debug-E74C3C?style=flat) | 인터랙티브 버전 선택기에서 변경 이력 보기 |
| 29 | `/tasks` | ![Debug](https://img.shields.io/badge/Debug-E74C3C?style=flat) | 백그라운드 태스크 목록 및 관리. 별칭: `/bashes` |
| 30 | `/copy [N]` | ![Export](https://img.shields.io/badge/Export-7F8C8D?style=flat) | 마지막 어시스턴트 응답을 클립보드에 복사. N을 전달하면 N번째 최신 응답 복사 |
| 31 | `/export [filename]` | ![Export](https://img.shields.io/badge/Export-7F8C8D?style=flat) | 현재 대화를 일반 텍스트로 내보내기 |
| 32 | `/agents` | ![Extensions](https://img.shields.io/badge/Extensions-16A085?style=flat) | 에이전트 설정 관리 |
| 33 | `/chrome` | ![Extensions](https://img.shields.io/badge/Extensions-16A085?style=flat) | Chrome 내 Claude 설정 구성 |
| 34 | `/hooks` | ![Extensions](https://img.shields.io/badge/Extensions-16A085?style=flat) | 도구 이벤트에 대한 훅 설정 보기 |
| 35 | `/ide` | ![Extensions](https://img.shields.io/badge/Extensions-16A085?style=flat) | IDE 통합 관리 및 상태 표시 |
| 36 | `/mcp` | ![Extensions](https://img.shields.io/badge/Extensions-16A085?style=flat) | MCP 서버 연결 및 OAuth 인증 관리 |
| 37 | `/plugin` | ![Extensions](https://img.shields.io/badge/Extensions-16A085?style=flat) | Claude Code 플러그인 관리 |
| 38 | `/reload-plugins` | ![Extensions](https://img.shields.io/badge/Extensions-16A085?style=flat) | 재시작 없이 보류 중인 변경사항을 적용하기 위해 모든 활성 플러그인 다시 로드 |
| 39 | `/skills` | ![Extensions](https://img.shields.io/badge/Extensions-16A085?style=flat) | 사용 가능한 스킬 목록 표시 |
| 40 | `/memory` | ![Memory](https://img.shields.io/badge/Memory-3498DB?style=flat) | `CLAUDE.md` 메모리 파일 편집, 자동 메모리 활성화/비활성화, 자동 메모리 항목 보기 |
| 41 | `/effort [low\|medium\|high\|max\|auto]` | ![Model](https://img.shields.io/badge/Model-E67E22?style=flat) | 모델 노력 수준 설정 |
| 42 | `/fast [on\|off]` | ![Model](https://img.shields.io/badge/Model-E67E22?style=flat) | 빠른 모드 켜기/끄기 전환 |
| 43 | `/model [model]` | ![Model](https://img.shields.io/badge/Model-E67E22?style=flat) | AI 모델 선택 또는 변경 |
| 44 | `/passes` | ![Model](https://img.shields.io/badge/Model-E67E22?style=flat) | 친구에게 Claude Code 무료 1주일 공유. 계정 자격이 있는 경우에만 표시 |
| 45 | `/plan [description]` | ![Model](https://img.shields.io/badge/Model-E67E22?style=flat) | 프롬프트에서 직접 계획 모드로 전환. 선택적 설명을 전달하여 해당 태스크로 즉시 시작 가능 |
| 46 | `/ultraplan <prompt>` | ![Model](https://img.shields.io/badge/Model-E67E22?style=flat) | 울트라플랜 세션에서 계획 초안 작성, 브라우저에서 검토, 원격으로 실행하거나 터미널로 전송 |
| 47 | `/add-dir <path>` | ![Project](https://img.shields.io/badge/Project-27AE60?style=flat) | 현재 세션 중 파일 접근을 위한 작업 디렉토리 추가 |
| 48 | `/diff` | ![Project](https://img.shields.io/badge/Project-27AE60?style=flat) | 커밋되지 않은 변경사항과 턴별 diff를 보여주는 인터랙티브 diff 뷰어 열기 |
| 49 | `/init` | ![Project](https://img.shields.io/badge/Project-27AE60?style=flat) | `CLAUDE.md` 가이드로 프로젝트 초기화 |
| 50 | `/review` | ![Project](https://img.shields.io/badge/Project-27AE60?style=flat) | 더 이상 사용되지 않음. 대신 `code-review` 플러그인 설치: `claude plugin install code-review@claude-plugins-official` |
| 51 | `/security-review` | ![Project](https://img.shields.io/badge/Project-27AE60?style=flat) | 현재 브랜치의 보류 중인 변경사항에서 보안 취약점 분석 |
| 52 | `/autofix-pr [prompt]` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | 현재 브랜치의 PR을 감시하고 CI 실패 또는 리뷰어 댓글 시 수정사항을 푸시하는 웹 세션 생성 |
| 53 | `/desktop` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | Claude Code Desktop 앱에서 현재 세션 계속. macOS 및 Windows만. 별칭: `/app` |
| 54 | `/install-github-app` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | 저장소에 Claude GitHub Actions 앱 설정 |
| 55 | `/install-slack-app` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | Claude Slack 앱 설치. OAuth 흐름을 완료하기 위해 브라우저 열기 |
| 56 | `/mobile` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | Claude 모바일 앱 다운로드를 위한 QR 코드 표시. 별칭: `/ios`, `/android` |
| 57 | `/remote-control` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | claude.ai에서 원격 제어가 가능하도록 이 세션 활성화. 별칭: `/rc` |
| 58 | `/remote-env` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | `--remote`로 시작한 웹 세션의 기본 원격 환경 설정 |
| 59 | `/schedule [description]` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | 클라우드 예약 태스크 생성, 업데이트, 목록 조회, 실행 |
| 60 | `/teleport` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | 웹 Claude Code 세션을 이 터미널로 가져오기. 별칭: `/tp` |
| 61 | `/web-setup` | ![Remote](https://img.shields.io/badge/Remote-5D6D7E?style=flat) | 로컬 `gh` CLI 자격 증명을 사용하여 GitHub 계정을 웹 Claude Code에 연결 |
| 62 | `/branch [name]` | ![Session](https://img.shields.io/badge/Session-4A90D9?style=flat) | 이 지점에서 현재 대화의 브랜치 생성. 별칭: `/fork` |
| 63 | `/btw <question>` | ![Session](https://img.shields.io/badge/Session-4A90D9?style=flat) | 대화에 추가하지 않고 빠른 사이드 질문하기 |
| 64 | `/clear` | ![Session](https://img.shields.io/badge/Session-4A90D9?style=flat) | 대화 이력 초기화 및 컨텍스트 해제. 별칭: `/reset`, `/new` |
| 65 | `/compact [instructions]` | ![Session](https://img.shields.io/badge/Session-4A90D9?style=flat) | 선택적 초점 지침으로 대화 압축 |
| 66 | `/exit` | ![Session](https://img.shields.io/badge/Session-4A90D9?style=flat) | CLI 종료. 별칭: `/quit` |
| 67 | `/rename [name]` | ![Session](https://img.shields.io/badge/Session-4A90D9?style=flat) | 현재 세션 이름 바꾸기 및 프롬프트 바에 이름 표시 |
| 68 | `/resume [session]` | ![Session](https://img.shields.io/badge/Session-4A90D9?style=flat) | ID 또는 이름으로 대화 재개 또는 세션 선택기 열기. 별칭: `/continue` |
| 69 | `/rewind` | ![Session](https://img.shields.io/badge/Session-4A90D9?style=flat) | 대화 및/또는 코드를 이전 지점으로 되감기. 별칭: `/checkpoint` |

`/debug` 등 번들된 스킬도 슬래시-명령어 메뉴에 나타날 수 있지만, 이들은 내장 명령어가 아닙니다.

---

## 출처

- [Claude Code 슬래시 명령어](https://code.claude.com/docs/en/slash-commands)
- [Claude Code 인터랙티브 모드](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code 변경 이력](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
