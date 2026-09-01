[← README로 돌아가기](../README.md)

# 어셈블리 경계가 강제하는 API 시그니처 — 반환 타입의 어셈블리를 먼저 본다

표현 계층이 호출할 API 를 설계할 때 **반환·인자 타입이 소속된 어셈블리를 먼저 확인**한다. asmdef references 는 컴파일러가 강제하는 계층 경계이고, 그 경계를 어기는 시그니처는 작성 시점에 잡지 않으면 **UI 배선 시점에** 터진다. Double Down 상점 각서(2026-09-01) 실측.

## 1. 인시던트

`ShopSession.BuyPackAndDraw()` (Application 계층) 가 도메인 타입 `HandUpgradeDefinition` 을 반환하도록 설계했다. 그러나:

```
DoubleDown.Presentation  → references: [Application, ...]   (Domain 없음)
DoubleDown.Boot.Scenes   → references: [Application, ...]   (Domain 없음)
```

UI 가 반환값을 받는 순간 Domain 참조가 필요해져 **호출 자체가 불가능**했다. 컴파일 전에 asmdef 를 읽어 발견 — 놓쳤다면 "왜 안 되지"가 배선 단계에서 터졌다.

## 2. 처방 3단계

1. **시그니처 확정 전 asmdef 대조** — 호출자 asmdef 의 `references` 에 반환·인자 타입의 어셈블리가 있는지 확인. 없으면 그 시그니처는 그 호출자에게 **존재하지 않는 API** 다
2. **경계를 넘는 선례를 먼저 grep** — 같은 경계를 이미 넘은 코드가 저장소에 있을 확률이 높다. 본 사례의 답은 `ScoreLineKind` — Domain 이 아니라 `Application/PresentationStep.cs` 에 있고 `HudWords` 가 표시 문구로 옮긴다
3. **표시용 값은 호출자가 닿는 계층의 struct 로** — `UpgradeOffer`(Application 계층, 도메인 타입 0)를 신설해 도메인 값을 표시용 필드로 변환. 참조를 늘리는 쪽(Presentation 에 Domain 추가)이 아니라 **타입을 낮은 결합 쪽으로 옮기는** 해법이 기본값

## 3. 왜 참조 추가가 아니라 타입 이동인가

- asmdef 참조 추가는 **경계 자체를 넓히는** 결정 — API 하나를 위해 계층 전체가 Domain 에 노출되고, 이후 모든 코드가 도메인 타입을 실수로 쓸 수 있게 된다
- 표시용 struct 는 그 API 하나의 폭만 노출 — 경계는 그대로, 값만 건넌다
- 참조 추가가 정당한 경우는 "이 계층이 원래 그 어셈블리를 알아야 했다"가 성립할 때뿐 — 그 판단은 시그니처 하나가 아니라 계층 설계 리뷰의 몫

## 종료 게이트

- [ ] 새 public API 의 반환·인자 타입 어셈블리를 호출자 asmdef `references` 와 대조했는가
- [ ] 경계를 넘는 기존 선례를 grep 했는가 (같은 경계, 같은 방향)
- [ ] 경계 위반 발견 시 참조 추가보다 표시용 struct 이동을 먼저 검토했는가

## 관련 문서

- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §0-1 Step 1 변경 전 영향 분석
- [unity-csharp-version-check.md](unity-csharp-version-check.md) — 작성 시점에 잡지 않으면 늦게 터지는 같은 계열 (컴파일 환경 제약)
