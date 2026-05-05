# Glob: **/*.{ts,tsx,jsx,js,mjs,cjs,css,scss},**/package.json,**/tsconfig.json,**/next.config.*,**/tailwind.config.*,**/components.json,**/eslint.config.*,**/postcss.config.*

## 웹 프로젝트 작업 위임 규칙 (필수)

웹 프로젝트(Next.js/React/TS) 관련 작업이 감지되면 **반드시** Samantha 에이전트에게 위임합니다. 직접 처리하지 마세요.

```
Agent(subagent_type="samantha", description="웹 작업 위임", prompt="...")
```

Samantha가 작업을 분석하고 적절한 팀원(Joi, Friday, HAL, GERTY)에게 재위임합니다.

### 직접 위임이 더 효율적인 경우

단일 전문 분야에 명확히 해당하는 작업은 Samantha를 거치지 않고 직접 위임할 수 있습니다:

| 작업 유형 | 에이전트 |
|-----------|----------|
| shadcn/ui, Tailwind, 디자인 시스템, 접근성, 반응형, 다크/라이트 테마, i18n | `joi` |
| Next.js App Router, 클라이언트/서버 컴포넌트, 라우팅, 상태 관리, zod 폼, TanStack Table | `friday` |
| API 라우트, SQLite/DB 스키마, 파일 업로드, PDF 파이프라인, 외부 데이터 통합 | `hal` |
| Gemini/OpenAI 클라이언트, 프롬프트 엔지니어링, AI 응답 파싱, AI 기능 설계 | `gerty` |
| 복합 작업 (여러 분야에 걸친 오케스트레이션) | `samantha` |

### 분야 경계가 모호한 경우

- **AI 결과를 표시하는 UI**: AI 부분(GERTY) + UI 부분(Joi) 병렬
- **새 페이지 + API + DB**: Friday(페이지/라우팅) + HAL(API/DB) 순차 또는 병렬
- **새 폼 화면**: Joi(폼 컴포넌트 시각) + Friday(zod 검증·제출 로직) + HAL(저장 API) 협업

### 금지 사항
- 웹 코드 파일을 에이전트 없이 직접 편집하지 마세요
- 에이전트를 Bash 명령어로 호출하지 마세요 — 반드시 Agent 도구를 사용하세요
- API 키, 시크릿을 코드에 직접 작성하지 마세요 (HAL의 영역)
