import json
from subprocess import CompletedProcess, CalledProcessError
from unittest.mock import patch

import pytest

from app.tools.container import get_container_details, get_container_logs, get_container_status


def test_container_status_parses_docker_stats():
    output = json.dumps({"Name": "api-1", "CPUPerc": "1.5%", "MemUsage": "20MiB / 1GiB", "MemPerc": "2%"})
    with patch("app.tools.container.subprocess.run", return_value=CompletedProcess([], 0, stdout=output)) as run:
        assert get_container_status() == [{"name": "api-1", "cpu_percent": "1.5%", "memory_usage": "20MiB / 1GiB", "memory_percent": "2%"}]
        assert run.call_args.kwargs["timeout"] == 15


def test_container_details_reports_exited_state():
    payload = [{"Name": "/fault-lab-api", "RestartCount": 0, "State": {"Status": "exited", "Running": False, "OOMKilled": False, "ExitCode": 1, "StartedAt": "start", "FinishedAt": "finish"}}]
    with patch("app.tools.container.subprocess.run", return_value=CompletedProcess([], 0, stdout=json.dumps(payload))) as run:
        result = get_container_details("fault-lab-api")
        assert result["status"] == "exited"
        assert result["exit_code"] == 1
        assert result["oom_killed"] is False
        assert run.call_args.args[0] == ["docker", "inspect", "fault-lab-api"]


@pytest.mark.parametrize("tail,expected", [(0, 1), (10, 10), (999, 200)])
def test_container_logs_clamps_tail(tail, expected):
    with patch("app.tools.container.subprocess.run", return_value=CompletedProcess([], 0, stdout="hello", stderr=" error")) as run:
        result = get_container_logs("fault-lab-api", tail=tail)
        assert result["tail"] == expected
        assert result["logs"] == "hello error"
        assert run.call_args.args[0] == ["docker", "logs", "--tail", str(expected), "fault-lab-api"]


def test_docker_failure_propagates():
    with patch("app.tools.container.subprocess.run", side_effect=CalledProcessError(1, ["docker", "inspect"])):
        with pytest.raises(CalledProcessError):
            get_container_details("missing")
