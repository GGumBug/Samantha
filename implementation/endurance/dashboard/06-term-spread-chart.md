[← README.md로 돌아가기](README.md)

# 06 — Term Spread Sparkline (v2 GEMSTONE Sapphire)

> **변경 이력**
> - v2 (2026-05-16): GEMSTONE EWS 재정의에 맞춰 책임 갱신. 사유: 사용자가 GEMSTONE 스크린샷 단언 후 정공 재정의 (옵션 D). 기존 v1 구현 코드는 이 명세 §"v1 코드 처리"에 따라 처리.
> - v1 (이전): KR/US 양 시장 LineChart overlay (180일 시계열).

**위임**: Joi | **위치**: 자산 15(15-model-inputs-7-cards.md) Sapphire 카드에 흡수 또는 본 파일 폐기 후 통합 (구현 시점 결정) | **의존**: Foundation 07 `metric-card`, Foundation 08 Sparkline, Phase 0.5 07 GEMSTONE Sapphire 토큰, Phase 1 02 `DashboardGemstoneBlock.modelInputs`

## v1 코드 처리

v1 `TermSpreadChart.tsx`(LineChart wrapper + KR/US overlay)는 **자산 15 MODEL INPUTS 7 변수 카드의 Sapphire 카드에 흡수**. 본 자산 단독 컴포넌트는 폐기 또는 자산 15의 Sapphire 인스턴스로 통합 — 구현 시점에 결정.

- v1 LineChart overlay → v2 sparkline 카드 (단일 변수 sparkline + z-score + NEUTRAL/REVERSION 라벨)
- v1 양 시장(KR + US) 동시 표시 → v2 US 10Y-2Y Treasury Yield Spread 단일 (GEMSTONE Sapphire 변수 정의 그대로). KR 국채 spread는 GEMSTONE 7 변수 정의 외 — 본 위젯에서 제거
- v1 단위 테스트 5건 → 자산 15 단위 테스트로 흡수
- v1 데이터 출처(yfinance `^TNX` 등) → 자산 15에서 FRED `T10Y2Y` 시리즈로 교체 (Phase 0.5 01 데이터 수집 파이프라인이 단일 진입점)

**시니어 판단**: 본 명세 파일을 즉시 삭제하지 않는 이유는 v1 구현 코드(4커밋)가 살아있고, 자산 15 머지 시점에 import 경로/책임 이전을 확정해야 하기 때문. 자산 15 머지 시 본 명세는 "redirect to 15" 한 줄 stub으로 축소 가능.

## Purpose

GEMSTONE Sapphire 변수(**US 10Y-2Y Treasury Yield Spread**)를 sparkline 카드 형태로 표시. MODEL INPUTS 7 변수 중 1개로 축소 — 자산 15가 7 변수를 일관 grid로 표시하며 그 중 Sapphire 인스턴스가 본 자산의 v2 책임. 양 시장(KR + US) overlay는 v2 범위 외(KR 국채는 GEMSTONE 7 변수 정의에 없음).

본 위젯은 외부 API 호출 0건. 02-data-api가 반환한 `DashboardGemstoneBlock.modelInputs[]` 중 `gemstoneId === "sapphire"` 항목을 props로 받아 sparkline + z-score + NEUTRAL/REVERSION 라벨만 그린다.

## 의존성

- **사용하는 자산**:
  - 자산 15(`15-model-inputs-7-cards.md`) — Sapphire 카드 인스턴스 (본 자산 v2 결과 흡수)
  - Foundation 07 `metric-card` 토큰, Foundation 08 Sparkline wrapper
  - Phase 0.5 07 GEMSTONE Sapphire 토큰 (보석색·i18n key)
  - Phase 1 02 v2 `DashboardGemstoneBlock.modelInputs[]` (gemstoneId === "sapphire")
- **이걸 사용하는 자산**: Phase 1 08 (Integration이 자산 15 grid 안에서 Sapphire 카드로 배치)

## Public Interface

v2 단독 컴포넌트는 폐기 권장 — 자산 15의 `ModelInputCard` 인스턴스가 본 자산 책임 흡수:

```typescript
// 자산 15에서 자동 렌더 — gemstoneId="sapphire" 카드
// 본 자산 단독 export 없음. 자산 15 ModelInputsCards가 7 카드 중 Sapphire 슬롯에 배치
```

표시 형태 (자산 15 Sapphire 카드 인스턴스):

```
┌─────────────────────────────┐
│ Sapphire                    │
│ US 10Y-2Y Treasury Spread   │
│ 0.34 (z=-1.8)               │
│ ╲╲╱╲╱       (90포인트 sparkline)│
│ REVERSION                   │
└─────────────────────────────┘
```

자세한 props 시그니처는 자산 15(`15-model-inputs-7-cards.md`) `ModelInputCardProps` 참조 — SSOT 단일.

## Implementation Notes

- **자산 15 인스턴스로 흡수**: v2는 자산 15 `ModelInputCard` Sapphire 슬롯에서 렌더. 본 자산 단독 컴포넌트 0줄 — 자산 15 명세 따른다.
- **데이터 출처 변경**: v1 yfinance `^TNX` 등 → v2 Phase 0.5 01 데이터 수집 파이프라인 (FRED `T10Y2Y` 시리즈). KR 국채 spread는 GEMSTONE 7 변수 정의 외 — v2에서 제거.
- **헌법 §6 escape hatch**: v2는 단독 컴포넌트 없음. 본 명세는 SSOT 추적 의무만 유지.

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| 자산 15 `ModelInputCard` props 시그니처 | 본 자산이 의존 (Sapphire 인스턴스). 변경 시 본 명세 동기 |
| Phase 0.5 07 GEMSTONE Sapphire 토큰 | 본 자산이 의존 (색·i18n key) |
| v1 `TermSpreadChart.tsx` 잔재 | git mv 또는 삭제 결정 — 자산 15 머지 시점에 |

### 헌법 §0-1 Step 2 합리화 회피

- "v1 컴포넌트 보존 + v2 별도 컴포넌트 신규": ❌ 위젯 중복 = SSOT 위반. 자산 15 단일 진입점.

## Test Strategy

자산 15 단위 테스트로 흡수 — Sapphire 인스턴스 시나리오 추가 의무 (자산 15 명세 Test Strategy 참조). 본 자산은 SSOT 박제 외 단독 테스트 없음.

## Verification

- [ ] v1 `TermSpreadChart.tsx` 파일 처리 결정 박혀 있음 (삭제 또는 자산 15 인스턴스 import 경로 갱신)
- [ ] 자산 15가 Sapphire 카드 인스턴스 렌더 검증 (자산 15 verification 항목과 동기)
- [ ] grep `TermSpreadChart` endurance/src/ 호출 0건 (v1 잔재 제거)
- [ ] grep `DashboardMacroBlock\|termSpreadSeries` 본 파일 0건 (v2 시그니처만)

## Open Questions

1. **v1 컴포넌트 파일 처리**: 즉시 삭제 vs 자산 15 머지 후 삭제. 후자 권장 (자산 15가 흡수 완료 후 제거).
2. **KR Term Spread Phase 2+ 추가**: GEMSTONE 7 변수 외이지만 Phase 2 종목 화면 또는 별도 위젯으로 추가 가능성 — 사용자 검증 후 결정.
