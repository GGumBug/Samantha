[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# Samantha 디자인 시스템 — Linear-Inspired Dark Canvas

이 디자인 시스템은 웹 팀 에이전트(Joi 우선)가 새 페이지·컴포넌트를 만들 때 따라야 할 **시각의 단일 진실 원천(SSOT)** 입니다. Linear 마케팅 캔버스의 다크 시스템에서 영감받았으며, 한국어 본문에 적합하도록 **Pretendard 폰트**로 적응됐습니다.

## 5대 원칙

1. **다크 캔버스가 곧 여백** — `{colors.canvas}` (#010102) 위에 surface ladder(1→4)로 위계를 표현. 그림자 의존 금지
2. **단일 색상 강조** — Linear 라벤더 블루(`{colors.primary}` #5e6ad2)는 브랜드 마크·1차 CTA·포커스 링·링크 강조에만. 두 번째 채도 색 도입 금지
3. **제품 스크린샷이 주인공** — 마케팅 크롬은 어두운 액자, 제품 UI 캡처가 의미를 옮긴다
4. **공격적 음수 트래킹** — display는 -3.0px(80px 기준)까지. body는 weight 400으로 잠근다
5. **`{rounded.md}` 8px CTA, `{rounded.lg}` 12px 카드** — 절대 pill 모양 CTA 금지

## 인덱스

| 영역 | 파일 | 핵심 결정 사항 |
|------|------|---------------|
| 색상 토큰 | [colors.md](colors.md) | Brand·Surface·Text·Semantic 4축 |
| 타이포그래피 | [typography.md](typography.md) | Pretendard 적용, hierarchy 13단계, 음수 트래킹 |
| 레이아웃 | [layout.md](layout.md) | Spacing 8단계, 1280px 컨테이너, 4단계 elevation, shapes 8단계 |
| 컴포넌트 | [components.md](components.md) | 버튼·카드·인풋·내비·푸터 명세 |
| 가이드라인 | [guidelines.md](guidelines.md) | Do's/Don'ts, 반응형, 반복 가이드 |
| 폰트 자산 | [fonts/Pretendard/](fonts/Pretendard/) | PretendardVariable.woff2 + 사용법 |

## 폰트 정책 (필수)

- **Display·Body**: Pretendard Variable (WOFF2) — `design-system/fonts/Pretendard/PretendardVariable.woff2`
- **Mono**: JetBrains Mono 또는 Geist Mono — 코드 스니펫 한정. CDN 또는 npm 패키지로 로드 가능
- 외부 CDN 의존 금지 — 폰트는 저장소 내 자체 호스팅이 SSOT

## 로고 정책

- **현재**: 로고 자리는 비어있게 디자인 (placeholder). 회사 로고가 결정되면 `design-system/assets/logo/` 에 추가
- **placeholder 치수**: 데스크톱 24px 높이 / 모바일 20px 높이 — Linear 스타일 wordmark 위치
- **임시 표기**: 로고 자리에 `[Brand]` 또는 빈 박스 — 텍스트 wordmark 가짜 레이블 금지

## 경계

- **모드**: 다크 모드 단일. 라이트 모드는 출시 안 함
- **색상 확장**: 채도 색 추가 금지(주황·분홍·녹색 등). 시맨틱 녹색(`{colors.semantic-success}` #27a644)만 status pill에 허용
- **장식 깊이**: 분위기 그라디언트·스포트라이트 카드 금지 — surface ladder + hairline 만으로 위계 표현

## 적용 대상

- 모든 마케팅 페이지·랜딩 페이지·문서 페이지
- 제품 내 UI는 별도 시스템 가능 (이슈 우선순위 색상 등 풍부한 팔레트 사용)
- 어드민 대시보드는 본 시스템을 기본으로 따르되 `{colors.semantic-*}` 확장 허용

## 변경 정책

- 토큰 변경은 **PR + 영향 받는 컴포넌트 grep 결과** 동반
- 새 컴포넌트는 `components.md`에 별도 엔트리로 추가, 기존 엔트리 확장 금지
- "Linear에서 본 X 변형" 같은 임시 변형은 도입 금지 — 시스템에 박혀야 함
