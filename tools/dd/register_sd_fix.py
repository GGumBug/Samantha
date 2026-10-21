"""S5 리뷰 수정(F1·F4) 뮤테이션 SD5~SD7을 mutate_copy.py에 등록한다. 원문은 정확히 1회 매칭돼야 한다."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MC = "C:/AI_Projects/Samantha/tools/dd/mutate_copy.py"
SRC = "C:/Unity_Projects/Double-Down/"
V = "Assets/Scripts/Presentation/Hud/ShopView.cs"
muts = [
    ("SD5", V, "            HideChipOpening();\n            CloseStampPanel();\n            RenderShelf();", "            HideChipOpening();\n            RenderShelf();", "재방문이 도장 패널을 안 닫는다", "EditMode"),
    ("SD6", V, "bool stampPanelOpen = _stampPanel != null && _stampPanel.IsOpen;", "bool stampPanelOpen = false;", "도장 패널이 열려도 매대를 안 잠근다", "EditMode"),
    ("SD7", V, "            // 잠금을 먼저 푼다. 잠긴 버튼에 선택을 주면 uGUI가 그 선택을 지운다.\n            RenderShelf();\n", "            // 잠금을 먼저 푼다. 잠긴 버튼에 선택을 주면 uGUI가 그 선택을 지운다.\n", "그만이 잠금을 안 풀고 선택을 준다", "EditMode"),
]
for m in muts:
    t = open(SRC + m[1], encoding="utf-8").read()
    probe = m[2].replace("\n", "\r\n") if "\r\n" in t else m[2]
    n = t.count(probe)
    if n != 1: print("원문 불일치", m[0], n); sys.exit(1)
src = open(MC, encoding="utf-8").read()
if "'SD5'" in src: print("이미 등록됨"); sys.exit(0)
anchor = src.index("    ('SD4',"); end = src.index("\n", anchor) + 1
open(MC, "w", encoding="utf-8", newline="\n").write(src[:end] + "".join(f"    {m!r},\n" for m in muts) + src[end:])
print("등록", len(muts))
