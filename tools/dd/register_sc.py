import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MC = "C:/AI_Projects/Samantha/tools/dd/mutate_copy.py"
SRC = "C:/Unity_Projects/Double-Down/"
S = "Assets/Scripts/Application/ShopSession.cs"
muts = [
    ("SC1", S, "if (second >= first)\n            {\n                second++;\n            }", "if (false)\n            {\n                second++;\n            }", "둘째 제시 보정 없음(같은 도장 둘)", "EditMode"),
    ("SC2", S, "offers.Add(catalog[low]);\n            offers.Add(catalog[high]);", "offers.Add(catalog[first]);\n            offers.Add(catalog[second]);", "제시 정렬 없음", "EditMode"),
    ("SC3", S, "            _stampSoldOut = true;", "            ;", "도장 품절 표시 없음", "EditMode"),
    ("SC4", S, "&& !IsStampSoldOut\n            && _run.Phase == RunPhase.AwaitingMatch", "&& !IsStampSoldOut", "도장 SKU 국면 조건 없음", "EditMode"),
    ("SC5", S, "if (IsSameStamp(_stamps.Slots[held].Stamp, stamp))", "if (false)", "같은 도장 재구매 허용", "EditMode"),
    ("SC6", S, "return overwriteSlot >= 0 && overwriteSlot < RunStamps.SlotCount;", "return overwriteSlot >= 0;", "덮을 칸 상한 검사 없음", "EditMode"),
    ("SC7", S, "if (!CanPlaceStamp(stampStableId, definitionId, overwriteSlot))", "if (false)", "BuyStamp가 배치 규칙을 건너뜀", "EditMode"),
    ("SC8", S, "                    heldStamp.StableId);", "                    null);", "HeldStampId가 늘 null", "EditMode"),
]
t = open(SRC + S, encoding="utf-8").read()
crlf = "\r\n" in t
for m in muts:
    probe = m[2].replace("\n", "\r\n") if crlf else m[2]
    n = t.count(probe)
    if n != 1: print("원문 불일치", m[0], n); sys.exit(1)
src = open(MC, encoding="utf-8").read()
if "'SC1'" in src: print("이미 등록됨"); sys.exit(0)
anchor = src.index("    ('SB3',"); end = src.index("\n", anchor) + 1
open(MC, "w", encoding="utf-8", newline="\n").write(src[:end] + "".join(f"    {m!r},\n" for m in muts) + src[end:])
print("등록", len(muts))
