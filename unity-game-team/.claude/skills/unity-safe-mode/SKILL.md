---
name: unity-safe-mode
description: Unity 프로젝트에서 위험한 파일 조작을 차단하는 온디맨드 안전 훅 스킬. .meta 파일 삭제, Assets 폴더 외부 bash 수정, ProjectSettings 변경을 사전 차단합니다. 중요한 파일을 건드리기 전 /unity-safe-mode 로 활성화하세요.
user-invocable: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: python3 -c "
import sys, json, os
data = json.load(sys.stdin)
cmd = data.get('tool_input', {}).get('command', '')
dangerous = [
  ('.meta', 'Unity .meta 파일 삭제/이동은 에셋 참조를 깨뜨립니다'),
  ('ProjectSettings/', 'ProjectSettings 직접 수정은 프로젝트 설정을 손상시킬 수 있습니다'),
  ('rm -rf', '재귀 삭제는 Unity 프로젝트에서 금지됩니다'),
]
for pattern, reason in dangerous:
  if pattern in cmd:
    print(json.dumps({'decision': 'block', 'reason': f'[unity-safe-mode] {reason}. Unity Editor에서 수행하세요.'}))
    sys.exit(0)
print(json.dumps({'decision': 'approve'}))
"
          timeout: 3000
---

# Unity Safe Mode — 프로젝트 보호 훅

이 스킬은 Unity 프로젝트에서 돌이킬 수 없는 실수를 방지하는 **온디맨드 훅**입니다.

*Thariq (Anthropic) 권장 패턴: "On-Demand Hooks — 위험한 작업에만 선택적으로 훅을 적용"*

## 활성화 방법

```
/unity-safe-mode
```

세션 중 이 스킬을 호출하면 남은 세션 동안 아래 보호 규칙이 자동 적용됩니다.

## 보호 규칙

| 패턴 | 차단 이유 |
|------|---------|
| `*.meta` 파일 bash 조작 | GUID 포함 — 삭제 시 에셋 참조 전체 깨짐 |
| `ProjectSettings/` bash 직접 수정 | 빌드, 입력, 물리 설정 손상 위험 |
| `rm -rf` | 재귀 삭제로 에셋 폴더 날아갈 위험 |

## 언제 사용하나

- 대규모 폴더 구조 리팩토링 전
- 에셋 이름 변경/이동 작업 전
- 팀원이 처음으로 Unity 프로젝트를 다룰 때

## 주의사항

- 이 훅은 **세션 단위**로만 활성화됩니다 (재시작 시 비활성)
- Unity Editor에서 직접 파일 이동은 허용됨 (bash를 통한 조작만 차단)
- 차단된 작업이 꼭 필요하다면 스킬 없이 직접 수행 가능
