# AGENTS.md

이 저장소의 작업 규칙 SSOT는 [CLAUDE.md](CLAUDE.md)와 [.claude/](.claude/)다.
AGENTS.md는 그 규약 이름을 읽는 다른 도구를 위한 얇은 포인터로만 남긴다.

## 어디를 읽어야 하는가

| 찾는 것 | 파일 |
|---|---|
| 저장소 작업 규칙, Unity 라우팅 표 | [CLAUDE.md](CLAUDE.md) |
| SOLID·SSOT 헌법 | [.claude/rules/engineering-constitution.md](.claude/rules/engineering-constitution.md) |
| Unity 위임과 범위 보존, 라이브 에디터 우선 | [.claude/rules/unity-delegation.md](.claude/rules/unity-delegation.md) |
| 평가 주도 검증, 두 겹 검증 루프 | [.claude/rules/evaluation.md](.claude/rules/evaluation.md) |
| 주석·커밋·문서 산문 규칙 | [.claude/rules/prose-style.md](.claude/rules/prose-style.md) |
| 전문가 에이전트 정의 | [.claude/agents/](.claude/agents/) |
| 스킬과 워크플로 명령어 | [.claude/skills/](.claude/skills/) · [.claude/commands/](.claude/commands/) |
| 실패에서 일반화한 패턴 | [best-practice/](best-practice/) |

## 왜 내용이 여기 없는가

2026-09-16 이전에는 Codex용 규칙 전문이 이 파일에, Claude Code용 전문이 CLAUDE.md에
따로 있었다. 두 벌은 갈라졌다. `hooks.py`가 서로 다른 구현으로 표류했고, 같은 이름의
스킬 둘이 다른 내용을 들고 있었으며, 테스트가 무는 쪽과 실제로 실행되는 쪽이 어긋났다.

같은 규칙을 두 파일에 적으면 한쪽만 고쳐지는 날이 반드시 온다. 그래서 전문은 한 곳에
두고 이 파일은 그곳을 가리키기만 한다. 걷어낸 Codex 자산의 이력은 git에 남아 있다.
