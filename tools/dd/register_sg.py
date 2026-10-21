"""S7 연출(SG) 뮤테이션을 mutate_copy.py에 등록한다. 원문은 구현 파일에서 정확히 1회 매칭돼야 한다."""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MC = "C:/AI_Projects/Samantha/tools/dd/mutate_copy.py"
SRC = "C:/Unity_Projects/Double-Down/"
TH = "Assets/Scripts/Application/StampTheft.cs"
CO = "Assets/Scripts/Application/PresentationStepConverter.cs"
SB = "Assets/Scripts/Presentation/Board/CardStampBadge.cs"
FT = "Assets/Scripts/Presentation/Board/FloatingTextMotion.cs"
muts = [
    ("SG1", TH, "return isMember && openBefore >= requiredCount && openBefore - 1 < requiredCount;", "return isMember && openBefore - 1 < requiredCount;", "이미 닫힌 줄에도 뺏김", "EditMode"),
    ("SG2", CO, "                        stampTheftLedger?.Reset();", "                        ;", "라운드가 바뀌어도 장부가 이월", "EditMode"),
    ("SG3", CO, "                CardTag resolvedTag = playerDeck.Resolve(definition).Tag;", "                ledger.RecordOpponentCapture(definitionId);\n                CardTag resolvedTag = playerDeck.Resolve(definition).Tag;", "판정 전에 그 카드를 장부에 기록", "EditMode"),
    ("SG4", SB, "rect.localScale = Vector3.one * _pulseScale;", "rect.localScale = Vector3.one;", "권위 렌더가 펄스를 지운다", "EditMode"),
    ("SG5", SB, "            _pulseHandle.TryCancel();\n            _pulseScale = 1f;", "            _pulseHandle.TryCancel();", "숨겨도 펄스 배율이 남는다", "EditMode"),
    ("SG6", FT, "                case StampStolenStep stolen:\n                    SpawnStampStolen(stolen);\n                    return UniTask.CompletedTask;", "                case StampStolenStep stolen:\n                    return UniTask.CompletedTask;", "뺏김 외침이 안 뜬다", "EditMode"),
]
for m in muts:
    t = open(SRC + m[1], encoding="utf-8").read()
    probe = m[2].replace("\n", "\r\n") if "\r\n" in t else m[2]
    n = t.count(probe)
    if n != 1: print("원문 불일치", m[0], n); sys.exit(1)
src = open(MC, encoding="utf-8").read()
if "'SG1'" in src: print("이미 등록됨"); sys.exit(0)
anchor = src.index("    ('SF9',"); end = src.index("\n", anchor) + 1
open(MC, "w", encoding="utf-8", newline="\n").write(src[:end] + "".join(f"    {m!r},\n" for m in muts) + src[end:])
print("등록", len(muts))
