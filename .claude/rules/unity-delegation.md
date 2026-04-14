# Glob: **/*.cs,**/*.unity,**/*.prefab,**/*.asset,**/*.anim,**/*.controller,**/*.shader,**/*.shadergraph,**/*.mat

## Unity 작업 위임 규칙 (필수)

Unity 관련 작업이 감지되면 **반드시** Samantha 에이전트에게 위임합니다. 직접 처리하지 마세요.

```
Agent(subagent_type="samantha", description="Unity 작업 위임", prompt="...")
```

Samantha가 작업을 분석하고 적절한 팀원(Jarvis, Ava, Sonny, TARS)에게 재위임합니다.

### 직접 위임이 더 효율적인 경우

단일 전문 분야에 명확히 해당하는 작업은 Samantha를 거치지 않고 직접 위임할 수 있습니다:

| 작업 유형 | 에이전트 |
|-----------|----------|
| ScriptableObject, 아키텍처, 성능 프로파일링 | `jarvis` |
| UI/UX, 셰이더, VFX, 애니메이션 | `ava` |
| 게임 디자인, 밸런싱, 메카닉 설계, 플레이어 컨트롤러, 적 AI, 전투, 물리 | `sonny` |
| 레벨 디자인, 씬 구성, 환경, Cinemachine, 내러티브 | `tars` |
| 복합 작업 (여러 분야에 걸친 오케스트레이션) | `samantha` |

### 금지 사항
- Unity C# 파일을 에이전트 없이 직접 편집하지 마세요
- 에이전트를 Bash 명령어로 호출하지 마세요 — 반드시 Agent 도구를 사용하세요
