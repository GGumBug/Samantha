[← DESIGN.md로 돌아가기](../../DESIGN.md)

# Pretendard Variable — 폰트 자산

## 파일

| 파일 | 용도 |
|------|------|
| `PretendardVariable.woff2` | Display·Body 폰트 (weight 100~900 단일 파일, ~2MB) |
| `LICENSE.txt` | SIL Open Font License (OFL-1.1) — 상업 사용 가능 |

## 버전

Pretendard 1.3.9 (2024). 원본: https://github.com/orioncactus/pretendard

## 웹 프로젝트 통합 가이드

### 1. 폰트 파일 배치

웹 프로젝트의 정적 자산 디렉토리(`public/fonts/Pretendard/` 또는 Next.js `app/fonts/`)에 `PretendardVariable.woff2`를 복사. 본 저장소(`design-system/fonts/Pretendard/`)는 SSOT이며, 실제 웹 앱은 빌드 시 이를 참조.

### 2. `@font-face` 선언

`globals.css` 또는 별도 `fonts.css`:

```css
@font-face {
  font-family: 'Pretendard';
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
  src: url('/fonts/Pretendard/PretendardVariable.woff2') format('woff2-variations');
}
```

### 3. CSS 변수 등록

```css
:root {
  --font-display: 'Pretendard', -apple-system, system-ui,
                  "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  --font-body: var(--font-display);
  --font-mono: 'JetBrains Mono', ui-monospace, "SF Mono", Menlo, monospace;
}

body {
  font-family: var(--font-body);
}
```

### 4. Tailwind v4 통합

```css
@theme {
  --font-display: 'Pretendard', -apple-system, system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
}
```

이렇게 하면 `font-display`, `font-mono` 유틸리티가 작동합니다.

### 5. 성능 최적화

#### Preload (권장)

`<head>`에 추가하여 LCP(Largest Contentful Paint) 개선:

```html
<link rel="preload"
      href="/fonts/Pretendard/PretendardVariable.woff2"
      as="font"
      type="font/woff2"
      crossorigin>
```

Next.js App Router에서:

```tsx
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="preload"
          href="/fonts/Pretendard/PretendardVariable.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

#### Next.js `next/font/local` 사용

빌드 타임 최적화·CLS 방지·자동 preload:

```tsx
// app/layout.tsx
import localFont from 'next/font/local';

const pretendard = localFont({
  src: './fonts/Pretendard/PretendardVariable.woff2',
  display: 'swap',
  weight: '100 900',
  variable: '--font-display',
});

export default function RootLayout({ children }) {
  return (
    <html lang="ko" className={pretendard.variable}>
      <body className="font-display">{children}</body>
    </html>
  );
}
```

이 방식이 **권장** — Next.js가 자동으로 preload·CLS 방지·서브셋 처리.

## Variable 폰트 활용

Pretendard Variable은 단일 파일에서 weight 100~900을 모두 지원합니다.

```css
.weight-100 { font-weight: 100; }  /* Thin */
.weight-200 { font-weight: 200; }  /* ExtraLight */
.weight-300 { font-weight: 300; }  /* Light */
.weight-400 { font-weight: 400; }  /* Regular */
.weight-500 { font-weight: 500; }  /* Medium */
.weight-600 { font-weight: 600; }  /* SemiBold */
.weight-700 { font-weight: 700; }  /* Bold */
.weight-800 { font-weight: 800; }  /* ExtraBold */
.weight-900 { font-weight: 900; }  /* Black */
```

또는 정밀 보간:

```css
.weight-650 { font-weight: 650; }  /* SemiBold ↔ Bold 사이 */
```

## 디자인 시스템 약속

- **권장 weight 범위**: 400(Body), 500(Button/Eyebrow), 600(Display) — `typography.md` 참조
- **700+ display weight 금지** — 절제된 위계 유지
- **숫자 정렬 필요 시**: `font-feature-settings: 'tnum'` 명시 (Pretendard는 기본 proportional)

## 라이선스 요약

SIL Open Font License 1.1 — 상업·개인·수정 사용 모두 허용. 단, 폰트 자체를 판매하는 것 금지. 자세한 사항은 `LICENSE.txt` 참조.
