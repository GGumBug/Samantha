---
name: agent-browser
description: AI 에이전트를 위한 브라우저 자동화 CLI. 사용자가 웹사이트와 상호작용해야 할 때 사용합니다. 페이지 탐색, 폼 작성, 버튼 클릭, 스크린샷 촬영, 데이터 추출, 웹 앱 테스트, 또는 브라우저 작업 자동화 등에 활용합니다. "웹사이트 열기", "폼 입력", "버튼 클릭", "스크린샷 찍기", "페이지에서 데이터 스크래핑", "웹 앱 테스트", "사이트 로그인", "브라우저 동작 자동화" 등 프로그래밍 방식의 웹 상호작용이 필요한 모든 작업에 사용합니다.
allowed-tools: Bash(agent-browser:*)
---

# agent-browser를 이용한 브라우저 자동화

## 핵심 워크플로우

모든 브라우저 자동화는 다음 패턴을 따릅니다:

1. **탐색**: `agent-browser open <url>`
2. **스냅샷**: `agent-browser snapshot -i` (`@e1`, `@e2` 같은 요소 참조 획득)
3. **상호작용**: 참조를 사용해 클릭, 입력, 선택
4. **재스냅샷**: 페이지 이동 또는 DOM 변경 후 새 참조 획득

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# 출력: @e1 [input type="email"], @e2 [input type="password"], @e3 [button] "Submit"

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # 결과 확인
```

## 주요 명령어

```bash
# 탐색
agent-browser open <url>              # 탐색 (별칭: goto, navigate)
agent-browser close                   # 브라우저 닫기

# 스냅샷
agent-browser snapshot -i             # 참조가 있는 인터랙티브 요소 (권장)
agent-browser snapshot -i -C          # 커서 인터랙티브 요소 포함 (onclick, cursor:pointer가 있는 div)
agent-browser snapshot -s "#selector" # CSS 선택자 범위로 한정

# 상호작용 (스냅샷의 @refs 사용)
agent-browser click @e1               # 요소 클릭
agent-browser fill @e2 "텍스트"       # 기존 내용 지우고 텍스트 입력
agent-browser type @e2 "텍스트"       # 내용 지우지 않고 텍스트 입력
agent-browser select @e1 "옵션"       # 드롭다운 옵션 선택
agent-browser check @e1               # 체크박스 선택
agent-browser press Enter             # 키 누르기
agent-browser scroll down 500         # 페이지 스크롤

# 정보 가져오기
agent-browser get text @e1            # 요소 텍스트 가져오기
agent-browser get url                 # 현재 URL 가져오기
agent-browser get title               # 페이지 제목 가져오기

# 대기
agent-browser wait @e1                # 요소 대기
agent-browser wait --load networkidle # 네트워크 유휴 상태 대기
agent-browser wait --url "**/page"    # URL 패턴 대기
agent-browser wait 2000               # 밀리초 대기

# 캡처
agent-browser screenshot              # 임시 디렉토리에 스크린샷 저장
agent-browser screenshot --full       # 전체 페이지 스크린샷
agent-browser pdf output.pdf          # PDF로 저장
```

## 자주 사용하는 패턴

### 폼 제출

```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"
agent-browser check @e4
agent-browser click @e5
agent-browser wait --load networkidle
```

### 상태 저장을 통한 인증

```bash
# 한 번 로그인 후 상태 저장
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# 이후 세션에서 재사용
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

### 데이터 추출

```bash
agent-browser open https://example.com/products
agent-browser snapshot -i
agent-browser get text @e5           # 특정 요소 텍스트 가져오기
agent-browser get text body > page.txt  # 페이지 전체 텍스트 가져오기

# 파싱을 위한 JSON 출력
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

### 병렬 세션

```bash
agent-browser --session site1 open https://site-a.com
agent-browser --session site2 open https://site-b.com

agent-browser --session site1 snapshot -i
agent-browser --session site2 snapshot -i

agent-browser session list
```

### 시각적 브라우저 (디버깅)

```bash
agent-browser --headed open https://example.com
agent-browser highlight @e1          # 요소 강조 표시
agent-browser record start demo.webm # 세션 녹화
```

### 로컬 파일 (PDF, HTML)

```bash
# file:// URL로 로컬 파일 열기
agent-browser --allow-file-access open file:///path/to/document.pdf
agent-browser --allow-file-access open file:///path/to/page.html
agent-browser screenshot output.png
```

### iOS 시뮬레이터 (모바일 Safari)

```bash
# 사용 가능한 iOS 시뮬레이터 목록 조회
agent-browser device list

# 특정 기기에서 Safari 실행
agent-browser -p ios --device "iPhone 16 Pro" open https://example.com

# 데스크톱과 동일한 워크플로우 - 스냅샷, 상호작용, 재스냅샷
agent-browser -p ios snapshot -i
agent-browser -p ios tap @e1          # 탭 (클릭의 별칭)
agent-browser -p ios fill @e2 "텍스트"
agent-browser -p ios swipe up         # 모바일 전용 제스처

# 스크린샷 촬영
agent-browser -p ios screenshot mobile.png

# 세션 종료 (시뮬레이터 종료)
agent-browser -p ios close
```

**요구사항:** Xcode가 설치된 macOS, Appium (`npm install -g appium && appium driver install xcuitest`)

**실제 기기:** 사전 설정된 경우 물리적 iOS 기기에서도 작동합니다. `xcrun xctrace list devices`에서 얻은 UDID를 사용하여 `--device "<UDID>"`를 지정하세요.

## 참조(Ref) 수명 주기 (중요)

참조(`@e1`, `@e2` 등)는 페이지가 변경되면 무효화됩니다. 다음 상황 후에는 반드시 재스냅샷 하세요:

- 페이지를 이동하는 링크나 버튼 클릭
- 폼 제출
- 동적 콘텐츠 로딩 (드롭다운, 모달)

```bash
agent-browser click @e5              # 새 페이지로 이동
agent-browser snapshot -i            # 반드시 재스냅샷
agent-browser click @e1              # 새 참조 사용
```

## 시맨틱 로케이터 (참조의 대안)

참조를 사용할 수 없거나 신뢰할 수 없는 경우 시맨틱 로케이터를 사용하세요:

```bash
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find role button click --name "Submit"
agent-browser find placeholder "Search" type "query"
agent-browser find testid "submit-btn" click
```
