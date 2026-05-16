[← README.md로 돌아가기](README.md)

# 08 — Dashboard Integration + `/dev/preview` 갱신 (v2 GEMSTONE A~G)

> **변경 이력**
> - v2 (2026-05-16): GEMSTONE EWS 재정의에 맞춰 책임 갱신. 사유: 사용자가 GEMSTONE 스크린샷 단언 후 정공 재정의 (옵션 D). 기존 v1 구현 코드는 이 명세 §"v1 코드 처리"에 따라 처리.
> - v1 (이전): 04 P/E + 05 Volatility + 06 Term Spread + 07 Gauge 4 위젯 2×2 grid 통합.

**위임**: Friday | **위치**: `endurance/src/app/dashboard/page.tsx` (01의 grid를 자산 11~17 GEMSTONE 위젯 A~G로 교체) + `endurance/src/app/dev/preview/_sections/DashboardPreview.tsx` (Foundation 10에 신규 섹션 추가) | **의존**: Phase 1 01, 02, 11, 12, 13, 14, 15, 16, 17

## v1 코드 처리

v1 위젯 배치(04 P/E·05 Volatility·06 Term Spread·07 Gauge) → **v2 위젯 배치(A~G, 자산 11~17)**. 반응형 grid **재설계 필요**:

- v1 2×2 grid(Gauge / P/E / Volatility / Term Spread) → v2 GEMSTONE 7 위젯 grid (좌상 INTENSITY+Stage, 우상 Forward Expectancy, 좌중 Performance Analytics, 우중 MODEL INPUTS 7카드, 헤더 시장+모델 토글+Refresh)
- v1 `getDashboardSnapshot` 1회 호출 + 4 위젯 props 분배 → v2 동일 패턴 유지(1회 호출 + 7 위젯 props 분배). SSOT 패턴 보존
- v1 `ErrorBadgeRow` 보존 — 자산 11~17 모두 부분 실패 시 동일 패턴 적용
- v1 data-testid 명명 규약 보존 + 신규 GEMSTONE 위젯 testid 추가 (아래 §data-testid 규약 표 v2)
- v1 단위/통합 테스트 → v2 위젯 7종 기준 재작성 (mocking은 02 v2 `DashboardSnapshot` 기준)

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
// src/app/dashboard/page.tsx (v2 GEMSTONE A~G 통합)
import { getDashboardSnapshot } from "@/lib/dashboard/data";
import { MarketToggleHeader } from "./_components/MarketToggleHeader"; // 자산 16
import { IntensityGaugeStageBadge } from "./_components/IntensityGaugeStageBadge"; // 자산 11 (A)
import { ModelMetaCardToggle } from "./_components/ModelMetaCardToggle"; // 자산 12 (B)
import { ForwardExpectancyTable } from "./_components/ForwardExpectancyTable"; // 자산 13 (C)
import { PerformanceAnalyticsChart } from "./_components/PerformanceAnalyticsChart"; // 자산 14 (D)
import { ModelInputsCards } from "./_components/ModelInputsCards"; // 자산 15 (E)
import { RefreshButton } from "./_components/RefreshButton"; // 자산 17 (G)
import { ErrorBadgeRow } from "./_components/ErrorBadgeRow";

export default async function DashboardPage({ searchParams }: DashboardPageProps) {
  const { market: raw, model: rawModel } = await searchParams;
  const market = parseMarket(raw);
  const modelKind = parseModelKind(rawModel); // "model1_forced" | "model2_optimal"
  const snapshot = await getDashboardSnapshot(market, { modelKind });
  return (
    <main className="mx-auto max-w-[1280px] px-6 py-section">
      <header className="flex items-center justify-between">
        <MarketToggleHeader current={market} />            {/* 자산 16 (F) */}
        <ModelMetaCardToggle meta={snapshot.modelMeta} />  {/* 자산 12 (B) — 모델 토글 + 메타 */}
        <RefreshButton market={market} modelKind={modelKind} />  {/* 자산 17 (G) */}
      </header>
      <ErrorBadgeRow errors={snapshot.errors} />
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <IntensityGaugeStageBadge blocks={snapshot.blocks} />        {/* A — 좌상 */}
        <ForwardExpectancyTable blocks={snapshot.blocks} />          {/* C — 우상 */}
        <PerformanceAnalyticsChart blocks={snapshot.blocks} />       {/* D — 좌중 */}
        <ModelInputsCards blocks={snapshot.blocks} />                {/* E — 우중 (7카드 grid) */}
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

3 시장 × 2 모델 = 6 조합으로 위젯 11~17(A~G) 한 화면 렌더 + 부분 실패 시뮬레이션.

## Implementation Notes

### Grid 레이아웃 (반응형)

| 폭 | 레이아웃 (GEMSTONE 스크린샷 패턴) |
|----|----------------------------------|
| 375px | 1col 세로 stack — F+B+G 헤더 → A → C → D → E (7카드 grid 내부 2col) |
| 768px | 2col — 1행 [A, C] / 2행 [D, E] / 헤더 풀폭 |
| 1280px | 2col 동일 + 넓은 padding. E(7카드) 4×2-1 grid 내부 |

### 02 호출 단일 진입점 (헌법 §2 SSOT)

- page.tsx에서 `getDashboardSnapshot(market, { modelKind })` **1회 호출**
- snapshot.blocks + snapshot.modelMeta를 위젯 11~17에 props 분배
- grep으로 `getDashboardSnapshot` 호출이 page.tsx + 02 lib 외 0건임을 verification에서 검증

### 부분 실패 가시화

- 02가 `errors=[{market:"US", code:"YFINANCE_503"}]` 반환 시 `ErrorBadgeRow`가 헤더 아래 trigger-badge 표시
- 위젯 11~17은 `blocks`만 보고 그림 — 정상 시장만 렌더

### 헌법 §6 escape hatch: 없음. production 통합 코드

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| 01 shell `DashboardGrid` placeholder | 본 자산이 교체. 01 v2 grid props 시그니처와 일치 |
| 02 v2 `getDashboardSnapshot` 시그니처 | page.tsx 호출처 변경 시 본 자산 동기 갱신 |
| 위젯 11~17 props (`blocks: DashboardGemstoneBlock[]`) | 본 자산이 분배. 위젯 props 시그니처 통일성 검증 |
| Foundation 10 preview 페이지 | 신규 v2 GEMSTONE 섹션 추가 — Foundation 10 명세 갱신 의무 |

### 헌법 §0-1 Step 2 합리화 회피

- "위젯이 각자 getDashboardSnapshot 호출하면 자율": ❌ SSOT 위반. 1회 호출 + props 분배 의무
- "ErrorBadgeRow 별도 컴포넌트 분리는 오버": ❌ errors 빈 시 null + 색·레이아웃 책임 분리. 7 위젯이 각자 에러 처리하면 SSOT 위반

## Test Strategy

### 통합 + 반응형 + 표준 검증 (헌법 §0-1 Step 3 신기능 통합)
- `/dashboard?market=KR|US|BOTH` × `?model=model1_forced|model2_optimal` 6 조합 모두 7 위젯 렌더
- 02 mock 부분 실패 → ErrorBadgeRow 가시화 + 7 위젯은 정상 시장 block만 그림
- 375px / 768px / 1280px 반응형 깨짐 0건
- null/empty `blocks=[]` → 7 위젯 모두 placeholder + 페이지 깨짐 0
- 02 호출 1회 (page.tsx grep 외 0건)
- i18n 마운트 토글 시 7 위젯 + ErrorBadgeRow 자동 갱신 (caller-driven string 0건 grep — 헌법 §2-0-1)

## Verification

- [ ] `endurance/src/app/dashboard/page.tsx` 가 01의 placeholder를 위젯 11~17(A~G)로 교체
- [ ] `endurance/src/app/dashboard/_components/ErrorBadgeRow.tsx` 존재 (v1 보존)
- [ ] `endurance/src/app/dev/preview/_sections/DashboardPreview.tsx` v2 GEMSTONE 7 위젯 렌더 + Foundation 10 명세 갱신
- [ ] `tsc --noEmit` 무경고 + `npm run build` 성공
- [ ] `/dashboard` 6 조합(market × model) 시각 정상
- [ ] 반응형 3 폭 깨짐 0건
- [ ] `grep "getDashboardSnapshot" endurance/src/` 결과 page.tsx + 02 lib 외 0건 (단일 진입점)
- [ ] grep 위젯 컴포넌트 내 `fetch(`, `yahoo-finance`, `infer(` 0건 (위젯 직접 호출 0건)
- [ ] anti-pattern §2-0-1 Pattern A·B grep 전 위젯 0건

### data-testid 명명 규약 (09 e2e 의존 박제)

09 smoke e2e 가 의존하는 testid 단일 진입점 (SSOT). 본 08 자산이 박제, 09 가 소비:

| testid | 위치 | 책임 |
|--------|------|------|
| `market-toggle` | MarketToggle 컨테이너 (`radiogroup`) — 자산 16 | 토글 자체 식별 |
| `market-toggle-KOSPI200` | 토글 segment (KR radio button, v2 라벨 갱신) | KOSPI200 시장 선택 시뮬레이션 |
| `market-toggle-SP500` | 토글 segment (US radio button, v2 라벨 갱신) | S&P 500 시장 선택 시뮬레이션 |
| `market-toggle-BOTH` | 토글 segment (BOTH radio button) | BOTH 시장 선택 시뮬레이션 |
| `model-toggle` | ModelMetaCardToggle 컨테이너 — 자산 12 | 모델 토글 자체 식별 |
| `model-toggle-model1_forced` | Model 1 Forced [2,8,9,16] segment | Model 1 선택 시뮬레이션 |
| `model-toggle-model2_optimal` | Model 2 Optimal segment | Model 2 선택 시뮬레이션 |
| `widget-intensity-gauge` | IntensityGaugeStageBadge wrapper — 자산 11 | INTENSITY 게이지 식별 |
| `widget-stage-badge` | Stage 배지 (자산 11 내부 노드) | Stage 1-5 배지 식별 |
| `widget-forward-expectancy` | ForwardExpectancyTable wrapper — 자산 13 | Forward Expectancy 5 bucket 표 |
| `widget-performance-analytics` | PerformanceAnalyticsChart wrapper — 자산 14 | Performance Analytics 차트+메트릭 |
| `widget-model-inputs` | ModelInputsCards wrapper — 자산 15 | 7 변수 카드 grid 식별 |
| `widget-model-meta` | ModelMetaCardToggle 메타 영역 — 자산 12 | OOS Sharpe 등 메타 카드 |
| `widget-refresh` | RefreshButton — 자산 17 | Refresh 버튼 |
| `error-badge-row` | ErrorBadgeRow wrapper (errors.length>0 시) | 부분 실패 가시화 root |
| `error-badge-KR` | KR 시장 trigger-badge wrapper | KR 에러 식별 |
| `error-badge-US` | US 시장 trigger-badge wrapper | US 에러 식별 |

규약:
- 위젯 컨테이너 testid 는 `widget-*` prefix. 위젯 내부 노드 testid (예: EarlyWarningGauge 의 `early-warning-placeholder-text`) 는 위젯별 책임으로 별도 박제.
- segment 단위 testid 는 `{컨테이너}-{값}` 형식 — Foundation 07 `MarketToggle` 의 `testIdPrefix` prop 으로 동적 박제 (optional prop, 기본 동작 변경 0건).
- 09 e2e 가 testid 추가/변경 필요 시 본 표 갱신 후 코드 동기 의무 (헌법 §2 SSOT).

## Open Questions

1. **위젯 grid 레이아웃 정확 매핑**: GEMSTONE 스크린샷 패턴(좌상 A·우상 C·좌중 D·우중 E·헤더 F+B+G) 시각 결정 — Phase 0.5 08 preview에서 결정.
2. **모바일 위젯 우선순위**: 375px에서 7 위젯 세로 stack 순서 — INTENSITY가 가장 위가 자연. Phase 0.5 08 preview에서 결정.
3. **i18n 적용 시점**: Phase 1 영어/한국어 혼재(라벨 영어, 도움말 한국어). Phase 2+ 본격 i18n 도입 시 본 자산 + 위젯 11~17 + ErrorBadgeRow 모두 §2-0-1 마이그레이션 의무.
4. **Foundation 10 preview 갱신**: 본 자산 v2가 Foundation 10 명세에 "v2 GEMSTONE Dashboard Preview 섹션 추가" 1줄 갱신 의무 (SSOT 동기).
