import pytest

from rinovision.core.errors import InvalidPipelineTransition
from rinovision.core.pipeline import can_transition, transition
from rinovision.core.project import create_project


def test_valid_pipeline_transition_passes():
    project = create_project("pipeline valid", "CAPTURE")
    transition(project, "CAPTURE_READY")
    assert project.status == "CAPTURE_READY"
    assert can_transition("CAPTURE_READY", "CAPTURE_RECORDED")


def test_invalid_pipeline_transition_fails():
    project = create_project("pipeline invalid", "CAPTURE")
    with pytest.raises(InvalidPipelineTransition):
        transition(project, "EXPORT_READY")
