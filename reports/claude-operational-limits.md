[← README로 돌아가기](../README.md)

# Claude 운영 한계 & 도구 결정 규칙

토큰 사용 한도, 도구 호출 패턴, 모노레포 스킬 활용은 비용·성능에 직접 영향을 준다. 사례 전체는 [reports/archive/](archive/)에 보존, 본 문서는 **결정 규칙 + 체크리스트 + 매트릭스**만 다룬다.

## 1. 결정 규칙

| When (상황) | Then (결정) |
|---|---|
| 토큰 절약이 최우선 | Tool Search Tool + PTC 병렬 — 도구 정의 ~85% 삭감, 라운드트립 ~37% 단축 |
| 웹 검색 / 페치 결과가 부풀어 있음 | Dynamic Filtering — Python 사전 필터로 입력 토큰 ~24% 절감 |
| 3 개 이상 도구 순차 호출 필요 | Programmatic Tool Calling (PTC) — 라운드트립 1회로 통합 |
| 단일 도구 호출 또는 즉시 응답 | 전통적 직접 호출 유지 (PTC 오버헤드 회피) |
| Rate limit 도달 | `/extra-usage` 활성화 — 표준 API 요금으로 계속 (5시간 리셋) |
| Fast 모드 사용 중 | 항상 추가 사용량 청구 발생 — 구독 여유분 무관 |
| 모노레포 + 팀별 다른 스택 | 패키지별 `.claude/skills/<pkg>-<workflow>/` 배치 — 자동 발견 활용 |
| 스킬 정의가 컨텍스트 10% 초과 | `ENABLE_TOOL_SEARCH=auto:N` — Tool Search 로 지연 로드 |
| 도구 파라미터 오류율 높음 | `input_examples` 추가 — 정확도 72% → 90% |
| MCP 도구 50개 이상, 빈도 불균형 | 상위 3-5개 즉시 로드, 나머지 `defer_loading: true` |

## 2. 운영 체크리스트

### 토큰 절약 (전 / 중 / 후)
- [ ] 세션 시작: `/usage` 로 남은 한도 확인
- [ ] 도구 로드 전: 정의가 10K 초과면 Tool Search Tool 활성화
- [ ] PTC 선택: 3+ 도구 순차이면 코드 한 번으로 통합
- [ ] 웹 검색: Dynamic Filtering 코드로 사전 필터링
- [ ] 세션 종료: `/cost` (API) 또는 `/usage` (구독) 로 사용량 검토

### 도구 호출 패턴
- [ ] 1-2 도구 + 빠른 응답 → direct
- [ ] 3+ 도구 + 데이터 처리 → `allowed_callers: ["code_execution_20250825"]` (PTC)
- [ ] direct + PTC 둘 다 허용 시 명확성이 떨어짐 — 한쪽 고정 권장
- [ ] PTC 결과에 외부 데이터 주입되면 코드 인젝션 위험 검토

### 모노레포 스킬
- [ ] 공유 워크플로 → 루트 `.claude/skills/`
- [ ] 패키지별 → `packages/<pkg>/.claude/skills/<pkg>-<workflow>/`
- [ ] 위험한 자동 호출 → `disable-model-invocation: true`
- [ ] 스킬 description 은 간결하게 (컨텍스트 예산 ~15K 자)
- [ ] 명명 규칙 `<package>-<workflow>` 으로 충돌 방지

## 3. 트레이드오프 매트릭스

### 도구 호출 패턴

| 패턴 | 대기시간 | 토큰 사용 | 컨텍스트 | 구현 복잡도 | 추천 |
|---|---|---|---|---|---|
| Direct (전통) | 낮음 | 높음 (라운드트립) | 높음 | 낮음 | 1-2 도구, 빠른 응답 |
| PTC | 높음 (추론) | ~37% 절감 | 낮음 | 높음 | 3+ 도구 배치 |
| Sub-agent | 중간 | 가변 | 가변 | 중간 | 독립·병렬 작업 |
| Skill | 빠름 (캐시) | 낮음 (지연 로드) | 낮음 (description) | 낮음 | 반복 작업, 자동 호출 |

### Rate limit 대응

| 상황 | 즉시 대응 | 중기 조치 |
|---|---|---|
| 5시간 한도 도달 | `/extra-usage` 활성 (표준 API 요금) | 월 지출 한도 설정 |
| Fast 모드 사용 | 항상 추가 사용량 — 비용 예산에 포함 | 일반 모드 vs Fast 비교로 결정 |
| API 키 사용자 | `--max-budget-usd <금액>` 사전 차단 | `--max-turns <N>` 으로 턴 제한 |

## 4. 참조

- [Anthropic Engineering: Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) — PTC, Dynamic Filtering, Tool Search
- [Claude Code Skills](https://code.claude.com/docs/en/skills) — 자동 발견, 모노레포 설계
- [Extra Usage for paid plans](https://support.claude.com/en/articles/12429409-extra-usage-for-paid-claude-plans) — Rate limit 대응
- [원본 사례 — reports/archive/claude-usage-and-rate-limits.md](archive/claude-usage-and-rate-limits.md)
- [원본 사례 — reports/archive/claude-advanced-tool-use.md](archive/claude-advanced-tool-use.md)
- [원본 사례 — reports/archive/claude-skills-for-larger-mono-repos.md](archive/claude-skills-for-larger-mono-repos.md)
