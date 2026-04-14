---
name: weather-svg-creator
description: 두바이의 현재 온도를 보여주는 SVG 날씨 카드를 생성합니다. SVG를 orchestration-workflow/weather.svg에 저장하고 orchestration-workflow/output.md를 업데이트합니다.
---

# 날씨 SVG 생성 스킬

두바이(UAE)의 시각적 SVG 날씨 카드를 생성하고 출력 파일을 작성합니다.

## 작업

호출 컨텍스트에서 온도 값과 단위(섭씨 또는 화씨)를 받습니다. SVG 날씨 카드를 생성하고 SVG와 마크다운 요약을 모두 작성합니다.

## 지침

1. **SVG 생성** — [reference.md](reference.md)의 SVG 템플릿을 사용하여 플레이스홀더를 실제 값으로 교체합니다
2. **SVG 파일 작성** — `orchestration-workflow/weather.svg`를 읽은 후 작성합니다
3. **요약 작성** — [reference.md](reference.md)의 마크다운 템플릿을 사용하여 `orchestration-workflow/output.md`를 읽은 후 작성합니다

## 규칙

- 제공된 온도 값과 단위를 그대로 사용합니다 — 다시 가져오거나 수정하지 않습니다
- SVG는 독립적이고 유효해야 합니다
- 두 출력 파일 모두 `orchestration-workflow/` 디렉토리에 저장합니다

## 추가 리소스

- SVG 템플릿, 출력 템플릿, 디자인 사양은 [reference.md](reference.md)를 참고합니다
- 입력/출력 예시는 [examples.md](examples.md)를 참고합니다
