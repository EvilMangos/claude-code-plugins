#!/usr/bin/env python3
"""
Tests for auto-save-signal-on-stop.py

Run with: python3 -m pytest auto-save-signal-on-stop_test.py -v
Or simply: python3 auto-save-signal-on-stop_test.py
"""
import json
import tempfile
import os
from pathlib import Path

# Import the module under test
import importlib.util
spec = importlib.util.spec_from_file_location(
    "auto_save_signal",
    Path(__file__).parent / "auto-save-signal-on-stop.py"
)
auto_save_signal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_save_signal)


class TestParseWorkflowContext:
    """Tests for parse_workflow_context()"""

    def test_extracts_task_id_and_report_type(self):
        prompt = """TASK_ID: develop-feature-test-123

## Task
Do something

## Output
reportType: performance
"""
        result = auto_save_signal.parse_workflow_context(prompt)
        assert result["task_id"] == "develop-feature-test-123"
        assert result["report_type"] == "performance"

    def test_handles_backtick_quoted_task_id(self):
        prompt = "TASK_ID: `my-task-456` \n\nreportType: security"
        result = auto_save_signal.parse_workflow_context(prompt)
        assert result["task_id"] == "my-task-456"
        assert result["report_type"] == "security"

    def test_handles_inline_report_type(self):
        prompt = "TASK_ID: task-789 \nreportType: implementation"
        result = auto_save_signal.parse_workflow_context(prompt)
        assert result["task_id"] == "task-789"
        assert result["report_type"] == "implementation"

    def test_returns_none_for_missing_fields(self):
        prompt = "Some random text without workflow context"
        result = auto_save_signal.parse_workflow_context(prompt)
        assert result["task_id"] is None
        assert result["report_type"] is None


class TestFindTaskCallForAgent:
    """Tests for find_task_call_for_agent() - the fixed parallel agent matching"""

    def _create_transcript(self, entries):
        """Helper to create a temporary transcript file"""
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        return path

    def test_matches_single_agent_correctly(self):
        """Single agent should match correctly"""
        entries = [
            # Task tool_use
            {
                "type": "assistant",
                "message": {
                    "content": [{
                        "type": "tool_use",
                        "id": "toolu_001",
                        "name": "Task",
                        "input": {
                            "subagent_type": "backend-toolbox:plan-creator",
                            "prompt": "TASK_ID: test-task-1\n\n## Output\nreportType: plan"
                        }
                    }]
                }
            },
            # Tool result with agentId
            {
                "type": "user",
                "message": {
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": "toolu_001",
                        "content": [{"type": "text", "text": "agentId: agent-abc"}]
                    }]
                },
                "toolUseResult": {"agentId": "agent-abc"}
            }
        ]
        path = self._create_transcript(entries)
        try:
            result = auto_save_signal.find_task_call_for_agent(path, "agent-abc")
            assert result["subagent_type"] == "backend-toolbox:plan-creator"
            assert "reportType: plan" in result["prompt"]
        finally:
            os.unlink(path)

    def test_matches_parallel_agents_correctly(self):
        """Parallel agents (performance + security) should each match correctly"""
        entries = [
            # Two Task tool_use calls in same message (parallel launch)
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_perf",
                            "name": "Task",
                            "input": {
                                "subagent_type": "backend-toolbox:performance-specialist",
                                "prompt": "TASK_ID: test-parallel\n\n## Output\nreportType: performance"
                            }
                        },
                        {
                            "type": "tool_use",
                            "id": "toolu_sec",
                            "name": "Task",
                            "input": {
                                "subagent_type": "backend-toolbox:application-security-specialist",
                                "prompt": "TASK_ID: test-parallel\n\n## Output\nreportType: security"
                            }
                        }
                    ]
                }
            },
            # Tool results for both agents
            {
                "type": "user",
                "message": {
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": "toolu_perf",
                        "content": [{"type": "text", "text": "agentId: perf-agent-123"}]
                    }]
                },
                "toolUseResult": {"agentId": "perf-agent-123"}
            },
            {
                "type": "user",
                "message": {
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": "toolu_sec",
                        "content": [{"type": "text", "text": "agentId: sec-agent-456"}]
                    }]
                },
                "toolUseResult": {"agentId": "sec-agent-456"}
            }
        ]
        path = self._create_transcript(entries)
        try:
            # Performance agent should match to performance reportType
            perf_result = auto_save_signal.find_task_call_for_agent(path, "perf-agent-123")
            assert perf_result["subagent_type"] == "backend-toolbox:performance-specialist"
            assert "reportType: performance" in perf_result["prompt"]

            # Security agent should match to security reportType
            sec_result = auto_save_signal.find_task_call_for_agent(path, "sec-agent-456")
            assert sec_result["subagent_type"] == "backend-toolbox:application-security-specialist"
            assert "reportType: security" in sec_result["prompt"]
        finally:
            os.unlink(path)

    def test_fallback_when_no_agent_id_match(self):
        """When agent_id doesn't match any result, should fallback to last Task call"""
        entries = [
            {
                "type": "assistant",
                "message": {
                    "content": [{
                        "type": "tool_use",
                        "id": "toolu_001",
                        "name": "Task",
                        "input": {
                            "subagent_type": "backend-toolbox:code-reviewer",
                            "prompt": "TASK_ID: test-fallback\n\n## Output\nreportType: code-review"
                        }
                    }]
                }
            }
            # No tool_result with agentId
        ]
        path = self._create_transcript(entries)
        try:
            result = auto_save_signal.find_task_call_for_agent(path, "unknown-agent")
            # Should fallback to the only Task call
            assert result["subagent_type"] == "backend-toolbox:code-reviewer"
            assert "reportType: code-review" in result["prompt"]
        finally:
            os.unlink(path)

    def test_ignores_non_backend_toolbox_agents(self):
        """Should only collect backend-toolbox Task calls"""
        entries = [
            {
                "type": "assistant",
                "message": {
                    "content": [{
                        "type": "tool_use",
                        "id": "toolu_other",
                        "name": "Task",
                        "input": {
                            "subagent_type": "Explore",
                            "prompt": "Search the codebase"
                        }
                    }]
                }
            }
        ]
        path = self._create_transcript(entries)
        try:
            result = auto_save_signal.find_task_call_for_agent(path, "any-agent")
            assert result["subagent_type"] == ""
            assert result["prompt"] == ""
        finally:
            os.unlink(path)

    def test_handles_empty_transcript(self):
        """Should handle empty transcript gracefully"""
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        try:
            result = auto_save_signal.find_task_call_for_agent(path, "agent-123")
            assert result["subagent_type"] == ""
            assert result["prompt"] == ""
        finally:
            os.unlink(path)

    def test_handles_nonexistent_file(self):
        """Should handle nonexistent file gracefully"""
        result = auto_save_signal.find_task_call_for_agent("/nonexistent/path.jsonl", "agent-123")
        assert result["subagent_type"] == ""
        assert result["prompt"] == ""

    def test_regression_parallel_agents_not_confused(self):
        """
        Regression test for the bug where parallel agents would get confused.

        Original bug: When performance and security agents were launched in parallel,
        both would incorrectly save as 'security' because find_task_call_for_agent()
        wasn't using agent_id to match - it just kept the last Task call found.

        This test ensures each agent gets its own correct reportType.
        """
        entries = [
            # Parallel launch: performance first, then security
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_01LnTeGasBaj2AXhLswyLquy",
                            "name": "Task",
                            "input": {
                                "subagent_type": "backend-toolbox:performance-specialist",
                                "prompt": "TASK_ID: develop-feature-test\n\n## Output\nreportType: performance"
                            }
                        },
                        {
                            "type": "tool_use",
                            "id": "toolu_0139tQwG8Fv8qjhcfGVwqvNM",
                            "name": "Task",
                            "input": {
                                "subagent_type": "backend-toolbox:application-security-specialist",
                                "prompt": "TASK_ID: develop-feature-test\n\n## Output\nreportType: security"
                            }
                        }
                    ]
                }
            },
            # Results come back in same order
            {
                "type": "user",
                "message": {
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": "toolu_01LnTeGasBaj2AXhLswyLquy",
                        "content": [{"type": "text", "text": "Launched agentId: a0cc3a9"}]
                    }]
                },
                "toolUseResult": {"agentId": "a0cc3a9"}
            },
            {
                "type": "user",
                "message": {
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": "toolu_0139tQwG8Fv8qjhcfGVwqvNM",
                        "content": [{"type": "text", "text": "Launched agentId: a8dbc5c"}]
                    }]
                },
                "toolUseResult": {"agentId": "a8dbc5c"}
            }
        ]
        path = self._create_transcript(entries)
        try:
            # THE BUG: Without the fix, both of these would return "security"
            # because the old code just kept the last Task call found.

            # Performance agent a0cc3a9 should get performance, NOT security
            perf_result = auto_save_signal.find_task_call_for_agent(path, "a0cc3a9")
            assert "reportType: performance" in perf_result["prompt"], \
                f"Performance agent got wrong reportType! Expected 'performance' but prompt was: {perf_result['prompt'][:100]}"

            # Security agent a8dbc5c should get security
            sec_result = auto_save_signal.find_task_call_for_agent(path, "a8dbc5c")
            assert "reportType: security" in sec_result["prompt"], \
                f"Security agent got wrong reportType! Expected 'security' but prompt was: {sec_result['prompt'][:100]}"

            # Extra validation: they should NOT be the same
            assert perf_result["prompt"] != sec_result["prompt"], \
                "Bug regression: Both agents got the same prompt!"
        finally:
            os.unlink(path)


class TestParseStatusFromTranscript:
    """Tests for parse_status_from_transcript()"""

    def test_detects_explicit_passed_status(self):
        transcript = "Analysis complete.\n\nSTATUS: PASSED"
        status, summary = auto_save_signal.parse_status_from_transcript(transcript)
        assert status == "passed"

    def test_detects_explicit_failed_status(self):
        transcript = "Found issues.\n\nSTATUS: FAILED"
        status, summary = auto_save_signal.parse_status_from_transcript(transcript)
        assert status == "failed"

    def test_detects_failure_from_error_indicator(self):
        transcript = "Error: Module not found\nCould not complete task"
        status, summary = auto_save_signal.parse_status_from_transcript(transcript)
        assert status == "failed"
        assert "ERROR" in summary

    def test_defaults_to_passed_when_no_indicators(self):
        transcript = "Everything completed successfully"
        status, summary = auto_save_signal.parse_status_from_transcript(transcript)
        assert status == "passed"


class TestExtractMarkdownSections:
    """Tests for extract_markdown_sections()"""

    def test_extracts_markdown_sections(self):
        transcript = """Some preamble text

## Summary
This is the summary.

## Analysis
Detailed analysis here.

STATUS: PASSED
"""
        result = auto_save_signal.extract_markdown_sections(transcript)
        assert "## Summary" in result
        assert "## Analysis" in result
        assert "This is the summary." in result

    def test_returns_full_transcript_if_no_sections(self):
        transcript = "Plain text without any markdown headings"
        result = auto_save_signal.extract_markdown_sections(transcript)
        assert "## Agent Output" in result
        assert transcript in result

    def test_handles_empty_transcript(self):
        result = auto_save_signal.extract_markdown_sections("")
        assert result == ""


class TestSaveReportAndSignal:
    """Tests for save_report() and save_signal()"""

    def test_save_report_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["TASK_REPORTS_DIR"] = tmpdir
            try:
                result = auto_save_signal.save_report("test-task", "performance", "# Report\nContent")
                assert result is True
                report_path = Path(tmpdir) / "test-task" / "reports" / "performance.md"
                assert report_path.exists()
                assert report_path.read_text() == "# Report\nContent"
            finally:
                del os.environ["TASK_REPORTS_DIR"]

    def test_save_signal_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["TASK_REPORTS_DIR"] = tmpdir
            try:
                result = auto_save_signal.save_signal("test-task", "security", "passed", "All good")
                assert result is True
                signal_path = Path(tmpdir) / "test-task" / "signals" / "security.json"
                assert signal_path.exists()
                data = json.loads(signal_path.read_text())
                assert data["taskId"] == "test-task"
                assert data["signalType"] == "security"
                assert data["status"] == "passed"
                assert data["summary"] == "All good"
                assert data["autoSaved"] is True
            finally:
                del os.environ["TASK_REPORTS_DIR"]


def run_tests():
    """Run all tests and report results"""
    import traceback

    test_classes = [
        TestParseWorkflowContext,
        TestFindTaskCallForAgent,
        TestParseStatusFromTranscript,
        TestExtractMarkdownSections,
        TestSaveReportAndSignal,
    ]

    total = 0
    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n{'='*60}")
        print(f"Running {test_class.__name__}")
        print('='*60)

        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total += 1
                try:
                    getattr(instance, method_name)()
                    print(f"  ✓ {method_name}")
                    passed += 1
                except AssertionError as e:
                    print(f"  ✗ {method_name}")
                    print(f"    AssertionError: {e}")
                    failed += 1
                except Exception as e:
                    print(f"  ✗ {method_name}")
                    print(f"    {type(e).__name__}: {e}")
                    traceback.print_exc()
                    failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print('='*60)

    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
