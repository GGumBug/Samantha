"""S6a(SE)·S6b(SF) 뮤테이션을 mutate_copy.py에 등록한다. 원문은 구현 파일에서 정확히 1회 매칭돼야 한다."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MC = "C:/AI_Projects/Samantha/tools/dd/mutate_copy.py"
SRC = "C:/Unity_Projects/Double-Down/"
MS = "Assets/Scripts/Application/MatchSession.cs"
SL = "Assets/Scripts/Application/ScoreLineMembers.cs"
PV = "Assets/Scripts/Application/PresentationVocabulary.cs"
CV = "Assets/Scripts/Presentation/Board/CardView.cs"
JT = "Assets/Scripts/Presentation/Hud/JokboTracker.cs"
SB = "Assets/Scripts/Presentation/Board/CardStampBadge.cs"
muts = [
    ("SE1", MS, "                CountTiers(entry.Upgrades),", "                entry.Upgrades.Count,", "도장을 금박 단으로 센다", "PlayMode"),
    ("SE2", MS, "                : StampLineProjection.TargetLineOf(resolvedTag);", "                : (ScoreLineKind?)null;", "프로브의 도장 줄이 늘 null", "PlayMode"),
    ("SE3", SL, "if (CountsToward(card, deck.Resolve(card).Tag, kind))", "if (CountsToward(card, card.Tag, kind))", "후보 표가 렌즈를 무시한다", "EditMode"),
    ("SE4", PV, "                && IsWeightAltered == other.IsWeightAltered\n                && StampLine == other.StampLine;", "                && IsWeightAltered == other.IsWeightAltered;", "같음 비교가 도장 줄을 무시한다", "EditMode"),
    ("SF1", CV, "                else\n                {\n                    _stampBadge.Hide();\n                }", "                else\n                {\n                }", "도장이 빠져도 배지가 남는다", "EditMode"),
    ("SF2", JT, "                _lineMembers != null && _lineMembers.TryGetValue(line.Kind, out IReadOnlyList<ushort> lensMembers)", "                false && _lineMembers.TryGetValue(line.Kind, out IReadOnlyList<ushort> lensMembers)", "힌트가 렌즈 표를 안 쓴다", "EditMode"),
    ("SF3", JT, "            _lineMembers = null;", "            // MUTATION", "판 사이에 렌즈 표가 남는다", "EditMode"),
    ("SF4", SB, "bounds.max.x - bounds.size.x * RightInsetFactor,", "bounds.min.x + bounds.size.x * RightInsetFactor,", "배지가 왼쪽 위로 간다", "EditMode"),
    ("SF5", SB, "_labelRenderer.sortingOrder = sortingOrder + SortingOrderOffset;", "_labelRenderer.sortingOrder = sortingOrder;", "배지가 카드와 같은 정렬 순서", "EditMode"),
]
for m in muts:
    t = open(SRC + m[1], encoding="utf-8").read()
    probe = m[2].replace("\n", "\r\n") if "\r\n" in t else m[2]
    n = t.count(probe)
    if n != 1: print("원문 불일치", m[0], n); sys.exit(1)
src = open(MC, encoding="utf-8").read()
if "'SE1'" in src: print("이미 등록됨"); sys.exit(0)
anchor = src.index("    ('SD4',"); end = src.index("\n", anchor) + 1
open(MC, "w", encoding="utf-8", newline="\n").write(src[:end] + "".join(f"    {m!r},\n" for m in muts) + src[end:])
print("등록", len(muts))
