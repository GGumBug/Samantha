import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MC = "C:/AI_Projects/Samantha/tools/dd/mutate_copy.py"
SRC = "C:/Unity_Projects/Double-Down/"
F = "Assets/Scripts/Boot/MatchSessionFactory.cs"
muts = [
    ("SB1", F, "cardUpgrades = _stamps.ApplyTo(cardUpgrades);", ";", "도장이 덱 렌즈에 안 실림", "PlayMode"),
    ("SB2", F, "_stakeRuleEnabled, _balances.Shop.StartGold);\n            _upgrades = new RunUpgrades();\n            _cardUpgrades = new RunCardUpgrades();\n            _bonusCards = new RunBonusCards();\n            _stamps = new RunStamps();",
               "_stakeRuleEnabled, _balances.Shop.StartGold);\n            _upgrades = new RunUpgrades();\n            _cardUpgrades = new RunCardUpgrades();\n            _bonusCards = new RunBonusCards();", "새 런이 옛 도장을 이음", "PlayMode"),
    ("SB3", F, "_stamps.Stamp(new CardDefinitionId(definitionId), StampCatalog.Get(stampStableId));", "try { _stamps.Stamp(new CardDefinitionId(definitionId), StampCatalog.Get(stampStableId)); } catch (System.ArgumentException) { }", "DebugStamp가 거부를 삼킴", "PlayMode"),
]
for m in muts:
    t = open(SRC + m[1], encoding="utf-8").read()
    probe = m[2].replace("\n", "\r\n") if "\r\n" in t else m[2]
    n = t.count(probe)
    if n != 1: print("원문 불일치", m[0], n); sys.exit(1)
src = open(MC, encoding="utf-8").read()
if "'SB1'" in src: print("이미 등록됨"); sys.exit(0)
anchor = src.index("    ('SA5',"); end = src.index("\n", anchor) + 1
open(MC, "w", encoding="utf-8", newline="\n").write(src[:end] + "".join(f"    {m!r},\n" for m in muts) + src[end:])
print("등록", len(muts))
