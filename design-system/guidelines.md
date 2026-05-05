[← DESIGN.md로 돌아가기](DESIGN.md)

# Guidelines — Do's/Don'ts·반응형·반복

## Do's — 따라야 할 것

- ✅ `{colors.canvas}` (#010102)을 시스템의 앵커 표면으로 보존 — 미세한 푸른 틴트는 의도적
- ✅ `{colors.primary}` 라벤더는 **오직** 브랜드 마크·1차 CTA·포커스 링·링크 강조에만
- ✅ Surface ladder 4단계(canvas → 1 → 2 → 3 → 4)로 위계 표현. 단계 건너뛰기 지양
- ✅ Display weight 600과 Body weight 400 페어링 — Linear 절제된 무게감
- ✅ Display에 공격적 음수 트래킹 적용 (Pretendard 기준 -2.5px @ 80px)
- ✅ 모든 섹션의 주인공으로 제품 UI 스크린샷 사용
- ✅ CTA는 `{rounded.md}` 8px 코너로 통일
- ✅ Pretendard Variable 단일 파일 자체 호스팅 — CDN 의존 금지

## Don'ts — 절대 금지

- ❌ 라이트 모드 마케팅 페이지 출시 금지
- ❌ 라벤더를 섹션 배경·카드 fill로 사용 금지
- ❌ 두 번째 채도 액센트(주황·분홍·녹색 등) 도입 금지 — 시맨틱 녹색만 status pill에 허용
- ❌ 분위기 그라디언트·스포트라이트 카드 추가 금지
- ❌ CTA 버튼을 pill 형태로 만들지 말 것 (`{rounded.pill}`은 가격 탭·status에만)
- ❌ `#000000` 순수 검정을 캔버스로 사용 금지 — 항상 `#010102`
- ❌ 제품 스크린샷 mockup에 여러 밝은 채도 색 조합 금지
- ❌ Pretendard 외 한글 폰트 도입 금지 (Apple SD Gothic·Malgun은 폴백 한정)

## Responsive Behavior

### Breakpoints

| 이름 | 폭 | 주요 변경 |
|------|-----|---------|
| Desktop-XL | 1440px | 기본 데스크톱 레이아웃 |
| Desktop | 1280px | 카드 그리드 3-up 유지 |
| Tablet | 1024px | 카드 그리드 3-up → 2-up |
| Mobile-Lg | 768px | 가격 비교 → 아코디언; 내비 햄버거 |
| Mobile | 480px | 단일 컬럼; display-xl 80px → ~36px |

### Touch Targets

- CTA: 모든 뷰포트에서 ≥40px tap height
- 가격 탭 pill: ≥36px tap height (터치 시 ≥44px)
- 폼 인풋: 터치 시 ≥44px

### Collapsing 전략

- **Top nav**: 768px 이하에서 링크 → 햄버거
- **카드 그리드**: 3-up → 2-up (1024px) → 1-up (768px 이하)
- **가격 비교**: 768px 이하 티어별 아코디언
- **Display 타입**: `{typography.display-xl}` 80px → `{typography.display-md}` 40px (모바일)

### 이미지 동작

- 제품 UI 스크린샷: aspect ratio 보존, crop 금지
- 고객사 로고 마키: 768px 이하 6-up → 3-up

## 반복 가이드 (Iteration Guide)

새 페이지/섹션 작업 시 다음 순서로 의사결정:

1. **컴포넌트 단위 집중**: 한 번에 하나의 컴포넌트만 수정. 토큰 이름으로 참조 (`button-primary` 등)
2. **섹션 surface 결정 먼저**: 새 섹션 도입 시 어느 surface 단계 위에 살지부터 결정 (canvas vs surface-1 vs surface-2)
3. **Body는 `{typography.body}` weight 400 기본**: 다른 사이즈는 명시적 이유 있을 때만
4. **새 변형은 별도 컴포넌트 엔트리**: 기존 엔트리 확장 금지 — `components.md`에 새 항목 추가
5. **라벤더는 희소 자원**: 브랜드 마크·1차 CTA·포커스·링크 강조 외에 사용 시 트레이드오프 보고
6. **모든 섹션은 제품 UI 스크린샷으로 시작**: "텍스트만으로 시작하지 말 것"

## 알려진 갭 (Known Gaps)

- 4단계 surface ladder의 정확한 hex 값은 Linear의 `--color-bg-level-3` 등 CSS 변수에서 추출 — Linear의 정식 surface 스펙
- 폼 필드 에러·검증 스타일링은 inspect한 페이지에 노출 안 됨 — 도입 시 `components.md`에 추가
- 라이트 모드 미정의 — 마케팅 사이트가 라이트 테마 출시 안 함
- 제품 내 UI는 풍부한 색상 태그 팔레트(red·orange·yellow·green·blue·purple) 사용 — 본 시스템과 별개
- Linear의 커스텀 display·text·mono 폰트는 비공개 — Pretendard로 적응. 영문 메트릭은 SF Pro Text와 거의 동일

## 검증 체크리스트 (PR 게이트)

새 컴포넌트/섹션 작업 후 PR 전 자가 점검:

- [ ] 모든 색상이 `{colors.*}` 토큰 사용 — `bg-[#xxx]` 임의 색 0건
- [ ] 모든 타이포가 `{typography.*}` 토큰 사용 — `text-[18px]` 임의 사이즈 0건
- [ ] 라벤더 사용처가 4가지(브랜드·1차 CTA·포커스·링크) 안에 있음
- [ ] 다크 모드만 — 라이트 토큰 0건
- [ ] 반응형 3 지점(375 / 768 / 1280) 시각 검증
- [ ] 접근성: 탭 키만으로 모든 인터랙션 도달, 포커스 인디케이터 가시
- [ ] 브라우저 검증 완료 (`npm run dev` 실제 확인)

## 변경 정책

- 토큰 추가/수정은 PR + 영향 받는 컴포넌트 grep 결과 동반 의무
- "임시 변형" 도입 금지 — 시스템에 박힌 컴포넌트로 추가하거나 도입하지 말 것
- Pretendard 외 폰트 도입은 디자인 헌법 변경 — 별도 RFC 필요
