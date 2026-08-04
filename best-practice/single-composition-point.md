[← README로 돌아가기](../README.md)

# 단일 합성 지점 — 소유권 교대 제거

한 값(트랜스폼·스케일·스프라이트·정렬 순서)에 **여러 주체가 직접 대입**하면, 주체들은 서로를 밟지 않기 위해 소유권을 주고받는 접합부를 만든다(`SuspendFollow`/`ResumeFollow` 류). 이 접합부는 시간이 갈수록 순서·우선순위·가시성 보장까지 암묵적으로 나르게 되어 제거 비용이 계속 오른다.

처방: **각 주체는 자기 표시 채널에 입력만 넣고, 실제 대입은 단일 합성 지점 1곳이 수행한다.** 소유권이라는 개념 자체를 소거한다. Double Down 카드 연출 구조 개편(2026-08-04, 연출 감독 클래스 333줄 철거) 실측.

## 1. 안티패턴 — 소유권 교대

```csharp
// 감독이 연출 동안 트랜스폼을 "빌린다"
_view.SuspendFollow();              // 뷰는 이 구간에 대입하지 않기로 약속
await PlayFlipAsync(token);         // 감독이 직접 transform.position 대입
_view.ResumeFollow();               // 소유권 반납
```

증상:

- **접합부가 계약을 문서 밖에 둔다** — "빌린 동안 뷰는 대입하지 않는다"가 코드가 아니라 약속. 새 주체(드래그 등)가 합류하면 약속이 하나 더 늘어난다
- **소유권 플래그가 다른 사실의 대리자로 전락** — "감독이 쥐고 있다"를 "지금 연출 중"으로 읽는 독자가 붙는다. 접합부 제거 시 이 독자들이 조용히 깨진다([implicit-proxy-state-removal.md](implicit-proxy-state-removal.md))
- **취소·파괴 경로가 접합부마다 곱해진다** — Suspend 후 예외/취소로 Resume 이 누락되면 값이 영구 동결
- **N 주체 = N² 조정** — 주체가 늘 때마다 기존 접합부 전부를 재검토

## 2. 처방 — 채널 입력 + 단일 대입

```csharp
// 각 주체는 자기 채널에만 쓴다 — 대입 권한 없음
_followOffset = ...;   // 추종
_riseHeight   = ...;   // 뜸(들어올림)
_flipOffset   = ...;   // 뒤집기
_dragOffset   = ...;   // 드래그

// 대입은 여기 한 곳 — 합성 규칙이 코드로 드러난다
private void ComposeTransform()
{
    transform.position = _basePosition + _followOffset + _riseHeight + _flipOffset + _dragOffset;
}
```

얻는 것:

- 주체 추가는 **채널 추가 + 합성식 한 항**. 기존 주체 무수정 (OCP)
- 우선순위·가산 여부가 합성식에 **명시** — "누가 이겼는지"를 디버거로 추적할 필요 없음
- 취소 처리는 "채널을 0으로" — 소유권 반납 누락이라는 실패 모드가 존재하지 않음
- 중간 상태가 화면에 새지 않음. 프레임당 대입이 1회로 고정

## 3. 같은 처방이 성격 다른 네 축에 적중

한 축에서만 통하면 임시방편이고, 성격이 다른 축에 모두 통하면 구조의 일반성이다. 본 개편에서 네 축이 차례로 같은 형태로 수렴했다.

| 축 | Before (흩어진 대입) | After (단일 합성) |
|---|---|---|
| 위치 | 뷰·감독이 번갈아 `transform.position` 대입 | `ComposeTransform` 1곳 |
| 스케일 | 연출별로 각자 대입 | 채널 합성 후 1곳 대입 |
| 스프라이트 | 뒤집기 중 앞/뒷면 교체를 호출 지점마다 | `_flipCoverActive` 선언 + 단일 대입 |
| 정렬 | `RefreshSorting` 이벤트 **10곳**에서 호출 | `LateUpdate` **1곳**에서 매 프레임 산출 |

정렬 축이 특히 중요하다. 이벤트 산재형은 "갱신 호출을 어디서 빠뜨렸나" 부류의 버그를 영구 생산하는데, 프레임 말 단일 산출로 바꾸면 **그 버그 부류 자체가 소멸**한다(호출 지점이 없으므로 누락도 없다). 대신 매 프레임 비용을 지불한다 — 항목 수가 크면 프레임 예산 확인 필요.

## 4. 적용 / 회피 판단

| 조건 | 판단 |
|---|---|
| 대입 주체 2개 이상 + 각자 다른 시간축(입력·애니메이션·물리·네트워크) | **적용** |
| 주체 간 조정을 위해 플래그·`Suspend/Resume`·`enabled` 토글이 이미 있음 | **적용** — 접합부는 부채의 이자다 |
| 대입 주체 1개 | 회피 — 합성 지점은 간접층만 추가 (헌법 §5 YAGNI) |
| 대입이 1회성 초기화 | 회피 — 경합이 없다 |
| 매 프레임 재산출 비용이 예산을 넘음 | 부분 적용 — 합성은 유지하되 **더티 플래그**로 산출 시점만 줄인다 |

**금기**: "나중에 주체가 늘 수도 있으니 미리 채널화" — 주체 2개가 실제로 경합할 때 도입한다(헌법 §3 3회 반복 원칙의 변형).

## 5. 이관 시 주의 — 접합부가 나르던 보장

접합부를 걷어내면 **접합부가 부수적으로 보장하던 것**이 함께 사라진다. 본 개편에서 "뒤집기가 추종을 얼려서 이동이 정지된다"는 안무 순서 보장이 접합부와 함께 소멸해 카드가 뒤집히며 미끄러지는 회귀가 발생했다. 채널 이관 전에 **읽기 지점 전수 조사**가 선행돼야 한다 — 절차는 [implicit-proxy-state-removal.md](implicit-proxy-state-removal.md).

## 관련 문서

- [implicit-proxy-state-removal.md](implicit-proxy-state-removal.md) — 접합부 제거 시 읽기 지점 전수 조사(본 문서의 짝)
- [multilayer-state-sync.md](multilayer-state-sync.md) — 상태 **전이** 를 SSOT 진입점으로 묶는 축(본 문서는 매 프레임 **값** 축)
- [ui-visibility-two-layer-srp.md](ui-visibility-two-layer-srp.md) — 가시성 SSOT 의 layer 분리
- [solid-unity-principles.md](solid-unity-principles.md) — Dirty Flag / Speculative Observer 안티패턴
- [.claude/rules/engineering-constitution.md](../.claude/rules/engineering-constitution.md) — §2 SSOT, §3 패턴 도입 기준, §5 오버엔지니어링 회피
