[← README.md로 돌아가기](README.md)

# 12 — 모델 메타 카드 + 모델 토글 (자산 B)

**위임**: Friday | **위치**: `endurance/src/app/dashboard/_components/ModelMetaCardToggle.tsx` (Client Component — 토글 URL 동기) | **의존**: Foundation 07 `metric-card` 토큰, Phase 0.5 04 모델 메타데이터(metadata.json), Phase 1 02 `DashboardSnapshot.modelMeta`

## Purpose

GEMSTONE EWS에 사용 중인 ML 모델 **메타데이터(OOS Sharpe·누적수익률·False Alarm Rate)** 표시 + 두 모델 비교 토글:
- **Model 1 Forced [2, 8, 9, 16]** — 변수 인덱스 강제 고정 (사용자 선호 — 도메인 직관 우선)
- **Model 2 Optimal** — 변수 선택 알고리즘이 OOS Sharpe 최적화로 선택

토글 클릭 시 URL `?model=model1_forced|model2_optimal` 갱신 + page 재진입(SSR)으로 02-data-api가 다른 모델 결과 로드.

## 의존성

- **사용하는 자산**:
  - Foundation 07 `metric-card` 토큰 (메타 표시)
  - Foundation 07 `market-toggle` 토큰 패턴 (모델 토글도 radiogroup 동일 구조 — 색만 다름)
  - Phase 1 02 `DashboardSnapshot.modelMeta` + `selectedModel`
- **이걸 사용하는 자산**: Phase 1 08 (Integration — 헤더 우측 또는 grid 상단 박스)

## Public Interface

```typescript
// src/app/dashboard/_components/ModelMetaCardToggle.tsx
"use client";

import type { DashboardModelMeta, ModelKind } from "@/lib/dashboard/data";

interface ModelMetaCardToggleProps {
  meta: DashboardModelMeta;
}

export function ModelMetaCardToggle(
  props: ModelMetaCardToggleProps,
): JSX.Element;
```

표시 형태:

```
┌──────────────────────────────────────────────────┐
│ MODEL  [ Model 1 Forced ] [ Model 2 Optimal ]    │
│                                                   │
│  Selected variables: [2, 8, 9, 16]                │
│  OOS Sharpe: 1.42                                 │
│  Cumulative Return: +38.2% vs BM                  │
│  False Alarm Rate: 7.3%                           │
└──────────────────────────────────────────────────┘
```

토글 클릭 시 `router.replace(`${pathname}?market=${market}&model=${next}`, { scroll: false })`.

data-testid:
- root: `widget-model-meta`
- 토글 컨테이너: `model-toggle`
- 토글 segment: `model-toggle-model1_forced`, `model-toggle-model2_optimal`

## Implementation Notes

- **Client Component**: `useRouter`/`useSearchParams` 필요 → `"use client"`. 메타 표시 자체는 Server에서 props로 받음.
- **selectedVariables 표시**: Model 1은 `[2, 8, 9, 16]` 고정. Model 2는 02-data-api가 Phase 0.5 04 metadata.json의 동적 선택 결과 로드. 두 모델 모두 동일 시그니처(`Array<2 | 8 | 9 | 16>` 자리 → 실제로는 1~22 범위) — Phase 0.5 04 metadata 스키마 SSOT에 맞춰 02가 정규화.
- **Foundation 07 radiogroup 패턴 재사용**: 자산 16 시장 토글과 동일 wrapper. testIdPrefix prop으로 `model-toggle` 박음 (헌법 §2 SSOT — 두 토글이 같은 wrapper).
- **URL 동시 갱신**: `?market=...&model=...` 두 param 동시 보존. `replace` 사용 (history 누적 금지).
- **OOS metric 포맷**: Sharpe 소수 2자리, Cumulative Return 부호+소수 1자리+`%`, False Alarm Rate 소수 1자리+`%`. `Intl.NumberFormat` 적용.

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| Phase 0.5 04 metadata.json `selected_features` 스키마 | 02가 로드, 본 위젯이 표시. 스키마 변경 시 양쪽 갱신 |
| 02 `DashboardModelMeta` 시그니처 | 본 위젯이 props로 받음. 변경 시 본 자산 동기 |
| Foundation 07 radiogroup wrapper testIdPrefix prop | 자산 16과 동일 사용. wrapper 변경 시 양쪽 영향 |

### 헌법 §0-1 Step 2 합리화 회피

- "메타 카드와 토글을 별도 컴포넌트로 분리": ❌ 토글 변경 → 메타 즉시 갱신이 핵심 UX. 분리하면 prop drilling 또는 context 추가 → 헌법 §5 오버엔지니어링. 단일 컴포넌트 유지.

## Test Strategy

### 단위
- `meta.modelKind="model1_forced"` → segment "Model 1 Forced" aria-checked=true
- 토글 클릭 → `router.replace` 호출, URL `?model=model2_optimal` 포함
- `meta.selectedVariables=[2,8,9,16]` → "[2, 8, 9, 16]" 표시
- `meta.oosSharpe=1.42` → "1.42" 표시

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 신기능 + 비동기 토글)
- 정상 토글: Model 1 → Model 2 → URL 갱신 + SSR 재진입 + 메타 갱신
- 토글 중 이전 fetch 취소: 빠른 토글 시 AbortSignal 동작 (02 의무, 본 위젯은 검증만)
- null edge: `meta=null` → "메타 데이터 없음" placeholder
- i18n: 마운트 중 언어 토글 시 라벨 자동 갱신 (caller-driven string 0건)

## Verification

- [ ] `endurance/src/app/dashboard/_components/ModelMetaCardToggle.tsx` 존재 + `"use client"` 디렉티브
- [ ] Foundation 07 radiogroup wrapper만 사용 (자체 토글 SVG 0줄)
- [ ] `tsc --noEmit` 무경고
- [ ] data-testid `widget-model-meta`, `model-toggle`, `model-toggle-model1_forced`, `model-toggle-model2_optimal` 박힘
- [ ] 단위 테스트 5개 이상 (토글 동작 + 메타 표시 + URL 갱신)
- [ ] URL `?market=...&model=...` 두 param 동시 보존 검증
- [ ] anti-pattern §2-0-1 Pattern A·B grep 0건

## Open Questions

1. **Model 1 변수 인덱스 의미 표시**: `[2, 8, 9, 16]`만 표시 vs 변수명까지 표시(`[2: KOSPI Skew, 8: ...]`). 후자 시 라벨 길어짐. 사용자 검증 후 결정 — 초안은 인덱스만 + tooltip에 변수명.
2. **OOS 기간 명시**: "OOS 2011-2023" 같은 메타도 카드에 표시할지. 신뢰도 가시화엔 좋으나 카드가 비대해짐 — 별도 tooltip 권장.
3. **Model 2 변수 변동**: Model 2 Optimal의 selected_features가 retrain마다 변동될 수 있음 — UI에 "변수 변동성" 메타도 노출할지(Phase 2+ 검토).
