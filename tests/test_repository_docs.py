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
        paths = [ROOT / "AGENTS.md", ROOT / "README.md"]
        paths.extend((ROOT / ".codex" / "agents").glob("*.toml"))
        paths.extend((ROOT / ".agents" / "skills").glob("*/SKILL.md"))
        for path in paths:
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(line_count, 200, str(path.relative_to(ROOT)))

    def test_readme_indexes_every_best_practice_document(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexed = {
            match
            for match in LINK_PATTERN.findall(readme)
            if match.startswith("best-practice/") and match.endswith(".md")
        }
        expected = {
            str(path.relative_to(ROOT))
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

    def test_codex_docs_use_canonical_lowercase_paths(self):
        paths = [ROOT / "AGENTS.md", ROOT / "README.md"]
        paths.extend((ROOT / ".codex" / "agents").glob("*.toml"))
        for path in paths:
            contents = path.read_text(encoding="utf-8")
            self.assertNotIn(".Codex", contents, str(path.relative_to(ROOT)))

    def test_skill_frontmatter_has_required_fields(self):
        for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md"):
            contents = path.read_text(encoding="utf-8")
            metadata = parse_skill_frontmatter(contents)
            self.assertTrue(metadata.get("name"), str(path.relative_to(ROOT)))
            self.assertTrue(metadata.get("description"), str(path.relative_to(ROOT)))

    @unittest.skipIf(tomllib is None, "TOML parsing requires Python 3.11+")
    def test_custom_agents_declare_required_fields(self):
        for path in (ROOT / ".codex" / "agents").glob("*.toml"):
            metadata = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(metadata.get("name"), str(path.relative_to(ROOT)))
            self.assertTrue(metadata.get("description"), str(path.relative_to(ROOT)))
            self.assertTrue(metadata.get("developer_instructions"), str(path.relative_to(ROOT)))

    def test_hooks_have_portable_root_resolved_commands(self):
        config = json.loads((ROOT / ".codex" / "hooks.json").read_text())
        for event, matcher_groups in config["hooks"].items():
            for matcher_group in matcher_groups:
                for hook in matcher_group["hooks"]:
                    self.assertIn("git rev-parse --show-toplevel", hook["command"], event)
                    self.assertIn("commandWindows", hook, event)
                    self.assertIn("git rev-parse --show-toplevel", hook["commandWindows"], event)


if __name__ == "__main__":
    unittest.main()
