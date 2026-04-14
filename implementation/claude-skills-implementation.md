# 스킬 구현

![Last Updated](https://img.shields.io/badge/Last_Updated-Mar_02%2C_2026-white?style=flat&labelColor=555)

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

<a href="#weather-svg-creator"><img src="../!/tags/implemented-hd.svg" alt="Implemented"></a>

이 저장소에는 **명령어 → 에이전트 → 스킬** 아키텍처 패턴의 일부로 두 가지 스킬이 구현되어 있으며, **에이전트 스킬**(사전 로드됨)과 **스킬**(직접 호출됨)이라는 두 가지 별개의 스킬 호출 패턴을 보여줍니다.

---

## 날씨 SVG 생성기 (스킬)

**파일**: [`.claude/skills/weather-svg-creator/SKILL.md`](../.claude/skills/weather-svg-creator/SKILL.md)

```yaml
---
name: weather-svg-creator
description: 두바이의 현재 온도를 보여주는 SVG 날씨 카드를 생성합니다.
  SVG를 orchestration-workflow/weather.svg에 저장하고
  orchestration-workflow/output.md를 업데이트합니다.
---

# 날씨 SVG 생성기 스킬

이 스킬은 시각적 SVG 날씨 카드를 생성하고 출력 파일을 작성합니다.

## 작업
두바이(UAE)의 온도를 표시하는 SVG 날씨 카드를 생성하고
요약과 함께 출력 파일에 작성합니다.

## 지침
호출 컨텍스트에서 온도 값과 단위(섭씨 또는 화씨)를 받습니다.

### 1. SVG 날씨 카드 생성
깔끔한 SVG 날씨 카드를 생성합니다...

### 2. SVG 파일 작성
SVG 내용을 `orchestration-workflow/weather.svg`에 작성합니다.

### 3. 출력 요약 작성
`orchestration-workflow/output.md`에 작성합니다...

...
```

이것은 **스킬** — 명령어가 Skill 도구를 통해 직접 호출합니다. 대화 컨텍스트에서 온도 데이터를 받아 SVG 날씨 카드와 출력 요약을 생성합니다.

---

## 날씨 가져오기 (에이전트 스킬)

**파일**: [`.claude/skills/weather-fetcher/SKILL.md`](../.claude/skills/weather-fetcher/SKILL.md)

```yaml
---
name: weather-fetcher
description: 두바이(UAE)의 현재 기상 온도 데이터를
  Open-Meteo API에서 가져오는 지침
user-invocable: false
---

# 날씨 가져오기 스킬

이 스킬은 현재 날씨 데이터를 가져오는 지침을 제공합니다.

## 작업
두바이(UAE)의 현재 온도를 요청된 단위(섭씨 또는 화씨)로 가져옵니다.

## 지침
1. 날씨 데이터 가져오기: WebFetch 도구를 사용하여 현재 날씨 데이터를 가져옵니다
   - 섭씨 URL: https://api.open-meteo.com/v1/forecast?latitude=25.2048&longitude=55.2708&current=temperature_2m&temperature_unit=celsius
   - 화씨 URL: https://api.open-meteo.com/v1/forecast?latitude=25.2048&longitude=55.2708&current=temperature_2m&temperature_unit=fahrenheit
2. 온도 추출: JSON 응답에서 `current.temperature_2m` 추출
3. 결과 반환: 온도 값과 단위를 명확하게 반환합니다.

...
```

이것은 **에이전트 스킬** — `skills:` 프론트매터 필드를 통해 시작 시 `weather-agent`에 사전 로드됩니다. 직접 호출되지 않고 에이전트 컨텍스트에 주입된 도메인 지식으로 역할합니다. `/` 명령어 메뉴에서 숨기는 `user-invocable: false`를 참고하세요.

---

## 두 가지 스킬 패턴

| 패턴 | 호출 | 예시 | 주요 차이점 |
|------|------|------|------------|
| **스킬** | `Skill(skill: "name")` | `weather-svg-creator` | Skill 도구를 통해 직접 호출 |
| **에이전트 스킬** | `skills:` 필드를 통해 사전 로드 | `weather-fetcher` | 시작 시 에이전트 컨텍스트에 주입 |

---

## ![사용 방법](../!/tags/how-to-use.svg)

**스킬** — 슬래시 명령어로 직접 호출:
```bash
$ claude
> /weather-svg-creator
```

---

## ![구현 방법](../!/tags/how-to-implement.svg)

Claude에게 하나 만들어달라고 요청하세요 — YAML 프론트매터와 본문이 있는 마크다운 파일을 `.claude/skills/my-skill/SKILL.md`에 생성해드립니다

# 나의 스킬

스킬의 역할에 대한 지침.
```
