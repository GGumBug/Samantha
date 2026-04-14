# 명령어 구현

![Last Updated](https://img.shields.io/badge/Last_Updated-Mar_02%2C_2026-white?style=flat&labelColor=555)

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

<a href="#weather-orchestrator"><img src="../!/tags/implemented-hd.svg" alt="Implemented"></a>

날씨 오케스트레이터 명령어는 이 저장소에서 **명령어 → 에이전트 → 스킬** 아키텍처 패턴의 진입점으로 구현되어 있으며, 명령어가 다단계 워크플로우를 어떻게 오케스트레이션하는지 보여줍니다.

---

## 날씨 오케스트레이터

**파일**: [`.claude/commands/weather-orchestrator.md`](../.claude/commands/weather-orchestrator.md)

```yaml
---
description: 두바이 날씨 데이터를 가져와 SVG 날씨 카드를 생성합니다
model: haiku
---

# 날씨 오케스트레이터 명령어

두바이(UAE)의 현재 온도를 가져와 시각적인 SVG 날씨 카드를 생성합니다.

## 워크플로우

### 1단계: 사용자 선호도 확인
AskUserQuestion 도구를 사용하여 사용자에게 섭씨 또는 화씨 중
어느 단위를 원하는지 묻습니다.

### 2단계: 날씨 데이터 가져오기
Agent 도구를 사용하여 날씨 에이전트를 호출합니다:
- subagent_type: weather-agent
- prompt: 두바이(UAE)의 현재 온도를 [unit]으로 가져오세요...

### 3단계: SVG 날씨 카드 생성
Skill 도구를 사용하여 weather-svg-creator 스킬을 호출합니다:
- skill: weather-svg-creator

...
```

명령어는 전체 워크플로우를 오케스트레이션합니다: 사용자에게 온도 단위 선호도를 묻고, Agent 도구를 통해 `weather-agent`를 호출하고, Skill 도구를 통해 `weather-svg-creator` 스킬을 호출합니다.

---

## ![사용 방법](../!/tags/how-to-use.svg)

```bash
$ claude
> /weather-orchestrator
```

---

## ![구현 방법](../!/tags/how-to-implement.svg)

Claude에게 하나 만들어달라고 요청하세요 — YAML 프론트매터와 본문이 있는 마크다운 파일을 `.claude/commands/<name>.md`에 생성해드립니다

---

<a href="https://github.com/shanraisshan/claude-code-best-practice#orchestration-workflow"><img src="../!/tags/orchestration-workflow-hd.svg" alt="Orchestration Workflow"></a>

날씨 오케스트레이터는 명령어 → 에이전트 → 스킬 오케스트레이션 패턴의 **명령어**입니다. 진입점 역할을 합니다 — 사용자 상호작용(온도 단위 선호도) 처리, `weather-agent`에 데이터 가져오기 위임, 시각적 출력을 위한 `weather-svg-creator` 스킬 호출.

<p align="center">
  <img src="../orchestration-workflow/orchestration-workflow.svg" alt="명령어 스킬 에이전트 아키텍처 흐름" width="100%">
</p>

| 컴포넌트 | 역할 | 이 저장소 |
|---------|------|---------|
| **명령어** | 진입점, 사용자 상호작용 | [`/weather-orchestrator`](../.claude/commands/weather-orchestrator.md) |
| **에이전트** | 사전 로드된 스킬로 데이터 가져오기 (에이전트 스킬) | [`weather-agent`](../.claude/agents/weather-agent.md)와 [`weather-fetcher`](../.claude/skills/weather-fetcher/SKILL.md) |
| **스킬** | 독립적으로 출력 생성 (스킬) | [`weather-svg-creator`](../.claude/skills/weather-svg-creator/SKILL.md) |
