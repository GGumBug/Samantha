[← CLAUDE.md로 돌아가기](../CLAUDE.md)

# Unity C# 버전 사전 검증

Unity 환경의 C# LangVersion은 Unity 버전에 종속된다. 모던 C# 기능을 무심코 사용하면 컴파일 실패 — 사전 검증 의무.

## Unity 버전 → C# LangVersion 기본값

| Unity 버전 | C# LangVersion (default) | 주요 미지원 |
|------------|--------------------------|-------------|
| 2021.3 LTS | C# 9.0 | record class/struct, required member, file-scoped types |
| 2022.3 LTS | C# 9.0 | record struct (C# 10+), required (C# 11+) |
| 2023.x | C# 9.0 | 동일 |
| 6.0 (2024+) | C# 9.0 (default), 일부 빌드는 10+ 가능 | 확인 필요 |

**중요**: Unity는 자체 컴파일 파이프라인 사용 — 시스템 dotnet 버전과 무관. `.csproj` 자동 생성도 LangVersion 9.0 기본.

## 사전 검증 체크리스트 (Plan 시점)

모던 C# 기능 사용 plan 작성 직전:

- [ ] **Unity 버전 확인** — Editor 좌상단 또는 `ProjectSettings/ProjectVersion.txt`
- [ ] **LangVersion 기본값 확인** — `Library/PlayerScriptAssemblies/*.csproj`의 `<LangVersion>`
- [ ] **사용 기능 호환성 확인** — record struct (C# 10), required (C# 11), file-scoped types (C# 11)
- [ ] **override 필요 시 `Assets/csc.rsp` 작성** — `-langversion:11` 등 (지원 검증 필요)
- [ ] **사전 mini 컴파일 검증** — 1줄 사용 후 Unity 콘솔 컴파일 성공 확인 후 본 작업 진행

## 본 세션 사고 사례 — CS8773

`record struct ImmutableEntityViewModel(...)` 도입 → Unity 2022.3 LTS 환경에서 **CS8773 LangVersion 9.0 미지원** 컴파일 실패.

**복구**:
```csharp
// 다운그레이드 — record struct → readonly struct
public readonly struct ImmutableEntityViewModel
{
    public readonly int Id;
    public readonly string Name;
    public ImmutableEntityViewModel(int id, string name) { Id = id; Name = name; }
}
```

**근본 원인**: plan 단계에서 LangVersion 미확인. 모던 C# 기능 사용 시 사전 컴파일 검증 단계 누락.

## 모던 C# 기능별 호환성 매트릭스

| 기능 | LangVersion | Unity 2022.3 LTS 기본 |
|------|-------------|------------------------|
| record class | C# 9.0 | OK |
| init-only setter | C# 9.0 | OK |
| target-typed new | C# 9.0 | OK |
| record struct | C# 10.0 | NG (csc.rsp override 필요) |
| file-scoped namespace | C# 10.0 | NG |
| required member | C# 11.0 | NG |
| primary constructor (class) | C# 12.0 | NG |
| collection expression `[1, 2, 3]` | C# 12.0 | NG |

## 안전 대안 (LangVersion 9.0 호환)

| 원하는 기능 | 9.0 호환 대안 |
|-------------|----------------|
| record struct | readonly struct + 수동 Equals/HashCode |
| required | constructor 강제 + private setter |
| file-scoped namespace | 일반 namespace block |
| collection expression | `new List<T> { ... }` |

## 참고

- [.claude/rules/unity-delegation.md](../.claude/rules/unity-delegation.md) — 리팩토링 위임 체크리스트
- [refactoring-lessons.md](refactoring-lessons.md) — 일반 리팩토링 교훈
