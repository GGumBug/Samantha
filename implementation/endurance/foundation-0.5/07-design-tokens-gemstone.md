[← README.md로 돌아가기](README.md)

# 07 — Design Tokens GEMSTONE (7 변수 게이지·라벨·색)

**위임**: Joi | **위치**: `design-system/gemstone.md` 신규 + `endurance/src/components/gemstone/` | **의존**: Foundation 07 (기존 데이터 비즈 토큰 7종 — gauge·heatmap·trigger-badge 등)

## Purpose

GEMSTONE 7 변수의 **시각 SSOT**. 각 변수는 보석명 별칭(`Garnet`·`Emerald`·`Moonstone` 등)을 갖고, 게이지 색·라벨 한국어/영어·tooltip 설명·z-score 표시 규칙을 본 명세가 박는다. Phase 1 위젯(GemstoneRadar, EarlyWarningGauge) 이 모두 본 토큰 경유 — 임의값 사용 금지(헌법 §2 SSOT).

Foundation 07 의 gauge·heatmap·trigger-badge 를 그대로 재사용하고, 본 명세는 **GEMSTONE 도메인 한정 메타데이터** (보석명, 변수 ID, 색 매핑) 만 박는다.

## 의존성

- **사용하는 자산**: Foundation 07 (gauge-meter·trigger-badge·metric-card 토큰), 디자인 시스템 colors.md (semantic-warning, semantic-danger)
- **이걸 사용하는 자산**: 08 (preview 확장), Phase 1 위젯 (EarlyWarningGauge, GemstoneRadar, VariableDetailCard)

## 7 GEMSTONE 변수 토큰 스펙

각 변수의 메타데이터 (i18n 키 보존 — 헌법 §2-0 anti-pattern 회피):

| ID | 보석명 | 변수 풀네임 (en) | i18n key (label) | i18n key (description) | 색 (z-score 양극) |
|----|--------|-----------------|------------------|------------------------|------------------|
| `garnet` | Garnet | KOSPI Return Skewness | `gemstone.garnet.label` | `gemstone.garnet.description` | `#a83232` ↔ `#6b3030` |
| `emerald` | Emerald | KOSPI Volume / Market Cap Ratio | `gemstone.emerald.label` | `gemstone.emerald.description` | `#2a6b3a` ↔ `#1a3a2a` |
| `moonstone` | Moonstone | KOSPI Pairwise Correlation | `gemstone.moonstone.label` | `gemstone.moonstone.description` | `#c0c8d4` ↔ `#5a6270` |
| `sapphire` | Sapphire | US 10Y-2Y Treasury Spread | `gemstone.sapphire.label` | `gemstone.sapphire.description` | `#2a4a8a` ↔ `#1a2a4a` |
| `topaz` | Topaz | Fed Policy Rate Uncertainty | `gemstone.topaz.label` | `gemstone.topaz.description` | `#d4a04a` ↔ `#7a5a2a` |
| `ruby` | Ruby | WTI Crude Oil Spot | `gemstone.ruby.label` | `gemstone.ruby.description` | `#c43a3a` ↔ `#6a1a1a` |
| `amber` | Amber | 10-Year Expected Inflation | `gemstone.amber.label` | `gemstone.amber.description` | `#d48a2a` ↔ `#7a4a1a` |

### TypeScript 스펙

```typescript
// endurance/src/components/gemstone/types.ts

export type GemstoneId =
  | "garnet" | "emerald" | "moonstone"
  | "sapphire" | "topaz" | "ruby" | "amber";

export interface GemstoneToken {
  id: GemstoneId;
  variableKey: keyof GemstoneVariables; // 02 의 GemstoneVariables 필드
  labelKey: string;                     // i18n key
  descriptionKey: string;
  gemColor: string;                     // 본문 보석색 (z-score 0 기준)
  alertColor: string;                   // z-score |z| > 2 시 alert 색
  defaultLookbackDays: number;          // 02 의 lookback (표시용)
}

export const GEMSTONE_TOKENS: Record<GemstoneId, GemstoneToken>;
```

### 게이지 색 매핑 (Foundation 07 gauge-meter 재사용)

- z-score 0 ~ ±1: 본문 gemColor
- |z| 1 ~ 2: `{colors.semantic-warning}` (#f0a04b)
- |z| > 2: `{colors.semantic-danger}` (#d4564b)

위 매핑은 7 변수 공통 — 변수별 분기 없음 (SSOT).

### EarlyWarningGauge 색 (5 Stage)

| Stage | 색 | 라벨 i18n key |
|-------|-----|--------------|
| 1 (Normal) | `{colors.semantic-success}` | `ews.stage.normal` |
| 2 (Watch) | `{colors.ink-muted}` | `ews.stage.watch` |
| 3 (Caution) | `{colors.semantic-warning}` (#f0a04b) | `ews.stage.caution` |
| 4 (Warning) | `#d48a2a` (커스텀, amber 계열) | `ews.stage.warning` |
| 5 (Critical) | `{colors.semantic-danger}` (#d4564b) | `ews.stage.critical` |

## Implementation Notes

- **i18n key 보존**: 컴포넌트는 `t(token.labelKey)` 호출, caller 가 번역된 string 박지 않음 — 헌법 §2-0 anti-pattern 회피 (caller-driven UI string snapshot 금지).
- **GemstoneToken SSOT**: `GEMSTONE_TOKENS` 상수 1곳에서 정의 — 02 변수 ID, 04 학습 feature_names, 07 디자인 토큰 3축이 본 객체 경유 정합.
- **보석색 임의값 아님**: 각 보석 실제 광물색 참고 (Garnet=짙은 적색, Emerald=짙은 녹, Moonstone=옅은 회청, etc). 임의값으로 보이지만 도메인 명명 — 사용자 직관 강화.
- **라벤더 보존**: GEMSTONE 보석색 7개 중 라벤더 없음 — 라벤더는 브랜드·CTA 전용 (헌법 §1·디자인 시스템 권위).
- **다크 단일**: 7 보석색은 다크 캔버스에서 충분한 대비. 라이트 모드 미존재(`design-system/DESIGN.md` 5원칙).

## Test Strategy

- **i18n 정합**: 7 × 2 = 14 i18n key 가 `messages/en.json`, `messages/ko.json` 양쪽 모두 존재 (누락 시 빌드 fail)
- **시각 회귀**: 08 preview 확장에서 7 GEMSTONE 토큰 모두 렌더 — 사용자/시니어 OK 판정
- **z-score → 색 매핑 단위 테스트**: -3, -1.5, 0, 1.5, 3 입력 → 기댓색 검증
- **접근성**: gauge `aria-label` 에 i18n 라벨 박힘, 색 단독 의미 전달 금지 (z-score 숫자 병기)

## Verification

- [ ] `design-system/gemstone.md` 신규 파일 작성 (본 명세를 시각 SSOT 로 박음)
- [ ] `GEMSTONE_TOKENS` 상수 export, 7 항목 + i18n key 14개
- [ ] `messages/en.json`, `messages/ko.json` 에 14 key 추가
- [ ] 8 preview 확장에서 7 GEMSTONE 토큰 모든 상태(normal/warning/critical) 렌더
- [ ] grep 으로 컴포넌트 내 hex 인라인 0건 (모두 토큰 경유)
- [ ] 헌법 §2-0 caller-driven string 안티패턴 0건 (props 는 token id + z-score, t() 는 컴포넌트 내부)

## Open Questions

1. **보석명 7개 vs 변수 추가 시 확장성**: 현재 7개 — 변수 8번째 추가 시 어떤 보석? 다이아몬드? 옅은 색 보석은 다크 캔버스 대비 어려움. Phase 2+ 검토.
2. **사용자 한글 보석명**: "Garnet" → "가넷" vs "석류석" — 시장 친숙도 검토. i18n key 박혀 있으니 후속 변경 비용 낮음.
3. **z-score 표시 단위**: 게이지에 z-score 숫자 병기 vs 보석명 + 색만. 접근성 위해 숫자 병기 우선 (정보 손실 회피).
