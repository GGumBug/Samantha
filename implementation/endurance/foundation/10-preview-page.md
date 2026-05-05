[← README.md로 돌아가기](README.md)

# 10 — Preview Page (`/dev/preview` 시각 검증)

**위임**: Friday | **위치**: `src/app/dev/preview/page.tsx` | **의존**: 01~09 모두

## Purpose

Phase 0의 통합 검증 페이지. **모든 신규 토큰·차트·게이지·테이블·sync 버튼**을 한 화면에서 시각적으로 확인. 본 페이지는 production 빌드에 포함되지 않거나(env flag) 라우트 가드로 막아 사용자에게 노출 안 함.

이 페이지가 통과하면 Phase 0 완료. Phase 1(`/dashboard`)는 본 페이지의 위젯들을 의미적 레이아웃으로 재배치하기만 하면 됨.

## 의존성

- **사용하는 자산**: 01~09 전부
- **이걸 사용하는 자산**: 없음 (개발자·시니어 검증 전용)

## 페이지 구조 (섹션별)

### Section 1 — Color Palette
디자인 시스템 모든 색 토큰 + 신규 4색을 시각화:
- Brand & Accent (라벤더 4색)
- Surface ladder (canvas → 1 → 2 → 3 → 4 + hairline 3종)
- Ink ladder (4단계)
- Semantic (success / warning / danger / overlay)
- Heatmap (positive/negative base)

각 색은 large swatch + 토큰 이름 + hex 표시.

### Section 2 — Typography
- display-xl ~ caption 13단계 모두 한국어·영어 혼합 샘플
- Pretendard weight 100~900 한 글자씩 시각화 (variable 동작 확인)
- 음수 트래킹 적용 확인 (display-xl `-2.5px`)

### Section 3 — Components (07 토큰 7종)
- `data-table` — 5행 데모 (정렬·hover·selected 상태)
- `chart-container` — 4종 차트 (LineChart, AreaChart, BarChart, Sparkline)
- `gauge-meter` — 3 사이즈 (sm/md/lg) × 4 구간 색
- `heatmap-cell` — 6×4 그리드 (-10% ~ +20% 분포)
- `metric-card` — 6개 (KOSPI / NASDAQ / 외국인 수급 / EPS / VIX / Term Spread)
- `market-toggle` — 3-state segmented control (KR / US / 양쪽)
- `trigger-badge` — 3 상태 (미발동 / 활성 / 음소거)

### Section 4 — Buttons & Forms
기존 디자인 시스템 컴포넌트 유지 검증:
- button-primary / secondary / tertiary / inverse 4종
- text-input + focus 상태
- pricing-tab default/selected

### Section 5 — Data Layer Smoke Test
실제 데이터 호출 결과 표시:
- `fetchSecurity('NVDA')` → Security 객체 표시
- `fetchPricesDaily('005930.KS', '2025-04-01', '2025-04-30')` → 30개 OHLCV → LineChart
- `getFxRate('2025-05-01', 'USD/KRW')` → 환율 표시
- `fetchMacroIndex('KR', '2025-05-01')` → MacroSnapshot 카드

호출 실패 시 `Result.error` 코드를 trigger-badge로 가시화 — 모든 실패 케이스가 silent fail 하지 않는지 검증.

### Section 6 — AI Smoke Test
- 버튼: "Generate sample SWOT for NVDA"
- 클릭 시 `getAiClient().generate({ prompt: buildSwotPrompt(...), schema: SwotResponseSchema })`
- 결과 SwotAnalysis 4사분면을 surface-1 카드로 표시
- 응답 zod 통과 / 실패 시 error 표시

### Section 7 — Sync Trigger
- 버튼: "Run syncAll()"
- 클릭 시 `/api/sync` POST
- SyncReport를 표로 표시 (각 step + duration + ok/error)
- 두 번 누르면 두 번째 호출은 외부 API 0건 (캐시 검증)

## Implementation Notes

### 라우트 가드

```typescript
// src/app/dev/preview/page.tsx
import { notFound } from 'next/navigation';

export default function PreviewPage() {
  if (process.env.NODE_ENV === 'production' && !process.env.ENABLE_DEV_PREVIEW) {
    notFound();
  }
  return <PreviewContent />;
}
```

production 환경에서는 404로 차단. 로컬·개발 환경에서만 접근 가능.

### 페이지 구조

```typescript
export default function PreviewContent() {
  return (
    <main className="mx-auto max-w-[1280px] px-6 py-section">
      <Section1Colors />
      <Section2Typography />
      <Section3Components />
      <Section4ButtonsForms />
      <Section5DataLayer />
      <Section6AI />
      <Section7Sync />
    </main>
  );
}
```

각 섹션은 독립 컴포넌트. 한 섹션 깨져도 나머지 정상 렌더 (헌법 §0-1 Step 3 에러 격리).

### 시각 검증 자기 평가 금지

본 페이지는 **사용자(또는 시니어 리뷰어)가 직접 눈으로 확인**해야 함. AI가 "잘 보인다"고 자체 선언 금지. preview 페이지의 스크린샷을 사용자가 보고 OK/NG 판정.

## Test Strategy

- **빌드 통과**: `npm run build` 시 본 페이지 포함 컴파일 성공
- **production 차단**: `NODE_ENV=production npm run start` 후 `/dev/preview` 호출 → 404 반환
- **각 섹션 독립 렌더**: 1~7 섹션 중 한 개의 데이터 호출이 throw해도 나머지 섹션 정상 표시
- **반응형**: 320px / 768px / 1280px 폭에서 모든 섹션 깨짐 없음
- **다크 일관성**: 모든 색이 `var(--color-*)` 토큰만 사용 (인라인 hex 0건)

## Verification (= Phase 0 완료 게이트)

본 페이지의 모든 항목 통과 = Phase 0 완료:

- [ ] Section 1: 모든 색 토큰 시각 일치 (디자인 시스템 docs와 비교)
- [ ] Section 2: Pretendard variable weight 100~900 부드러운 변화
- [ ] Section 3: 7종 토큰 모든 상태 정상
- [ ] Section 4: 기존 컴포넌트 회귀 없음
- [ ] Section 5: 4개 데이터 호출 모두 success (NVDA, 삼성전자, FX, KOSPI 거시)
- [ ] Section 6: SWOT 응답 zod 통과 (5회 중 4회 이상)
- [ ] Section 7: syncAll 정상 종료 + 두 번째 호출 외부 API 0건
- [ ] production 빌드에서 404 차단
- [ ] 사용자(시니어 리뷰어) OK 판정

## Open Questions

1. **production에서 영구 노출 여부**: env flag로 토글하는 게 안전. 사용자가 settings에서 "개발자 모드" 토글 시 활성? Phase 1 검토
2. **자동 스크린샷 회귀 테스트**: Playwright 등으로 preview 페이지 스크린샷을 매 빌드 시 저장 → 시각 회귀 자동 감지. Phase 3+ 검토
3. **AI Smoke Test 비용**: Gemini 무료 티어 충분하지만 SWOT 호출 빈도 제한. 본 페이지 방문 시마다 호출 vs 버튼 클릭 시만 호출 → 후자로 결정 (위 명세대로)
