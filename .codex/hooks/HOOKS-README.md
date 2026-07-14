# Codex hooks

이 디렉터리는 Samantha 저장소의 Codex 라이프사이클 음성 알림과 세션 시작 컨텍스트를 관리합니다.

## 구성

| 경로 | 역할 |
|---|---|
| `../hooks.json` | 프로젝트 훅 등록 |
| `scripts/hooks.py` | 훅 입력 처리, 컨텍스트 출력, 사운드 재생 |
| `config/hooks-config.json` | 팀 공유 활성화·로깅 설정 |
| `config/hooks-config.local.json` | 개인 재정의, Git 제외 |
| `sounds/<Event>/` | 이벤트별 WAV·MP3 파일 |
| `logs/hooks-log.jsonl` | 선택적 JSON Lines 로그, Git 제외 |

프로젝트 훅은 저장소가 Codex에서 신뢰된 경우에만 로드됩니다. 새 훅이나 변경된 훅은 Codex CLI의 `/hooks`에서 내용을 검토하고 신뢰해야 실행됩니다.

## 등록 이벤트

현재 음성 알림을 제공하는 이벤트는 5개입니다.

| 이벤트 | 동작 |
|---|---|
| `SessionStart` | 시간·작업 디렉터리·Git 브랜치·워킹트리 상태를 개발자 컨텍스트로 출력하고 사운드 재생 |
| `PreToolUse` | 도구 실행 전 사운드 재생 |
| `PostToolUse` | 도구 실행 후 사운드 재생 |
| `UserPromptSubmit` | 사용자 프롬프트 제출 시 사운드 재생 |
| `Stop` | 턴 종료 시 사운드 재생 |

`hooks.json`의 명령은 Codex가 하위 디렉터리에서 시작되더라도 동작하도록 `git rev-parse --show-toplevel`로 스크립트 경로를 계산합니다.

## 설정

팀 기본값은 `config/hooks-config.json`입니다.

```json
{
  "disableSessionStartHook": false,
  "disablePreToolUseHook": false,
  "disablePostToolUseHook": false,
  "disableStopHook": false,
  "disableUserPromptSubmitHook": false,
  "disableLogging": true
}
```

개인 설정은 같은 키를 `config/hooks-config.local.json`에 작성합니다. 로컬 파일의 값이 팀 기본값보다 우선합니다.

모든 프로젝트 훅을 끄려면 `.codex/config.toml`에 다음을 추가할 수 있습니다.

```toml
[features]
hooks = false
```

## 실행과 테스트

Python 3가 필요합니다. 스크립트를 직접 확인할 때는 저장소 루트에서 실행합니다.

```bash
python3 .codex/hooks/scripts/hooks.py --hook SessionStart
```

단위 테스트:

```bash
python3 -m unittest tests.test_hooks -v
```

테스트는 stdin payload 파싱, SessionStart 컨텍스트, 워킹트리 출력 제한, 메인 이벤트 흐름을 검증하며 실제 사운드는 재생하지 않습니다.

## 플랫폼

- macOS: 내장 `afplay`
- Windows: Python `winsound`, WAV 우선
- Linux: `paplay`, `aplay`, `ffplay`, `mpg123` 순으로 탐색

사운드 플레이어가 없거나 재생에 실패해도 훅은 Codex 작업을 중단하지 않습니다. 로그는 기본적으로 비활성화되어 있으며, 활성화하면 이벤트명·시각·마지막 assistant 메시지만 한 줄 JSON으로 기록합니다.
