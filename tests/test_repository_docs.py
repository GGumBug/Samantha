import ast
import json
import re
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_skill_frontmatter(contents):
    """Parse the scalar-only YAML subset used by repository skills."""
    lines = contents.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("missing closing frontmatter delimiter") from error

    result = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if line[:1].isspace() or ":" not in line:
            raise ValueError(f"unsupported frontmatter line: {line}")
        key, raw_value = line.split(":", 1)
        if not re.fullmatch(r"[a-z][a-z0-9-]*", key):
            raise ValueError(f"invalid frontmatter key: {key}")
        if key in result:
            raise ValueError(f"duplicate frontmatter key: {key}")
        raw_value = raw_value.strip()
        if not raw_value:
            raise ValueError(f"empty frontmatter value: {key}")
        if raw_value[:1] in ('"', "'"):
            result[key] = ast.literal_eval(raw_value)
        else:
            result[key] = raw_value
    return result


class RepositoryDocumentationTests(unittest.TestCase):
    def test_instruction_files_stay_under_200_lines(self):
        paths = [ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "README.md"]
        paths.extend((ROOT / ".claude" / "rules").glob("*.md"))
        paths.extend((ROOT / ".claude" / "agents").glob("*.md"))
        for path in paths:
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(line_count, 200, path.relative_to(ROOT).as_posix())

    def test_readme_indexes_every_best_practice_document(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexed = {
            match
            for match in LINK_PATTERN.findall(readme)
            if match.startswith("best-practice/") and match.endswith(".md")
        }
        expected = {
            # as_posix 가 아니면 Windows 에서 역슬래시가 나와 README 의 링크와 영영 어긋난다.
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "best-practice").glob("*.md")
        }
        self.assertEqual(indexed, expected)

    def test_primary_docs_have_no_broken_local_links(self):
        for relative_path in ("AGENTS.md", "README.md"):
            path = ROOT / relative_path
            for target in LINK_PATTERN.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#")):
                    continue
                target_path = target.split("#", 1)[0]
                resolved = (path.parent / target_path).resolve()
                self.assertTrue(resolved.exists(), f"{relative_path}: {target}")

    def test_skill_frontmatter_has_required_fields(self):
        # 전체 YAML 을 풀지 않고 두 키의 존재만 본다. 스킬 프론트매터에는 목록·중첩이
        # 들어와 최소 파서로는 읽을 수 없고, 이 시험이 지키려는 것은 형식이 아니라
        # "이름과 설명이 있는가"다. 설명이 없으면 자동 검색이 그 스킬을 못 고른다.
        for path in (ROOT / ".claude" / "skills").glob("*/SKILL.md"):
            self.assertFrontmatterNames(path)

    def test_custom_agents_declare_required_fields(self):
        for path in (ROOT / ".claude" / "agents").glob("*.md"):
            self.assertFrontmatterNames(path)

    def assertFrontmatterNames(self, path):
        contents = path.read_text(encoding="utf-8")
        where = path.relative_to(ROOT).as_posix()
        self.assertTrue(contents.startswith("---"), where)
        block = contents.split("---", 2)[1]
        for key in ("name", "description"):
            match = re.search(rf"^{key}:\s*(\S.*)$", block, re.MULTILINE)
            self.assertIsNotNone(match, f"{where}: {key} 없음")

    def test_hook_events_point_at_the_repository_handler(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        events = settings.get("hooks", {})
        self.assertTrue(events, ".claude/settings.json 에 훅 이벤트가 하나도 없다")
        for event, matcher_groups in events.items():
            for matcher_group in matcher_groups:
                for hook in matcher_group["hooks"]:
                    command = hook.get("command", "")
                    if "hooks.py" not in command:
                        continue
                    # 경로를 저장소 루트에서 풀어야 다른 PC 에서도 같은 핸들러를 부른다.
                    self.assertIn("CLAUDE_PROJECT_DIR", command, event)
                    self.assertIn(".claude/hooks/scripts/hooks.py", command, event)


if __name__ == "__main__":
    unittest.main()
