# 서브에이전트 구현

![Last Updated](https://img.shields.io/badge/Last_Updated-Mar_02%2C_2026_07%3A59_PM_PKT-white?style=flat&labelColor=555)

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

<a href="#weather-agent"><img src="../!/tags/implemented-hd.svg" alt="Implemented"></a>

날씨 에이전트는 이 저장소에서 **명령어 → 에이전트 → 스킬** 아키텍처 패턴의 예시로 구현되어 있으며, 두 가지 별개의 스킬 패턴을 보여줍니다.

---

## 날씨 에이전트

**파일**: [`.claude/agents/weather-agent.md`](../.claude/agents/weather-agent.md)

```yaml
---
name: weather-agent
description: 두바이(UAE)의 날씨 데이터를 가져와야 할 때 PROACTIVELY 이 에이전트를 사용합니다.
  이 에이전트는 사전 로드된 weather-fetcher 스킬을 사용해
  Open-Meteo에서 실시간 온도를 가져옵니다.
tools: WebFetch, Read, Write, Edit
model: sonnet
color: green
maxTurns: 5
permissionMode: acceptEdits
memory: project
skills:
  - weather-fetcher
---

# 날씨 에이전트

당신은 두바이(UAE)의 날씨 데이터를 가져오는 전문 날씨 에이전트입니다.

## 작업

사전 로드된 스킬의 지침에 따라 날씨 워크플로우를 실행합니다:

1. **가져오기**: `weather-fetcher` 스킬 지침에 따라
   현재 온도를 가져옵니다
2. **보고**: 온도 값과 단위를 호출자에게 반환합니다
3. **메모리**: 이력 추적을 위해 에이전트 메모리를 업데이트합니다

...
```

에이전트에는 Open-Meteo에서 가져오는 지침을 제공하는 하나의 사전 로드된 스킬(`weather-fetcher`)이 있습니다. 온도 값과 단위를 호출하는 명령어에 반환합니다.

---

## ![사용 방법](../!/tags/how-to-use.svg)

```bash
$ claude
> 두바이 날씨가 어때?
```

---

## ![구현 방법](../!/tags/how-to-implement.svg)

`/agents` 명령어를 사용하여 에이전트를 만들 수 있습니다:
```bash
$ claude
> /agents
```

또는 Claude에게 하나 만들어달라고 요청하세요 — YAML 프론트매터와 본문이 있는 마크다운 파일을 `.claude/agents/<name>.md`에 생성해드립니다

---

<a href="https://github.com/shanraisshan/claude-code-best-practice#orchestration-workflow"><img src="../!/tags/orchestration-workflow-hd.svg" alt="Orchestration Workflow"></a>

날씨 에이전트는 명령어 → 에이전트 → 스킬 오케스트레이션 패턴의 **에이전트**입니다. `/weather-orchestrator` 명령어로부터 워크플로우를 받아 사전 로드된 스킬(`weather-fetcher`)을 사용하여 온도를 가져옵니다. 명령어는 시각적 출력을 생성하기 위해 독립 실행형 `weather-svg-creator` 스킬을 호출합니다.

<p align="center">
  <img src="../orchestration-workflow/orchestration-workflow.svg" alt="명령어 스킬 에이전트 아키텍처 흐름" width="100%">
</p>

| 컴포넌트 | 역할 | 이 저장소 |
|---------|------|---------|
| **명령어** | 진입점, 사용자 상호작용 | [`/weather-orchestrator`](../.claude/commands/weather-orchestrator.md) |
| **에이전트** | 사전 로드된 스킬로 데이터 가져오기 (에이전트 스킬) | [`weather-agent`](../.claude/agents/weather-agent.md)와 [`weather-fetcher`](../.claude/skills/weather-fetcher/SKILL.md) |
| **스킬** | 독립적으로 출력 생성 (스킬) | [`weather-svg-creator`](../.claude/skills/weather-svg-creator/SKILL.md) |
