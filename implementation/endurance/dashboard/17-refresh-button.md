[← README.md로 돌아가기](README.md)

# 17 — Refresh 버튼 (자산 G)

**위임**: Friday | **위치**: `endurance/src/app/dashboard/_components/RefreshButton.tsx` (Client Component) + `endurance/src/app/api/dashboard/refresh/route.ts` (선택 — Server Action 대안) | **의존**: Foundation 09 sync-scheduler 재사용, Phase 1 02 `getDashboardSnapshot({ force: true })`

## Purpose

`/dashboard` 헤더에 **수동 Refresh 버튼**을 박는다. 클릭 시 02-data-api가 `force: true` 옵션으로 캐시 무시 + 외부 API 재페치 + ML inference 재호출 → 02 v2 응답을 새로 받아 SSR 재진입. 사용자가 시장 휴장일·캐시 만료 후 강제 갱신 필요 시 사용.

본 자산은 **Foundation 09 sync-scheduler 재사용** — 동일 sync 흐름을 수동 트리거로 호출. cron 자동 sync(Foundation 09) + 수동 Refresh(본 자산) 단일 진입점 (헌법 §2 SSOT).

## 의존성

- **사용하는 자산**:
  - Foundation 09 `sync-scheduler` (sync step 재사용 — Phase 0.5 01 데이터 수집 파이프라인이 sync step으로 등록됨)
  - Phase 1 02 `getDashboardSnapshot(market, { force: true })`
  - (선택) Server Action 또는 `/api/dashboard/refresh` Route Handler
- **이걸 사용하는 자산**: Phase 1 08 (Integration — 헤더 우측 배치, 자산 G)

## Public Interface

```typescript
// src/app/dashboard/_components/RefreshButton.tsx
"use client";

import type { DashboardMarket, ModelKind } from "@/lib/dashboard/data";

interface RefreshButtonProps {
  market: DashboardMarket;
  modelKind: ModelKind;
}

export function RefreshButton(props: RefreshButtonProps): JSX.Element;
```

표시 형태:

```
[ ↻ Refresh ]   ← 클릭 가능
[ ⟳ Loading... ] ← 로딩 중 (disabled + spinner)
[ ↻ Refresh ]   ← 완료 후 다시 enabled
```

data-testid: `widget-refresh`

### Server Action (선택)

```typescript
// src/app/dashboard/_actions.ts
"use server";

import { revalidatePath } from "next/cache";

export async function refreshDashboard(
  market: DashboardMarket,
  modelKind: ModelKind,
): Promise<{ ok: true; generatedAt: string } | { ok: false; error: string }>;
```

내부 흐름:
1. `getDashboardSnapshot(market, { force: true, modelKind })` 호출 (02 v2)
2. 성공 시 `revalidatePath("/dashboard")` 호출 — Next.js cache 무효화
3. 실패 시 `{ ok: false, error }` 반환 (silent fail 금지)

## Implementation Notes

- **Client Component**: 버튼 클릭 + 로딩 상태 관리 → `"use client"` 필수. Server Action 호출 또는 `/api/dashboard/refresh` fetch.
- **Server Action vs Route Handler**: Server Action이 단순 (revalidatePath 통합). Phase 1 초안 — Server Action 권장.
- **로딩 상태 (헌법 §0-1 Step 3 비동기)**:
  - 클릭 → `disabled=true` + spinner 표시
  - 성공 → `disabled=false` + 짧은 success 토스트 또는 silent
  - 실패 → error 토스트 + button 다시 enabled
- **AbortController**: 사용자가 빠르게 여러 번 클릭 시 이전 fetch 취소 (재진입 atomicity). `AbortController.abort()` + 새 요청.
- **재진입 atomicity**: 동일 market+model 중복 호출 시 in-flight dedup (02 의무, 본 위젯은 검증만).
- **Foundation 09 sync 흐름 재사용**: cron이 호출하는 sync step과 동일 진입점 (02 `getDashboardSnapshot`). cron + 수동이 같은 코드 경로 → SSOT (헌법 §2).
- **헌법 §6 escape hatch**: 없음. production 코드.

### 헌법 §0-1 Step 1 영향 분석

| 변경 대상 | 영향 |
|----------|------|
| 02 `getDashboardSnapshot({ force: true })` 옵션 | 본 자산이 호출. force 옵션 시그니처 변경 시 본 자산 갱신 |
| Foundation 09 sync-scheduler step 등록 | 본 자산이 cron과 단일 진입점 공유. sync step 시그니처 변경 시 양쪽 영향 |
| Next.js Server Action contract | 본 자산이 호출. Next.js 버전 업그레이드 시 영향 |

### 헌법 §0-1 Step 2 합리화 회피

- "Refresh 호출 시 yfinance/FX 클라이언트 직접 호출": ❌ SSOT 위반. 02-data-api 경유 의무
- "로딩 상태 생략 즉시 표시 갱신": ❌ 사용자 클릭 피드백 없음. UX 손실. spinner 의무
- "에러 시 silent fail": ❌ 사용자가 갱신 실패 인지 못 함. 토스트 또는 error 표시 의무

## Test Strategy

### 단위
- 버튼 클릭 → Server Action 호출 (mock) + disabled 상태 전환
- 성공 후 disabled=false + 토스트 표시
- 실패 시 error 토스트 + button enabled
- AbortController 빠른 더블 클릭 시 이전 호출 abort

### 표준 검증 시나리오 (헌법 §0-1 Step 3 — 비동기/Server Action)
- 정상 완료: 버튼 클릭 → revalidatePath → 페이지 데이터 갱신
- 언마운트 중 취소: 페이지 이탈 시 AbortController.abort
- 재진입 atomicity: 빠른 더블 클릭 시 외부 API 호출 ≤ 1
- 에러 경계: 02 reject 시 토스트 + button 복원, unhandled rejection 0건
- i18n: 마운트 중 언어 토글 시 "Refresh" / "새로고침" 자동 갱신 (caller-driven string 0건 grep)

## Verification

- [ ] `endurance/src/app/dashboard/_components/RefreshButton.tsx` 존재 + `"use client"` 디렉티브
- [ ] Server Action 또는 Route Handler `/api/dashboard/refresh` 존재 (둘 중 하나)
- [ ] data-testid `widget-refresh` 박힘
- [ ] `tsc --noEmit` 무경고
- [ ] 단위 테스트 6개 이상 (정상/실패/abort/재진입/disabled 전환/i18n)
- [ ] 02 `getDashboardSnapshot({ force: true })` 호출 검증 (grep)
- [ ] Foundation 09 sync-scheduler step 시그니처 재사용 검증
- [ ] anti-pattern §2-0-1 grep 0건 (라벨은 컴포넌트 내부 t() 또는 const, props로 string 받지 않음)
- [ ] unhandled rejection 0건 (에러 경계 처리 검증)

## Open Questions

1. **Refresh 빈도 제한**: 빠른 연타 시 API rate limit 위험. throttle 도입(예: 5초 cooldown)? 초안은 AbortController + dedup만, throttle은 Phase 2+.
2. **Success 토스트 vs silent**: 매번 토스트는 노이즈, silent는 갱신 인지 어려움. Phase 1 초안 — silent + `generatedAt` 표시 업데이트로 가시화.
3. **Server Action vs Route Handler 결정**: Server Action이 단순하나 외부 호출(e.g., curl)이 필요한 경우 Route Handler 필요. Phase 1 초안 — Server Action.
4. **로딩 spinner 위치**: 버튼 내부 vs 페이지 상단 progress bar — Phase 0.5 08 preview에서 결정.
