[← README로 돌아가기](../README.md)

# 단언의 판별력 — 부정형은 틀린 값의 목록이고, 판별력은 대역 데이터에서 나온다

상점의 작업패 카드가 **이름 글자** 대신 **실제 화투 앞면 스프라이트**를 세우도록 바꾸며 시험을 고친 실측(2026-09-09, Double Down 상점 카드 표시). 단언문을 강하게 쓰는 것만으로는 판별력이 생기지 않고, 그 단언이 딛는 **대역 데이터가 서로 구별될 때만** 무언가를 가른다.

## 1. 부정형 단언은 틀린 값의 목록을 손으로 적는 것이다

옛 단언은 이름 문자열을 부정형 3연으로 물었다:

```csharp
string name = ReadField<TextMeshProUGUI>(card, "_cardLabel").text;
Assert.That(name, Is.Not.Empty, ...);                       // 비지 않음
Assert.That(name, Is.Not.EqualTo(offer.CardStableId), ...); // 키를 그대로 올리지 않음
Assert.That(name, Is.Not.EqualTo(MissingCardCaption), ...); // 자리표가 아님
```

셋 다 "이것은 아니어야 한다"뿐이라 **목록 밖의 틀림**을 전부 통과시킨다. 실제로 통과하던 결함: **칸끼리 얼굴이 뒤바뀜**(0번 칸에 1번 패). 그 값은 비어 있지도, 키도, 자리표도 아니므로 세 단언을 전부 만족한다.

이것은 [hand-listed-roster-decay.md](hand-listed-roster-decay.md) 가 다루는 **손 명부**의 단언 판이다 — 명부가 대상 목록이면 조용히 낡고, 명부가 "틀린 값 목록"이면 조용히 통과한다.

처방: **"무엇이 아닌가"가 아니라 "무엇인가"를 문다.** 기대값은 계산이 아니라 **정본에서 파생**해 시험이 자기 식을 세우지 않게 한다.

```csharp
Image face = ReadField<Image>(card, "_faceImage");
_cardSpriteTable.TryGetFront(offer.DefinitionId, out Sprite expectedFace);
Assert.That(face.sprite, Is.SameAs(expectedFace), ...);   // 표에서 그 id로 꺼낸 인스턴스 자체
Assert.That(face.enabled, Is.True, ...);
```

## 2. (더 중요) 판별력은 단언문이 아니라 대역 데이터의 다양성에서 온다

동일성 단언으로 바꾼 것만으로는 반쪽이었다. 이 저장소의 기존 대역 표 선례(`PpeokLockUnderlineTests`)는 **48칸에 `Sprite` 하나를 나눠 쓴다**:

```csharp
for (int month = 1; month <= 12; month++)
    for (int slot = 1; slot <= 4; slot++)
        entries.Add(new CardSpriteEntry(month * 100 + slot, _sprite));  // ← 같은 인스턴스
```

그 표 위에서는 `Is.SameAs` 조차 **아무것도 판별하지 못한다** — 두 칸을 맞바꿔도 같은 인스턴스라 통과한다. id마다 **다른 인스턴스**를 심어야 단언이 비로소 무언가를 가른다. 뒷면도 앞면 48장과 다른 인스턴스로 두어 "얼굴 자리에 뒷면이 선 화면"까지 갈랐다.

## 3. 판정 질문

> **"이 대역 위에서 두 칸을 맞바꾸면 이 테스트가 빨개지는가."**

빨개지지 않으면 단언문이 아무리 강해도 **픽스처가 판별력을 지워 버린 것**이다. 일반형: **대역 데이터가 서로 구별되지 않으면, 그 축을 무는 단언은 전부 공허하다.**

이 판정은 뮤테이션 검증([.claude/rules/evaluation.md](../.claude/rules/evaluation.md) 「뮤테이션 검증 절차 게이트」)과 짝이다 — 뮤테이션은 *구현*을 흔들어 시험을 검증하고, 이 질문은 *픽스처*를 흔들어 같은 것을 검증한다. 초록 개수로는 둘 다 보이지 않는다.

## 종료 게이트

- [ ] 단언이 부정형(`Is.Not.*`)이면 동일성 단언으로 바꿀 수 있는지 먼저 검토했는가
- [ ] 기대값을 정본(표·설정·시트)에서 파생했는가 — 테스트가 자기 식을 세우지 않는가
- [ ] 대역 데이터의 칸끼리 서로 구별되는가 (id마다 다른 인스턴스/값)
- [ ] "두 칸을 맞바꾸면 빨개지는가" 를 실제로 흔들어 확인했는가

## 관련 문서

- [hand-listed-roster-decay.md](hand-listed-roster-decay.md) — 손 명부의 대상 목록 판(본 문서는 그 "틀린 값 목록" 판)
- [.claude/rules/evaluation.md](../.claude/rules/evaluation.md) — 뮤테이션 검증 절차 게이트
