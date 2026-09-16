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
    / ".claude"
    / "hooks"
    / "scripts"
    / "hooks.py"
)
SPEC = importlib.util.spec_from_file_location("samantha_hooks", HOOK_PATH)
HOOKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOKS)


class ParseArgumentsTests(unittest.TestCase):
    def test_agent_defaults_to_none(self):
        with mock.patch.object(sys, "argv", ["hooks.py"]):
            self.assertIsNone(HOOKS.parse_arguments().agent)

    def test_agent_name_is_captured(self):
        with mock.patch.object(sys, "argv", ["hooks.py", "--agent", "ava"]):
            self.assertEqual(HOOKS.parse_arguments().agent, "ava")


class SessionContextTests(unittest.TestCase):
    def test_reports_branch_and_clean_worktree(self):
        with mock.patch.object(
            HOOKS,
            "_run_git",
            side_effect=["feature/shelf", ""],
        ):
            context = HOOKS.get_session_context({"cwd": "/tmp"})

        self.assertIn("git branch: feature/shelf", context)
        self.assertIn("working tree: clean", context)
        self.assertIn(f"cwd: {Path('/tmp').resolve()}", context)

    def test_limits_large_worktree_output(self):
        status = "\n".join(f" M file-{index}.txt" for index in range(25))
        with mock.patch.object(
            HOOKS,
            "_run_git",
            side_effect=["feature/shelf", status],
        ):
            context = HOOKS.get_session_context({"cwd": "/tmp"})

        self.assertIn("dirty (25 paths; first 20)", context)
        self.assertIn("file-19.txt", context)
        self.assertNotIn("file-20.txt", context)


class SoundVolumeTests(unittest.TestCase):
    """소리 크기 설정이 Windows 에서도 실제로 듣는지 확인한다.

    winsound.PlaySound 에는 볼륨 인자가 없어 샘플을 직접 줄인다. 그 계산이
    조용히 틀리면 소리만 어긋나고 어디에도 오류가 남지 않는다.
    """

    def test_scaling_reads_and_rewrites_a_16bit_wav(self):
        import array
        import tempfile
        import wave

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tone.wav"
            with wave.open(str(path), "wb") as writer:
                writer.setnchannels(1)
                writer.setsampwidth(2)
                writer.setframerate(44100)
                writer.writeframes(array.array("h", [10000, -10000, 0]).tobytes())

            scaled = HOOKS.scale_wav_to_memory(path, 0.5)

        self.assertIsNotNone(scaled)
        with wave.open(io.BytesIO(scaled), "rb") as reader:
            samples = array.array("h")
            samples.frombytes(reader.readframes(reader.getnframes()))

        self.assertEqual(list(samples), [5000, -5000, 0])


class ConfigurationTests(unittest.TestCase):
    def test_logging_setting_is_read_from_the_repository_config(self):
        # 이 저장소의 공유 설정은 로깅을 끈 상태다. 켜지는 날 이 단언이 먼저 알린다.
        self.assertTrue(HOOKS.is_logging_disabled())

    def test_sound_volume_is_within_range(self):
        volume = HOOKS.get_sound_volume()
        self.assertGreaterEqual(volume, 0.0)
        self.assertLessEqual(volume, 1.0)


class MainTests(unittest.TestCase):
    def test_session_start_prints_context_without_requiring_audio(self):
        payload = json.dumps({"cwd": "/tmp", "hook_event_name": "SessionStart"})
        output = io.StringIO()

        with mock.patch.object(sys, "argv", ["hooks.py"]), \
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
        # 사운드 이름은 sounds/ 아래 폴더 이름이라 소문자다.
        play_sound.assert_called_once_with("sessionstart")

    def test_agent_session_does_not_inject_repository_context(self):
        payload = json.dumps({"cwd": "/tmp", "hook_event_name": "SessionStart"})
        output = io.StringIO()

        with mock.patch.object(sys, "argv", ["hooks.py", "--agent", "ava"]), \
                mock.patch.object(sys, "stdin", io.StringIO(payload)), \
                mock.patch.object(HOOKS, "log_hook_data"), \
                mock.patch.object(HOOKS, "get_session_context") as get_context, \
                mock.patch.object(HOOKS, "play_sound"), \
                self.assertRaises(SystemExit), \
                redirect_stdout(output):
            HOOKS.main()

        get_context.assert_not_called()
        self.assertEqual(output.getvalue().strip(), "")


if __name__ == "__main__":
    unittest.main()
