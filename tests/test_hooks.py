import importlib.util
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


HOOK_PATH = (
    Path(__file__).resolve().parents[1]
    / ".codex"
    / "hooks"
    / "scripts"
    / "hooks.py"
)
SPEC = importlib.util.spec_from_file_location("samantha_hooks", HOOK_PATH)
HOOKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOKS)


class ParseArgsTests(unittest.TestCase):
    def test_parses_hook_name_and_stdin_payload(self):
        payload = {"cwd": "/tmp/project", "hook_event_name": "SessionStart"}

        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
            event_type, hook_data = HOOKS.parse_args(["--hook", "SessionStart"])

        self.assertEqual(event_type, "SessionStart")
        self.assertEqual(hook_data["cwd"], "/tmp/project")
        self.assertEqual(hook_data["type"], "SessionStart")

    def test_ignores_unknown_arguments(self):
        self.assertEqual(HOOKS.parse_args(["--unknown"]), (None, None))


class SessionContextTests(unittest.TestCase):
    def test_reports_branch_and_clean_worktree(self):
        with mock.patch.object(
            HOOKS,
            "_run_git",
            side_effect=["feature/codex", ""],
        ):
            context = HOOKS.get_session_context({"cwd": "/tmp"})

        self.assertIn("git branch: feature/codex", context)
        self.assertIn("working tree: clean", context)
        self.assertIn(f"cwd: {Path('/tmp').resolve()}", context)

    def test_limits_large_worktree_output(self):
        status = "\n".join(f" M file-{index}.txt" for index in range(25))
        with mock.patch.object(
            HOOKS,
            "_run_git",
            side_effect=["feature/codex", status],
        ):
            context = HOOKS.get_session_context({"cwd": "/tmp"})

        self.assertIn("dirty (25 paths; first 20)", context)
        self.assertIn("file-19.txt", context)
        self.assertNotIn("file-20.txt", context)


class ConfigurationTests(unittest.TestCase):
    def test_logging_fails_closed_when_config_is_unavailable(self):
        with mock.patch.object(HOOKS, "load_config", return_value=(None, None)):
            self.assertTrue(HOOKS.is_logging_disabled())

    def test_explicit_team_setting_can_enable_logging(self):
        with mock.patch.object(
            HOOKS,
            "load_config",
            return_value=(None, {"disableLogging": False}),
        ):
            self.assertFalse(HOOKS.is_logging_disabled())


class MainTests(unittest.TestCase):
    def test_session_start_prints_context_without_requiring_audio(self):
        payload = json.dumps({"cwd": "/tmp", "hook_event_name": "SessionStart"})
        output = io.StringIO()

        with mock.patch.object(sys, "argv", ["hooks.py", "--hook", "SessionStart"]), \
                mock.patch.object(sys, "stdin", io.StringIO(payload)), \
                mock.patch.object(HOOKS, "log_hook_data"), \
                mock.patch.object(HOOKS, "is_hook_disabled", return_value=False), \
                mock.patch.object(HOOKS, "get_session_context", return_value="context"), \
                mock.patch.object(HOOKS, "play_sound") as play_sound, \
                self.assertRaises(SystemExit) as exit_context, \
                redirect_stdout(output):
            HOOKS.main()

        self.assertEqual(exit_context.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), "context")
        play_sound.assert_called_once_with("SessionStart")


if __name__ == "__main__":
    unittest.main()
