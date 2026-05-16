[← README.md로 돌아가기](README.md)

# 08 — Dashboard Integration + `/dev/preview` 갱신

**위임**: Friday | **위치**: `endurance/src/app/dashboard/page.tsx` (01의 grid를 04~07 실제 위젯으로 교체) + `endurance/src/app/dev/preview/_sections/DashboardPreview.tsx` (Foundation 10에 신규 섹션 추가) | **의존**: Phase 1 01, 02, 04, 05, 06, 07

## Purpose

Phase 1 01~07 자산이 머지된 후, 01의 placeholder grid를 04~07 위젯 4종으로 교체해 **`/dashboard` 페이지를 첫 끝-끝 동작 상태**로 만든다. 동시에 Foundation 10 `/dev/preview` 페이지에 "Dashboard Preview" 섹션을 추가해 시각 회귀 검증을 박는다.

본 자산은 **새 로직 없음** — 01~07 결합만. 그러나 다음 통합 책임은 본 자산이 맡음:
1. Grid 레이아웃 (1280px desktop · 768px tablet · 375px mobile 반응형)
2. 부분 실패 가시화 (02 `errors[]`을 위젯별 trigger-badge로 분배)
3. 02 호출 1회 + 4 위젯에 props 분배 (헌법 §2 SSOT — 위젯이 각자 호출하지 않음)
4. `/dev/preview` Section 추가 (회귀 회피용)

## 의존성

- **사용하는 자산**: Phase 1 01 (shell), 02 (data), 04 (P/E cards), 05 (volatility), 06 (term spread), 07 (gauge)
- **이걸 사용하는 자산**: Phase 1 09 (e2e smoke 테스트)

## Public Interface

### `/dashboard` 페이지 통합 (01-route-shell의 DashboardGrid 구현)

```typescript
// src/app/dashboard/page.tsx (01에서 placeholder였던 부분을 본격 통합)
import { getDashboardSnapshot } from "@/lib/dashboard/data";
import { MarketToggleHeader } from "./_components/MarketToggleHeader";
import { PeMetricCards } from "./_components/PeMetricCards";
import { VolatilitySparkline } from "./_components/VolatilitySparkline";
import { TermSpreadChart } from "./_components/TermSpreadChart";
import { EarlyWarningGauge } from "./_components/EarlyWarningGauge";
import { ErrorBadgeRow } from "./_components/ErrorBadgeRow";

export default async function DashboardPage({ searchParams }: DashboardPageProps) {
  const { market: raw } = await searchParams;
  const market = parseMarket(raw);
  const snapshot = await getDashboardSnapshot(market);
  return (
    <main className="mx-auto max-w-[1280px] px-6 py-section">
      <MarketToggleHeader current={market} />
      <ErrorBadgeRow errors={snapshot.errors} />
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <EarlyWarningGauge blocks={snapshot.blocks} size="md" />
        <PeMetricCards blocks={snapshot.blocks} />
        <VolatilitySparkline blocks={snapshot.blocks} />
        <div className="md:col-span-2">
          <TermSpreadChart blocks={snapshot.blocks} heightPx={240} />
        </div>
      </section>
    </main>
  );
}
```

### `ErrorBadgeRow` (본 자산에서 정의 — 최소 컴포넌트)

```typescript
// src/app/dashboard/_components/ErrorBadgeRow.tsx
import type { DashboardSnapshot } from "@/lib/dashboard/data";

interface ErrorBadgeRowProps {
  errors: DashboardSnapshot["errors"];
}

export function ErrorBadgeRow({ errors }: ErrorBadgeRowProps): JSX.Element | null;
```

`errors`가 비어 있으면 `null` 반환 (자리 차지 X). 1개 이상이면 헤더 아래에 Foundation 07 `trigger-badge` 토큰으로 시장별 에러 표시.

### `/dev/preview` 신규 섹션

```typescript
// src/app/dev/preview/_sections/DashboardPreview.tsx
export function DashboardPreviewSection(): JSX.Element;
```

세 모드(KR / US / BOTH)로 4 위젯을 한 화면에 렌더 + 부분 실패 시뮬레이션(02 mock에서 errors 박은 상태) 시각 확인.

## Implementation Notes

### Grid 레이아웃 결정 (반응형)

| 폭 | 레이아웃 |
|----|---------|
| 375px (mobile) | 1 column 세로 stack — Gauge → P/E cards → Volatility → Term Spread |
| 768px (tablet) | 2 column — 1행 [Gauge, P/E] / 2행 [Volatility, Term Spread] |
| 1280px (desktop) | 2 column 동일 + 더 넓은 padding |

Term Spread는 시계열이라 가능하면 풀폭(desktop 2-col span) 권장.

### 02 호출 단일 진입점 (헌법 §2 SSOT)

- page.tsx에서 `getDashboardSnapshot(market)` **1회 호출**
- snapshot.blocks를 4 위젯에 props로 분배
- grep으로 `getDashboardSnapshot` 호출이 page.tsx 외 0건임을 본 자산 verification에서 검증 의무

### 부분 실패 가시화

- 02가 `errors=[{market:"US", code:"YFINANCE_503", ...}]` 반환 시
- `ErrorBadgeRow`가 헤더 아래 한 줄에 "NASDAQ 데이터 일시 실패" trigger-badge 표시
- 4 위젯은 `blocks`만 보고 그림 — KR 블록만 있으면 NASDAQ 자리는 자동으로 빈칸 (위젯 자체 빈 데이터 처리)

### `/dev/preview` 회귀 박제

- Foundation 10 preview 페이지에 `<DashboardPreviewSection />` 추가
- Section 3 토큰 회귀와 별개로, 본 섹션은 **실제 dashboard 위젯 조합** 회귀 감지

### 헌법 §6 escape hatch 적용 가능 영역

- 없음. 본 자산은 production 통합 코드

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| 01 shell `DashboardGrid` placeholder | 본 자산이 교체. 01 명세의 grid props 시그니처와 일치 |
| 02 `getDashboardSnapshot` 시그니처 | page.tsx 호출처 변경 시 본 자산 동기 갱신 |
| 04~07 위젯 props (`blocks: DashboardMacroBlock[]`) | 본 자산이 분배. 위젯 props 시그니처 통일성 검증 |
| Foundation 10 preview 페이지 | 신규 섹션 추가 — Foundation 10 명세에 본 자산 추가 박제 (10 명세 갱신 의무) |

### 헌법 §0-1 Step 2 합리화 회피

- "위젯이 각자 getDashboardSnapshot 호출하면 자율": ❌ N번 호출 + 부분 실패 분산 → SSOT 위반. 1회 호출 + props 분배 의무
- "ErrorBadgeRow 별도 컴포넌트 분리는 오버": ❌ ErrorBadgeRow는 errors 빈 배열 시 null 반환 + 색·레이아웃 책임 분리. 4 위젯이 각자 에러 처리하면 SSOT 위반 (헌법 §2)

## Test Strategy

### 통합
- `/dashboard?market=BOTH` → 4 위젯 모두 렌더 + 양 시장 데이터 표시
- `/dashboard?market=KR` → 4 위젯에 KR 데이터만 (NASDAQ 자리 자동 비움)
- 02 mock에서 US reject → 헤더 아래 ErrorBadgeRow에 NASDAQ 에러 + 4 위젯은 KR 블록만 그림

### 반응형
- 375px / 768px / 1280px 폭에서 레이아웃 깨짐 0건
- desktop에서 Term Spread 풀폭 span 확인

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 신기능 통합)
- ✅ 정상 호출: 3 market 모두 200
- ✅ null/empty: 02 응답 blocks=[] → 4 위젯 모두 "데이터 없음" placeholder + 페이지 깨짐 0
- ✅ 외부 API 실패: 부분 실패 시 ErrorBadgeRow 가시화
- ✅ 02 호출 1회: page.tsx에서만 호출 (grep 0건 외)

### 표준 검증 시나리오 (i18n — Phase 1 미적용)
- 현재 i18n 미적용 — Open Questions에 박제
- 추후 i18n 도입 시 ErrorBadgeRow + 위젯들이 `useTranslation` 구독 + 키 보존 props로 마이그레이션 의무 (헌법 §2-0-1)

## Verification

- [ ] `endurance/src/app/dashboard/page.tsx` 가 01의 placeholder를 04~07 실제 위젯으로 교체
- [ ] `endurance/src/app/dashboard/_components/ErrorBadgeRow.tsx` 존재
- [ ] `endurance/src/app/dev/preview/_sections/DashboardPreview.tsx` 존재 + Foundation 10 preview에 섹션 추가
- [ ] `tsc --noEmit` 무경고
- [ ] `npm run build` 성공
- [ ] `/dashboard` 직접 방문 시 4 위젯 모두 시각 렌더
- [ ] `/dashboard?market=KR | US | BOTH` 3 모드 모두 정상
- [ ] 02 부분 실패 시뮬레이션 → ErrorBadgeRow 가시
- [ ] 반응형 3 폭 깨짐 0건
- [ ] `grep "getDashboardSnapshot" endurance/src/` 결과가 page.tsx + 02 lib 외 0건 (단일 진입점)
- [ ] `/dev/preview` Dashboard Preview 섹션 추가 확인 + Foundation 10 명세 갱신
- [ ] grep으로 본 위젯 컴포넌트 내 `fetch(`, `yahoo-finance` 0건 (위젯 자체 호출 없음)

### data-testid 명명 규약 (09 e2e 의존 박제)

09 smoke e2e 가 의존하는 testid 단일 진입점 (SSOT). 본 08 자산이 박제, 09 가 소비:

| testid | 위치 | 책임 |
|--------|------|------|
| `market-toggle` | MarketToggle 컨테이너 (`radiogroup`) | 토글 자체 식별 |
| `market-toggle-KR` | 토글 segment (KR radio button) | KR 시장 선택 시뮬레이션 |
| `market-toggle-US` | 토글 segment (US radio button) | US 시장 선택 시뮬레이션 |
| `market-toggle-BOTH` | 토글 segment (BOTH radio button) | BOTH 시장 선택 시뮬레이션 |
| `widget-pe-cards` | PeMetricCards wrapper (page.tsx) | P/E·EPS 위젯 식별 |
| `widget-volatility-sparkline` | VolatilitySparkline wrapper | 변동성 위젯 식별 |
| `widget-term-spread-chart` | TermSpreadChart wrapper | Term Spread 위젯 식별 |
| `widget-early-warning-gauge` | EarlyWarningGauge wrapper | 게이지 위젯 식별 |
| `error-badge-row` | ErrorBadgeRow wrapper (errors.length>0 시) | 부분 실패 가시화 root |
| `error-badge-KR` | KR 시장 trigger-badge wrapper | KR 에러 식별 |
| `error-badge-US` | US 시장 trigger-badge wrapper | US 에러 식별 |

규약:
- 위젯 컨테이너 testid 는 `widget-*` prefix. 위젯 내부 노드 testid (예: EarlyWarningGauge 의 `early-warning-placeholder-text`) 는 위젯별 책임으로 별도 박제.
- segment 단위 testid 는 `{컨테이너}-{값}` 형식 — Foundation 07 `MarketToggle` 의 `testIdPrefix` prop 으로 동적 박제 (optional prop, 기본 동작 변경 0건).
- 09 e2e 가 testid 추가/변경 필요 시 본 표 갱신 후 코드 동기 의무 (헌법 §2 SSOT).

## Open Questions

1. **Refresh 버튼**: 02에 `force: true` 옵션이 있음. UI에 Refresh 버튼 노출 여부 — Phase 1은 자동 로드만 + Refresh 미노출(YAGNI). Phase 2+ 검토
2. **Term Spread 풀폭 vs 1열**: desktop에서 풀폭이 시각 임팩트 크지만 다른 위젯과 시각 비대칭. 사용자 검증 후 결정
3. **모바일 게이지 사이즈**: 375px에서 `size="md"`는 클 수 있음. `size="sm"`으로 자동 다운사이즈 vs CSS로 scale — 후자가 단순
4. **i18n**: Phase 1 한국어 단일. Phase 2+ 도입 시 본 자산 + 4 위젯 + ErrorBadgeRow 모두 마이그레이션 (헌법 §2-0-1 데이터 흐름 string snapshot 박멸)
5. **`/dev/preview` 갱신이 Foundation 10 명세를 수정해야 함** — Phase 1 자산이 Phase 0 SSOT를 건드리는 첫 케이스. 본 PR에서 Foundation 10 명세에 "Phase 1 Dashboard Preview 섹션 추가" 1줄 갱신 의무 (헌법 §2 SSOT 동기)
