"""S6b 리뷰 수정(F2·F3·F5) 뮤테이션 SF6~SF9를 mutate_copy.py에 등록한다. 원문은 정확히 1회 매칭돼야 한다."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MC = "C:/AI_Projects/Samantha/tools/dd/mutate_copy.py"
SRC = "C:/Unity_Projects/Double-Down/"
R = "Assets/Scripts/Presentation/Board/CardViewRegistry.cs"
CV = "Assets/Scripts/Presentation/Board/CardView.cs"
SB = "Assets/Scripts/Presentation/Board/CardStampBadge.cs"
muts = [
    ("SF6", R, "if (zone == BoardZone.OpponentCaptured && values.HasStamp)", "if (false && values.HasStamp)", "상대 획득패에도 내 도장 배지", "EditMode"),
    ("SF7", CV, "if (!IsFlipCovered && _upgradeValues.HasStamp)", "if (_upgradeValues.HasStamp)", "뒤집기 가림 중에도 배지", "EditMode"),
    ("SF8", SB, "            _label = holder.AddComponent<TextMeshPro>();\n            if (_font != null)\n            {\n                _label.font = _font;\n            }", "            _label = holder.AddComponent<TextMeshPro>();", "새 배지 라벨이 폰트를 안 받는다", "EditMode"),
    ("SF9", SB, "            if (_label != null && font != null)\n            {\n                _label.font = font;\n            }", "            if (false)\n            {\n                _label.font = font;\n            }", "이미 선 배지가 폰트 교체를 안 받는다", "EditMode"),
]
for m in muts:
    t = open(SRC + m[1], encoding="utf-8").read()
    probe = m[2].replace("\n", "\r\n") if "\r\n" in t else m[2]
    n = t.count(probe)
    if n != 1: print("원문 불일치", m[0], n); sys.exit(1)
src = open(MC, encoding="utf-8").read()
if "'SF6'" in src: print("이미 등록됨"); sys.exit(0)
anchor = src.index("    ('SF5',"); end = src.index("\n", anchor) + 1
open(MC, "w", encoding="utf-8", newline="\n").write(src[:end] + "".join(f"    {m!r},\n" for m in muts) + src[end:])
print("등록", len(muts))
