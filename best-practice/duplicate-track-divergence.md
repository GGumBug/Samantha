[← README로 돌아가기](../README.md)

# 갈라진 두 트랙 — 지우기 전에 무엇이 검증되는지 먼저 본다

같은 파일이 두 경로에 있을 때 비싼 것은 중복 자체가 아니다. **검증하는 쪽과 실제로 실행되는 쪽이
어긋나는 것**이 먼저 오고, 그 어긋남은 초록 화면 뒤에 숨는다. 이 저장소가 `.codex/`와 `.claude/`
두 트랙을 두 달 유지하다 2026-09-16에 한 트랙으로 모으며 실측했다.

## 1. 시험이 보던 쪽은 실행되지 않는 쪽이었다

| | 검증 대상 | 실행 대상 |
|---|---|---|
| `hooks.py` | `tests/test_hooks.py`가 가리킨 `.codex` 사본 | `.claude/hooks/scripts/hooks.py` |

전날 `.claude` 쪽에 넣은 수정이 **시험 0건 아래에서** 커밋됐다. 그동안 시험은 내내 초록이었고, 그
초록의 근거는 아무도 실행하지 않는 사본이었다. 두 이름이 같아서 **초록이 어느 파일의 것인지 아무도
묻지 않았다**.

## 2. 멈춘 트랙이 죽은 트랙은 아니다

두 `hooks.py`는 사본이 아니라 **갈라진 두 구현**이었다. 396줄 대 664줄, diff 577줄이고 각자에만 있는
함수가 있었다(`.codex`의 `load_config`·`get_config_value`, `.claude`의 `scale_wav_to_memory`·
`detect_bash_command_sound` 등). "두 달 커밋 없음"을 죽음의 증거로 읽고 지웠으면 기능을 조용히 잃었다.

정지 기간은 **누가 그 파일을 읽는가**에 대해 아무것도 말하지 않는다. 훅·CI 설정·에디터 연동처럼
사람이 직접 부르지 않는 진입점일수록 조용하다.

## 3. 지우기 전 판별 질문 둘

1. **시험이 가리키는 쪽은 어디인가.** 테스트·러너·CI 설정에서 경로를 grep 해 실행 진입점
   (`settings.json`의 훅 등록 등)과 대조한다. 둘이 같은 파일이 아니면 그것이 1순위 결함이다.
2. **각자에만 있는 것이 무엇인가.** `diff`로 대조해 한쪽에만 있는 함수·분기를 목록화한다. 목록이
   비어야 "사본"이고, 비지 않으면 할 일은 삭제가 아니라 **합류**다.

```bash
grep -rn "hooks.py" tests/ .claude/settings.json          # 검증 쪽과 실행 쪽 경로
diff <(git show HEAD:A/x.py) <(git show HEAD:B/x.py)      # 내용 갈림
diff <(grep -o "^def [a-z_]*" A/x.py) <(grep -o "^def [a-z_]*" B/x.py)   # 각자에만 있는 것
```

## 4. 통합 후 고정

- 시험 대상을 **실행 경로로** 고정하고 그 경로를 한 곳에만 적는다. 두 곳에 적으면 다시 갈라진다
- 남길 트랙 하나만 두고 나머지는 이력에 맡긴다. git이 사본을 보관하므로 저장소에 둘 이유가 없다
- 트랙을 걷어낸 사실을 적은 **현황 문장도 함께 갱신**한다([../.claude/rules/markdown-docs.md](../.claude/rules/markdown-docs.md))

## 종료 게이트

- [ ] 같은 이름의 파일이 두 경로에 있는가. 있으면 시험이 가리키는 경로를 grep 으로 확인했는가
- [ ] 검증 대상과 실행 진입점이 **같은 파일**인가
- [ ] 지우기 전 `diff`로 각자에만 있는 것을 목록화했는가
- [ ] 통합 후 시험 대상 경로가 한 곳에만 적혀 있는가

## 관련 문서

- [hand-listed-roster-decay.md](hand-listed-roster-decay.md) — 명부가 둘로 갈라지면 반드시 어긋난다(요구·공급 판)
- [stale-artifact-false-signal.md](stale-artifact-false-signal.md) — 판정자가 거짓말하는 조건을 함께 확인
- [.claude/rules/evaluation.md](../.claude/rules/evaluation.md) — 미실행 산출물은 "컴파일 미검증"으로 취급
