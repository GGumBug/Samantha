# Claude 메모리

CLAUDE.md 파일을 통한 영구 컨텍스트 — 작성 방법과 모노레포에서의 로딩 방식.

<table width="100%">
<tr>
<td><a href="../">← Claude Code 모범 사례로 돌아가기</a></td>
<td align="right"><img src="../!/claude-jumping.svg" alt="Claude" width="60" /></td>
</tr>
</table>

---

## 1. 좋은 CLAUDE.md 작성하기

잘 구조화된 CLAUDE.md는 프로젝트에서 Claude Code의 출력을 향상시키는 단일 가장 영향력 있는 방법입니다. Humanlayer에 포함할 내용, 구조화 방법, 일반적인 함정을 다루는 훌륭한 가이드가 있습니다.

- [Humanlayer - 좋은 Claude.md 작성하기](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

---

## 2. 대규모 모노레포에서의 CLAUDE.md

모노레포에서 Claude Code를 사용할 때, CLAUDE.md 파일이 컨텍스트에 로드되는 방식을 이해하는 것은 프로젝트 지침을 효과적으로 구성하는 데 중요합니다.

<p align="center">
  <a href="https://x.com/bcherny/status/2016339448863355206"><img src="assets/claude-memory/claude-memory-monorepo.jpg" alt="모노레포에서의 CLAUDE.md 로딩" width="600"></a>
</p>

### 두 가지 로딩 메커니즘

Claude Code는 CLAUDE.md 파일을 로드하기 위해 두 가지 별개의 메커니즘을 사용합니다:

#### 조상 로딩 (디렉토리 트리 위쪽)

Claude Code를 시작하면 현재 작업 디렉토리에서 파일시스템 루트 방향으로 **위쪽**으로 걸어 올라가며 발견하는 모든 CLAUDE.md를 로드합니다. 이 파일들은 **시작 시 즉시 로드**됩니다.

#### 후손 로딩 (디렉토리 트리 아래쪽)

현재 작업 디렉토리 아래 하위 디렉토리의 CLAUDE.md 파일은 **시작 시 로드되지 않습니다**. 세션 중 해당 하위 디렉토리의 파일을 읽을 때만 포함됩니다. 이를 **지연 로딩**이라 합니다.

### 예시 모노레포 구조

다른 컴포넌트를 위한 별도 디렉토리가 있는 일반적인 모노레포를 고려해보세요:

```
/mymonorepo/
├── CLAUDE.md          # 루트 수준 지침 (모든 컴포넌트에 공유)
├── frontend/
│   └── CLAUDE.md      # 프론트엔드 전용 지침
├── backend/
│   └── CLAUDE.md      # 백엔드 전용 지침
└── api/
    └── CLAUDE.md      # API 전용 지침
```

### 시나리오 1: 루트 디렉토리에서 Claude Code 실행

`/mymonorepo/`에서 Claude Code를 실행할 때:

```bash
cd /mymonorepo
claude
```

| 파일 | 시작 시 로드? | 이유 |
|------|------------|------|
| `/mymonorepo/CLAUDE.md` | 예 | 현재 작업 디렉토리 |
| `/mymonorepo/frontend/CLAUDE.md` | 아니요 | `frontend/` 내 파일을 읽거나 편집할 때만 로드 |
| `/mymonorepo/backend/CLAUDE.md` | 아니요 | `backend/` 내 파일을 읽거나 편집할 때만 로드 |
| `/mymonorepo/api/CLAUDE.md` | 아니요 | `api/` 내 파일을 읽거나 편집할 때만 로드 |

### 시나리오 2: 컴포넌트 디렉토리에서 Claude Code 실행

`/mymonorepo/frontend/`에서 Claude Code를 실행할 때:

```bash
cd /mymonorepo/frontend
claude
```

| 파일 | 시작 시 로드? | 이유 |
|------|------------|------|
| `/mymonorepo/CLAUDE.md` | 예 | 조상 디렉토리 |
| `/mymonorepo/frontend/CLAUDE.md` | 예 | 현재 작업 디렉토리 |
| `/mymonorepo/backend/CLAUDE.md` | 아니요 | 다른 디렉토리 트리 분기 |
| `/mymonorepo/api/CLAUDE.md` | 아니요 | 다른 디렉토리 트리 분기 |

### 핵심 요점

1. **조상은 항상 시작 시 로드됩니다** — Claude는 디렉토리 트리를 위쪽으로 걸어 올라가며 발견하는 모든 CLAUDE.md 파일을 로드합니다. 이는 루트 수준, 저장소 전체 지침에 항상 접근할 수 있도록 보장합니다.

2. **후손은 지연 로딩됩니다** — 하위 디렉토리 CLAUDE.md 파일은 해당 하위 디렉토리의 파일과 상호작용할 때만 로드됩니다. 이는 관련 없는 컨텍스트가 세션을 부풀리는 것을 방지합니다.

3. **형제는 절대 로드되지 않습니다** — `frontend/`에서 작업 중이라면 `backend/CLAUDE.md` 또는 `api/CLAUDE.md`가 컨텍스트에 로드되지 않습니다.

4. **전역 CLAUDE.md** — 홈 폴더의 `~/.claude/CLAUDE.md`에 CLAUDE.md를 배치하면 프로젝트에 관계없이 모든 Claude Code 세션에 적용됩니다.

### 이 설계가 모노레포에 효과적인 이유

- **공유 지침이 아래로 전파됩니다** — 루트 수준 CLAUDE.md에는 모든 곳에 적용되는 저장소 전체 관례, 코딩 표준, 공통 패턴이 포함됩니다.

- **컴포넌트별 지침이 격리됩니다** — 프론트엔드 개발자는 백엔드 특정 지침이 컨텍스트를 어지럽히는 것이 필요 없고, 그 반대도 마찬가지입니다.

- **컨텍스트가 최적화됩니다** — 후손 CLAUDE.md 파일을 지연 로딩함으로써 Claude Code는 시작 시 잠재적으로 수백 킬로바이트의 관련 없는 지침을 로드하는 것을 피합니다.

### 모범 사례

1. **공유 관례를 루트 CLAUDE.md에 넣으세요** — 코딩 표준, 커밋 메시지 형식, PR 템플릿, 기타 저장소 전체 지침.

2. **컴포넌트별 지침을 컴포넌트 CLAUDE.md에 넣으세요** — 프레임워크별 패턴, 컴포넌트 아키텍처, 해당 컴포넌트에 고유한 테스트 관례.

3. **개인 선호도에는 CLAUDE.local.md를 사용하세요** — 팀과 공유해서는 안 되는 지침을 위해 `.gitignore`에 추가하세요.

---

## 출처

- [Claude Code 공식 문서 - 메모리 조회 방법](https://code.claude.com/docs/en/memory#how-claude-looks-up-memories)
- [Boris Cherny의 X - CLAUDE.md 로딩 설명](https://x.com/bcherny/status/2016339448863355206)
- [Humanlayer - 좋은 Claude.md 작성하기](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
