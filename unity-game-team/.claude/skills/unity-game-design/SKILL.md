---
name: unity-game-design
description: Unity 게임 디자인 표준 참조 지식. Ava(게임 디자인/레벨 디자인)에 사전 로드됩니다. GDD 구조, 레벨 디자인 원칙, 게임 메카닉 설계 공식, 밸런스 수치 체계를 정의합니다.
user-invocable: false
---

# Unity 게임 디자인 표준

이 스킬은 Ava가 게임을 '시스템의 집합'으로 설계할 때 사용하는 표준 원칙과 템플릿입니다.

---

## 1. 게임 디자인 문서(GDD) 표준 구조

```markdown
# [게임명] — 게임 디자인 문서 (GDD)

## 1. 핵심 컨셉
- **장르**: (예: 2D 플랫포머, 탑다운 슈터, 퍼즐)
- **핵심 재미(Core Fun)**: 한 문장으로 표현
- **타깃 플레이어**: (연령대, 게이머 수준)
- **예상 플레이 시간**: (1회 세션 / 전체 클리어)
- **참조 게임**: (영감을 받은 타이틀 3개 이내)

## 2. 핵심 게임 루프 (Core Loop)
행동 → 결과 → 보상/패널티 → 다음 행동

## 3. 메카닉 목록
| 메카닉 | 설명 | 우선순위 | 구현 난이도 |
|-------|-----|---------|-----------|

## 4. 레벨 구성
| 레벨 | 목표 | 신규 도입 메카닉 | 난이도 |
|-----|-----|--------------|------|

## 5. 플레이어 스탯
| 스탯 | 기본값 | 최소 | 최대 | 비고 |
|-----|--------|-----|-----|-----|

## 6. Unity 씬 계층 구조

## 7. 프리팹 목록 (Sonny 구현용)

## 8. UI 요구사항 (Rachael 구현용)

## 9. 알려진 리스크
```

---

## 2. Jesse Schell의 렌즈(Lenses) 적용 체크리스트

기획서를 작성할 때 아래 렌즈로 교차 검증합니다:

| 렌즈 | 핵심 질문 |
|-----|---------|
| 재미의 렌즈 | "무엇이 재미있는가? 왜 재미있는가?" |
| 흐름의 렌즈 | "플레이어가 몰입 상태를 유지하는가?" |
| 균형의 렌즈 | "공정한가? 지루하지도, 좌절스럽지도 않은가?" |
| 기술의 렌즈 | "어떤 기술이 필요하며 성장감이 있는가?" |
| 경제의 렌즈 | "자원 관리 시스템이 충분히 흥미로운가?" |
| 시간의 렌즈 | "세션 길이가 적절한가?" |

---

## 3. 난이도 곡선 설계 공식

```
난이도 곡선 = 도전(Challenge) − 실력(Skill)

이상적 상태: 도전 ≈ 실력 (Flow 상태)
너무 쉬움: 도전 << 실력 → 지루함(Boredom)
너무 어려움: 도전 >> 실력 → 좌절(Frustration)
```

### 레벨별 난이도 수치 표준

```
레벨         1    2    3    4    5    Boss
적 수        3    5    7    8    10   1(강함)
적 체력      30   40   50   60   70   300
적 속도      2    2.5  3    3    3.5  4
플레이어 목숨  3    3    2    2    1    1
시간 제한(s)   -    -    120  90   60   -
```

---

## 4. 핵심 게임 루프 설계 패턴

### 마이크로 루프 (5~30초)
```
입력 → 즉각 피드백 → 소규모 보상
예: 공격 → 히트 이펙트/사운드 → 경험치 +1
```

### 메조 루프 (5분~1시간)
```
목표 → 진행 → 달성 → 언락
예: 레벨 클리어 → 새 스킬 해금
```

### 매크로 루프 (수 시간)
```
내러티브 진행 → 세계 확장 → 최종 보스
예: 챕터 클리어 → 스토리 전개
```

---

## 5. 데이터 계약 — Sonny에게 전달할 메카닉 스펙

```json
{
  "mechanics": [
    {
      "id": "player_jump",
      "type": "action",
      "trigger": "Space / Button_A",
      "condition": "IsGrounded == true",
      "effect": "AddForce(Vector2.up * jumpForce)",
      "parameters": {
        "jumpForce": 10.0,
        "maxJumps": 1
      }
    }
  ],
  "playerStats": {
    "maxHealth": 100,
    "moveSpeed": 5.0,
    "jumpForce": 10.0,
    "attackDamage": 25.0
  },
  "levelRules": {
    "winCondition": "reach_goal",
    "loseCondition": "health_zero",
    "timeLimit": 180
  }
}
```

---

## 6. 데이터 계약 — Rachael에게 전달할 UI 스펙

```json
{
  "screens": ["MainMenu", "GameHUD", "PauseMenu", "GameOver", "Victory"],
  "hudElements": [
    { "id": "healthBar", "type": "fillImage", "position": "topLeft" },
    { "id": "scoreDisplay", "type": "text", "position": "topCenter" },
    { "id": "livesDisplay", "type": "iconGroup", "position": "topRight" }
  ],
  "colorPalette": {
    "primary": "#E94560",
    "secondary": "#0F3460",
    "background": "#0D0D1A",
    "textPrimary": "#EAEAEA"
  }
}
```

---

## 7. 씬 계층 표준 (Unity 규칙)

```
[Scene]
├── _Managers           ← DontDestroyOnLoad 대상
│   ├── GameManager
│   ├── AudioManager
│   └── UIManager
├── _Environment
│   ├── Tilemap_Ground
│   ├── Tilemap_Platform
│   └── Background
├── _Gameplay
│   ├── Player (태그: Player)
│   ├── EnemySpawner
│   └── ItemSpawner
├── _UI
│   └── Canvas (Screen Space Overlay)
└── _Cameras
    └── Main Camera
```

---

## 8. 레벨 디자인 — 공간 언어 원칙

| 원칙 | 방법 |
|-----|-----|
| 시선 유도 | 조명, 색상, 크기 차이로 목표 지점 강조 |
| 안전 공간 | 위험 구간 전후에 플레이어가 숨을 고를 공간 제공 |
| 가르치기 전에 보여주기 | 새 메카닉은 실패해도 패널티 없는 단계에서 먼저 경험 |
| 3의 법칙 | 새 개념은 3번 반복 등장 (소개 → 응용 → 심화) |
