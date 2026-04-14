# MCP 서버 모범 사례

![Last Updated](https://img.shields.io/badge/Last_Updated-Mar%2002%2C%202026%2012%3A30%20PM%20PKT-white?style=flat&labelColor=555)<br>
[![Implemented](https://img.shields.io/badge/Implemented-2ea44f?style=flat)](../.mcp.json)

MCP(Model Context Protocol) 서버는 Claude Code를 외부 도구, 데이터베이스, API에 연결하여 확장합니다. 이 가이드는 일상적인 사용을 위한 권장 서버와 설정 모범 사례를 다룹니다.

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

## 일상적인 사용을 위한 MCP 서버

> *"15개 MCP 서버를 과도하게 설치했지만 결국 4개만 매일 사용했습니다."* — [r/mcp](https://reddit.com/r/mcp/comments/1mj0fxs/) (682 추천)

| MCP 서버 | 기능 | 리소스 |
|----------|------|--------|
| [**Context7**](https://github.com/upstash/context7) | 최신 라이브러리 문서를 컨텍스트로 가져옴. 오래된 학습 데이터로 인한 환각 API 방지 | [Reddit: "코딩에 최고의 MCP"](https://reddit.com/r/mcp/comments/1qarjqm/) · [npm](https://www.npmjs.com/package/@upstash/context7-mcp) |
| [**Playwright**](https://github.com/microsoft/playwright-mcp) | 브라우저 자동화 — UI 기능을 자율적으로 구현, 테스트, 검증. 스크린샷, 탐색, 폼 테스트 | [Reddit: 프론트엔드에 필수](https://reddit.com/r/mcp/comments/1m59pk0/) · [문서](https://playwright.dev/) |
| [**Claude in Chrome**](https://github.com/nicobailon/claude-code-in-chrome-mcp) | Claude를 실제 Chrome 브라우저에 연결 — 콘솔, 네트워크, DOM 검사. 사용자가 실제로 보는 것 디버깅 | [Reddit: 디버깅에 "게임 체인저"](https://reddit.com/r/mcp/comments/1qarjqm/5_mcps_that_have_genuinely_made_me_10x_faster/nza0i7t/) · [비교 보고서](../reports/claude-in-chrome-v-chrome-devtools-mcp.md) |
| [**DeepWiki**](https://github.com/devanshusemwal/deepwiki-mcp) | 모든 GitHub 저장소의 구조화된 위키 스타일 문서 가져오기 — 아키텍처, API 표면, 관계 | [Reddit: "Context7와 함께 게이트웨이 뒤에 두기"](https://reddit.com/r/mcp/comments/1qarjqm/) |
| [**Excalidraw**](https://github.com/antonpk1/excalidraw-mcp-app) | 프롬프트에서 손으로 그린 Excalidraw 스케치로 아키텍처 다이어그램, 순서도, 시스템 설계 생성 | [GitHub](https://github.com/antonpk1/excalidraw-mcp-app) |

리서치 (Context7/DeepWiki) → 디버깅 (Playwright/Chrome) → 문서화 (Excalidraw)

---

## 설정

MCP 서버는 프로젝트 루트의 `.mcp.json` (프로젝트 범위) 또는 `~/.claude.json` (사용자 범위)에서 설정합니다.

### 서버 타입

| 타입 | 전송 | 예시 |
|------|------|------|
| **stdio** | 로컬 프로세스 실행 | `npx`, `python`, 바이너리 |
| **http** | 원격 URL 연결 | HTTP/SSE 엔드포인트 |

### 예시 `.mcp.json`

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    },
    "deepwiki": {
      "command": "npx",
      "args": ["-y", "deepwiki-mcp"]
    },
    "remote-api": {
      "type": "http",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

`.mcp.json`에 API 키를 커밋하는 대신 비밀을 위해 환경 변수 확장을 사용하세요:

```json
{
  "mcpServers": {
    "remote-api": {
      "type": "http",
      "url": "https://mcp.example.com/mcp?token=${MCP_API_TOKEN}"
    }
  }
}
```

### MCP 서버를 위한 설정

`.claude/settings.json`의 이 설정들은 MCP 서버 승인을 제어합니다:

| 키 | 타입 | 설명 |
|----|------|------|
| `enableAllProjectMcpServers` | boolean | 프롬프트 없이 모든 `.mcp.json` 서버를 자동 승인 |
| `enabledMcpjsonServers` | array | 자동 승인할 특정 서버 이름의 허용 목록 |
| `disabledMcpjsonServers` | array | 거부할 특정 서버 이름의 차단 목록 |

### MCP 도구에 대한 권한 규칙

MCP 도구는 권한 규칙에서 `mcp__<server>__<tool>` 명명 규칙을 따릅니다:

```json
{
  "permissions": {
    "allow": [
      "mcp__*",
      "mcp__context7__*",
      "mcp__playwright__browser_snapshot"
    ],
    "deny": [
      "mcp__dangerous-server__*"
    ]
  }
}
```

---

## MCP 범위

MCP 서버는 세 가지 레벨에서 정의할 수 있습니다:

| 범위 | 위치 | 목적 |
|------|------|------|
| **프로젝트** | `.mcp.json` (저장소 루트) | 팀 공유 서버, git에 커밋 |
| **사용자** | `~/.claude.json` (`mcpServers` 키) | 모든 프로젝트에 걸친 개인 서버 |
| **서브에이전트** | 에이전트 프론트매터 (`mcpServers` 필드) | 특정 서브에이전트에 범위가 지정된 서버 |

우선순위: 서브에이전트 > 프로젝트 > 사용자

---

## 출처

- [MCP 서버 — Claude Code 공식 문서](https://code.claude.com/docs/en/mcp)
- [Model Context Protocol 명세](https://modelcontextprotocol.io/)
- [나를 정말로 10배 빠르게 만든 5개의 MCP — r/mcp](https://reddit.com/r/mcp/comments/1qarjqm/)
- [MCP 서버 과부하 토론 — r/mcp](https://reddit.com/r/mcp/comments/1mj0fxs/)
