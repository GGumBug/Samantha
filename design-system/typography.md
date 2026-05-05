[← DESIGN.md로 돌아가기](DESIGN.md)

# Typography — 타이포그래피 (Pretendard 적응)

## 폰트 패밀리

| 용도 | 폰트 | 비고 |
|------|------|------|
| Display + Body | **Pretendard Variable** | `design-system/fonts/Pretendard/PretendardVariable.woff2` 자체 호스팅 |
| Mono | **JetBrains Mono** 또는 **Geist Mono** | 코드 스니펫 한정. npm 패키지 또는 자체 호스팅 |
| 폴백 (Display+Body) | `-apple-system, system-ui, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif` | Pretendard 로드 실패 시 |

### Pretendard 선택 이유

Linear의 커스텀 영문 폰트는 **한글 본문이 들어오면 일관성이 깨집니다**. Pretendard는:
- 영문 SF Pro Text와 거의 동일한 메트릭 (한·영 혼용 시 라인 베이스라인 일치)
- Variable 폰트 단일 파일(~700KB)에 weight 100~900 모두 포함
- 음수 트래킹에 안정적인 한글 자형
- 오픈소스 (SIL OFL)

Linear의 커스텀 폰트와 비교한 시각적 차이는 미미하며, 한국어 사용자 경험은 압도적으로 우수합니다.

### `font-family` 선언

```css
@font-face {
  font-family: 'Pretendard';
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
  src: url('/fonts/Pretendard/PretendardVariable.woff2') format('woff2-variations');
}

:root {
  --font-display: 'Pretendard', -apple-system, system-ui, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  --font-body: var(--font-display);
  --font-mono: 'JetBrains Mono', ui-monospace, "SF Mono", Menlo, monospace;
}
```

Display·Body는 동일 패밀리 — 변경은 silent.

## Hierarchy — 13단계

Pretendard 메트릭에 맞게 음수 트래킹을 약간 완화했습니다 (Linear 커스텀 폰트는 글리프 너비가 더 좁아 더 강한 음수 트래킹 가능 → Pretendard는 -2.5px 정도가 시각적 동등).

| 토큰 | Size | Weight | Line Height | Letter Spacing | 사용처 |
|------|------|--------|-------------|----------------|-------|
| `{typography.display-xl}` | 80px | 600 | 1.05 | -2.5px | 최대 히어로 헤드라인 |
| `{typography.display-lg}` | 56px | 600 | 1.10 | -1.6px | 섹션 오프너 헤드라인 |
| `{typography.display-md}` | 40px | 600 | 1.15 | -0.9px | 서브 섹션 헤드라인 |
| `{typography.headline}` | 28px | 600 | 1.20 | -0.5px | 가격 티어 타이틀, CTA 배너 |
| `{typography.card-title}` | 22px | 500 | 1.25 | -0.3px | 피처 카드 타이틀 |
| `{typography.subhead}` | 20px | 400 | 1.40 | -0.2px | 리드 본문, 서론 단락 |
| `{typography.body-lg}` | 18px | 400 | 1.50 | -0.1px | 히어로 서브헤드, 리드 단락 |
| `{typography.body}` | 16px | 400 | 1.50 | -0.05px | 기본 본문 |
| `{typography.body-sm}` | 14px | 400 | 1.50 | 0 | 카드 본문, 푸터 컬럼 |
| `{typography.caption}` | 12px | 400 | 1.40 | 0 | 캡션, 메타, status |
| `{typography.button}` | 14px | 500 | 1.20 | 0 | 모든 버튼 라벨 |
| `{typography.eyebrow}` | 13px | 500 | 1.30 | +0.4px | 섹션 eyebrow (양수 트래킹) |
| `{typography.mono}` | 13px | 400 | 1.50 | 0 | 코드 스니펫 |

## 원칙

- **공격적 음수 트래킹 (display)**: -2.5px / 80px ≈ 3% — Pretendard 안정 한계
- **단일 보이스**: display 600 ↔ body 400. 같은 패밀리, 다른 weight만으로 위계 표현
- **eyebrow는 양수 트래킹** (+0.4px) — 음수 트래킹 display와의 대비로 "분류 라벨"임을 시각적으로 표시
- **Mono는 코드 컨텍스트에만** — 마케팅 크롬에 mono 등장 금지
- **700+ display weight 금지** — Linear의 절제된 무게감 유지. 가독성 강조가 필요하면 size를 키울 것

## 한글 특수 사항

- **Pretendard는 한글 자간이 살짝 좁음** — 음수 트래킹 적용 시 자간 충돌 가능. `display-xl`에서 한글 단어 시각 검토 필수
- **숫자 디스플레이**: Pretendard는 표준 숫자(proportional). 표 정렬 필요 시 `font-feature-settings: 'tnum'` 명시
- **한자·기호 혼용**: Pretendard 자체 한자 글리프 사용. 추가 폰트 폴백 불필요

## 구현 체크리스트

- [ ] `@font-face` 선언이 `font-display: swap` 포함 — FOIT(Flash of Invisible Text) 방지
- [ ] `font-weight` 범위가 `100 900` — Variable 활성화
- [ ] CLS 방지: `font-display: swap` + `<html lang="ko">` 명시
- [ ] preload: `<link rel="preload" href="/fonts/Pretendard/PretendardVariable.woff2" as="font" type="font/woff2" crossorigin>`
- [ ] Tailwind v4 `@theme`에서 `--font-display`, `--font-mono` 노출 → `font-display`, `font-mono` 유틸리티 사용
