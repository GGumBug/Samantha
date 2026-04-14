# Unity Game Development Team

이 디렉토리는 Unity 게임 개발을 위한 에이전트 팀의 루트입니다.
`cd unity-game-team && claude`로 실행하면 팀 전체가 활성화됩니다.

## 팀 구성

| 에이전트 | 영화 출처 | 역할 |
|---------|----------|------|
| **Samantha** | *Her* (2013) | 👑 팀장 — 오케스트레이션, 작업 분배, 통합 |
| **Ava** | *Ex Machina* (2015) | 🎨 게임 디자인 & 레벨 디자인 |
| **Sonny** | *I, Robot* (2004) | 💻 게임플레이 프로그래밍 (C#) |
| **Rachael** | *Blade Runner* (1982) | 🖼️ UI/UX & 셰이더 |
| **TARS** | *Interstellar* (2014) | 🔧 시스템 아키텍처 & 최적화 |
| **Bishop** | *Aliens* (1986) | 🎵 콘텐츠 통합 & QA |

## 협업 흐름

```
사용자 요청
    │
    ▼
Samantha (팀장) ─── 작업 분배 ───┬── Ava      (디자인)
                                 ├── Sonny    (프로그래밍)
                                 ├── Rachael  (UI/비주얼)
                                 ├── TARS     (시스템)
                                 └── Bishop   (QA)
                                      │
                                 결과 취합
                                      │
                                 Samantha (최종 검토 & 통합)
```

## 핵심 원칙

- **Samantha**가 작업을 분배하고 최종 통합을 담당합니다
- 의존성 없는 작업(UI, 게임플레이)은 병렬로 진행합니다
- **Bishop**은 항상 마지막에 QA 검증을 수행합니다
- 에이전트 간 통신은 `Agent` 도구를 사용합니다 (bash 명령 금지)

## 파일 구조

```
unity-game-team/
├── CLAUDE.md                    ← 이 파일
├── .claude/
│   ├── agents/
│   │   ├── samantha.md          ← 팀장
│   │   ├── ava.md               ← 디자인
│   │   ├── sonny.md             ← 프로그래밍
│   │   ├── rachael.md           ← UI/셰이더
│   │   ├── tars.md              ← 시스템/최적화
│   │   └── bishop.md            ← QA
│   ├── commands/
│   │   └── unity-dev.md         ← 개발 워크플로우 진입점
│   └── skills/
│       ├── unity-patterns/      ← Unity C# 패턴 참조
│       ├── unity-ui-standards/  ← UI 표준
│       └── unity-qa-checklist/  ← QA 체크리스트
└── output/                      ← 생성된 게임 파일 출력
```
