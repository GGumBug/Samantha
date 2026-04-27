[← README로 돌아가기](../README.md)

# 브라우저 자동화 도구 선택 결정 규칙

Playwright MCP / Chrome DevTools MCP / Claude in Chrome 3자 비교. 사례 전체는 [reports/archive/claude-in-chrome-v-chrome-devtools-mcp.md](archive/claude-in-chrome-v-chrome-devtools-mcp.md)에 보존.

## 1. 결정 규칙

| When (상황) | Then (결정) |
|---|---|
| 성능 분석 + Network 디버깅 | Chrome DevTools MCP |
| 크로스 브라우저 E2E 테스트 | Playwright MCP |
| 로그인 상태 기반 수동 검증 | Claude in Chrome |
| CI/CD 파이프라인 자동화 | Playwright MCP |
| 콘솔 에러 + 스택 트레이스 분석 | Chrome DevTools MCP |
| 디자인 검증 (Figma vs 실제 출력) | Claude in Chrome |
| 토큰 효율 우선 | Playwright MCP (~13.7K, 컨텍스트 6.8%) |

## 2. 운영 체크리스트

- [ ] 크로스 브라우저 지원 필요 여부 확인 (필요 → Playwright)
- [ ] 성능 trace / Core Web Vitals 측정 필요 여부 (필요 → Chrome DevTools MCP)
- [ ] CI/CD headless 실행 요구 여부 (필요 → Playwright 또는 Chrome DevTools MCP)
- [ ] 로그인 세션 필요 여부 (필요 → Claude in Chrome)
- [ ] 토큰 사용량 제약 검토 (엄격 → Playwright 우선)
- [ ] 보안 정책 검토 (금융 / 민감 데이터 → Claude in Chrome 제외 권장)

## 3. 트레이드오프 매트릭스

| 항목 | Playwright MCP | Chrome DevTools MCP | Claude in Chrome |
|---|---|---|---|
| 토큰 효율 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 크로스 브라우저 | O (Chrome / Firefox / Safari) | X (Chrome only) | X (Chrome only) |
| 성능 분석 | 제한적 | 우수 | 없음 |
| CI/CD 통합 | 우수 | 우수 | 부적합 |
| 로그인 세션 | 셋업 필요 | 셋업 필요 | 네이티브 지원 |
| 보안 | 성숙 | 격리됨 | 23.6% 취약 사례 보고 |
| 비용 | Free | Free | 유료 Plan 필요 |

## 4. 참조

- [Chrome DevTools MCP — GitHub](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Playwright MCP — GitHub](https://github.com/microsoft/playwright-mcp)
- [Claude in Chrome](https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome)
- [원본 사례 — reports/archive/claude-in-chrome-v-chrome-devtools-mcp.md](archive/claude-in-chrome-v-chrome-devtools-mcp.md)
