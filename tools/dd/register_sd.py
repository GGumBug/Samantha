"""S5 상점 도장 화면 뮤테이션(SD)을 mutate_copy.py에 등록한다. 원문은 구현 파일에서 정확히 1회 매칭돼야 한다."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MC = "C:/AI_Projects/Samantha/tools/dd/mutate_copy.py"
SRC = "C:/Unity_Projects/Double-Down/"
P = "Assets/Scripts/Presentation/Hud/ShopStampPanel.cs"
V = "Assets/Scripts/Presentation/Hud/ShopView.cs"
muts = [
    ("SD1", P, "                && _chosenCard.HasValue\n                && session.CanPlaceStamp(\n                    session.StampOffers[_offerIndex].StableId, _chosenCard.Value, _chosenSlot);", "                && _chosenCard.HasValue;", "확인 버튼이 CanPlaceStamp를 안 묻는다", "EditMode"),
    ("SD2", P, "            Close();\n            buy(stampId, card, slot);", "            buy(stampId, card, slot);\n            Close();", "확인이 닫기보다 사기를 먼저 한다", "EditMode"),
    ("SD3", P, "card.SetChoosable(!string.Equals(target.HeldStampId, offer.StableId, StringComparison.Ordinal));", "card.SetChoosable(true);", "같은 도장을 든 패도 고를 수 있다", "EditMode"),
    ("SD4", V, "            session.BuyStamp(stampStableId, definitionId, overwriteSlot);\n\n            RenderShelf();\n            SettleLayout();\n            HudModal.TakeSelectionIfLost(_leaveButton != null ? _leaveButton.gameObject : null);", "            session.BuyStamp(stampStableId, definitionId, overwriteSlot);\n\n            RenderShelf();\n            SettleLayout();", "도장 구매 뒤 잃은 선택을 안 옮긴다", "EditMode"),
]
for m in muts:
    t = open(SRC + m[1], encoding="utf-8").read()
    probe = m[2].replace("\n", "\r\n") if "\r\n" in t else m[2]
    n = t.count(probe)
    if n != 1: print("원문 불일치", m[0], n); sys.exit(1)
src = open(MC, encoding="utf-8").read()
if "'SD1'" in src: print("이미 등록됨"); sys.exit(0)
anchor = src.index("    ('SC8',"); end = src.index("\n", anchor) + 1
open(MC, "w", encoding="utf-8", newline="\n").write(src[:end] + "".join(f"    {m!r},\n" for m in muts) + src[end:])
print("등록", len(muts))
