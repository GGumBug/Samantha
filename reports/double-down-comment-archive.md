# Double-Down 주석 아카이브 — 걷어낸 근거의 좌표

2026-09-15에 클래스 doc 상위 10개를 6줄 이하로 압축했다. 이 문서는 걷어낸 근거를 **어디서 찾는지** 가리킨다. 원문을 복사하지 않는다.

[← 저장소 루트로](../README.md) · [압축 근거](agent-prose-readability.md) · [한국어 문체](korean-prose-style.md)

---

## 왜 원문을 복사하지 않는가

git이 원문을 영구 보존한다. 복사하면 사본이 둘이 되고 그중 하나는 갱신되지 않아 조용히 낡는다. 헌법 §2 SSOT가 여기에도 적용된다. 이 문서가 담는 것은 **좌표**다.

압축 직전 커밋은 `354a8fb`다. 어느 파일이든 원문 doc은 이 명령으로 그대로 나온다.

주석에서 이 문서를 가리킬 때는 **저장소 이름을 함께 적는다**. Double-Down 워킹트리에는 `reports/`가 없고 `.claude`만 정션으로 걸려 있어, `reports/...`만 적으면 그 저장소 기준으로 끊긴 링크가 된다.

```csharp
/// 설계 근거와 거부한 대안: Samantha 저장소 reports/double-down-comment-archive.md
```

```bash
git -C C:/Unity_Projects/Double-Down show 354a8fb:<파일경로> | head -80
```

---

## 대상 10개

`DoubleDownControls.cs`(57줄)는 목록에서 뺐다. Unity Input System이 `.inputactions`에서 자동 생성하는 파일이라 재생성하면 편집이 사라진다.

| 파일 | 압축 전 | 원문이 마지막으로 바뀐 커밋 |
|---|---:|---|
| `Assets/Scripts/Application/ShopSession.cs` | 66줄 | `a8a0789` |
| `Assets/Tests/Presentation/ShopViewLifecycleTests.cs` | 64줄 | `bbac09c` |
| `Assets/Tests/Integration/UICardReactionTests.cs` | 57줄 | `9b4ab8b` |
| `Assets/Tests/Presentation/ShopBonusOfferDisplayTests.cs` | 54줄 | `bbac09c` |
| `Assets/Tests/Integration/ShopViewSlideTests.cs` | 45줄 | `ab317b2` |
| `Assets/Tests/Integration/FloorChoiceLiftLifetimeTests.cs` | 42줄 | `b121b5d` |
| `Assets/Tests/Presentation/JokboTrackerLineDisplayTests.cs` | 41줄 | `d81dfaa` |
| `Assets/Tests/Presentation/BonusSlotListTests.cs` | 40줄 | `265dfd6` |
| `Assets/Tests/Presentation/ShopViewPrefabWiringTests.cs` | 39줄 | `3eb5ce7` |
| `Assets/Tests/Presentation/ShopChipOfferDisplayTests.cs` | 38줄 | `44042f4` |

---

## 걷어낸 내용의 성격

세 갈래였고, 처리가 각각 다르다.

### 1. 다른 문서에 이미 있던 내용 (재수록)

가장 많았다. 규칙 문서를 인용하면서 그 규칙을 다시 설명한 단락이다. 링크 한 줄로 대체했고 잃은 정보가 없다.

| 되풀이된 내용 | 원래 있는 곳 |
|---|---|
| EditMode·PlayMode 판정 사유 | [.claude/rules/evaluation.md](../.claude/rules/evaluation.md), [best-practice/unity-test-mode-selection.md](../best-practice/unity-test-mode-selection.md) |
| 계측 실패를 넘기는 가드 금지, 상한·하한 동시 단언 | [.claude/rules/evaluation.md](../.claude/rules/evaluation.md) |
| 손 명부 금지와 파생 명부 | [best-practice/hand-listed-roster-decay.md](../best-practice/hand-listed-roster-decay.md) |
| 타입에 축을 더할 때 생산자 전수 | [best-practice/second-producer-axis-drift.md](../best-practice/second-producer-axis-drift.md) |

`prose-style.md` §7이 금지한 "과거 인시던트 서술을 주석에 재수록"이 바로 이 갈래다.

### 2. 코드가 이미 말하던 내용

필드 이름과 타입이 말하는 것을 산문으로 한 번 더 적은 부분이다. 삭제했다.

### 3. 이 타입만의 설계 근거 (6줄 안에 남김)

압축 후 doc에 남은 것이 이 갈래다. 예를 들어 `ShopSession`은 네 가지를 남겼다.

- 상점 방문 한 번의 상태이고 Unity 의존이 없는 POCO다
- 국면이 재고와 대기 두 필드에서 파생한다(별도 열거를 두지 않는 이유가 여기서 나온다)
- SKU 셋이 독립이고 보너스만 장착 슬롯 상한을 함께 본다
- 추첨이 주입된 `IRandomStream`만 쓰고 SKU마다 스트림이 따로다

`ShopViewSlideTests`는 2026-09-03 거짓 초록 사고의 후속이라는 한 줄을 남겼다. 그때 7건이 전부 초록인데 연출을 통째로 지워도 통과했다.

---

## 남은 부채

이번에 만진 것은 상위 10개뿐이다. 압축으로 476줄이 줄었고 최대 타입 doc이 66줄에서 57줄로 내려갔다.

| 지표 | 압축 전 | 압축 후 |
|---|---:|---:|
| 6줄 임계 초과 타입 | 212 / 316 | 202 / 316 |
| 타입 doc 평균 | 13.0줄 | 11.6줄 |
| 전체 주석 비율 | 24.1% | 23.8% |
| 주석 내 `<b>` | 4,916개 | 4,670개 |

멤버 doc은 이번 범위가 아니라 3,626개 중 2,000개가 여전히 3줄을 넘는다. 남은 `<b>` 4,670개도 대부분 멤버 doc과 `[Tooltip]`에 있다.

나머지는 [agent-prose-readability.md](agent-prose-readability.md) 4-5절의 "만질 때 고친다"를 따른다. 해당 파일을 편집할 때 그 파일의 doc을 함께 줄인다.

현황은 언제든 다시 잴 수 있다.

```bash
python tools/prose-audit.py --commits 60
```
