from .errors import InvalidPipelineTransition, InvalidStateError
from .project import save_project


STATES = [
    "PROJECT_CREATED",
    "MEDIA_IMPORTED",
    "CAPTURE_READY",
    "CAPTURE_RECORDED",
    "AUDIO_EXTRACTED",
    "TRANSCRIBED",
    "SUBTITLES_GENERATED",
    "FRAMES_EXTRACTED",
    "AI_SCRIPT_CREATED",
    "AI_STORYBOARD_CREATED",
    "AI_PROMPTS_CREATED",
    "AI_VIDEO_REQUESTED",
    "AI_VIDEO_GENERATED_RAW",
    "AI_VIDEO_IMPORTED_FOR_EDITING",
    "EDIT_PLAN_CREATED",
    "VIDEO_EDITED",
    "THUMBNAIL_GENERATED",
    "SOCIAL_POST_GENERATED",
    "QC_READY",
    "QC_APPROVED",
    "EXPORT_READY",
    "FAILED",
]

TERMINAL_STATES = {"EXPORT_READY", "FAILED"}

TRANSITIONS = {
    "PROJECT_CREATED": {"MEDIA_IMPORTED", "CAPTURE_READY", "AI_SCRIPT_CREATED", "EDIT_PLAN_CREATED", "FAILED"},
    "MEDIA_IMPORTED": {"EDIT_PLAN_CREATED", "AUDIO_EXTRACTED", "FRAMES_EXTRACTED", "FAILED"},
    "CAPTURE_READY": {"CAPTURE_RECORDED", "FAILED"},
    "CAPTURE_RECORDED": {"MEDIA_IMPORTED", "AUDIO_EXTRACTED", "FAILED"},
    "AUDIO_EXTRACTED": {"TRANSCRIBED", "FAILED"},
    "TRANSCRIBED": {"SUBTITLES_GENERATED", "FAILED"},
    "SUBTITLES_GENERATED": {"EDIT_PLAN_CREATED", "FAILED"},
    "FRAMES_EXTRACTED": {"EDIT_PLAN_CREATED", "FAILED"},
    "AI_SCRIPT_CREATED": {"AI_STORYBOARD_CREATED", "FAILED"},
    "AI_STORYBOARD_CREATED": {"AI_PROMPTS_CREATED", "FAILED"},
    "AI_PROMPTS_CREATED": {"AI_VIDEO_REQUESTED", "FAILED"},
    "AI_VIDEO_REQUESTED": {"AI_VIDEO_GENERATED_RAW", "FAILED"},
    "AI_VIDEO_GENERATED_RAW": {"AI_VIDEO_IMPORTED_FOR_EDITING", "FAILED"},
    "AI_VIDEO_IMPORTED_FOR_EDITING": {"EDIT_PLAN_CREATED", "FAILED"},
    "EDIT_PLAN_CREATED": {"VIDEO_EDITED", "THUMBNAIL_GENERATED", "QC_READY", "FAILED"},
    "VIDEO_EDITED": {"THUMBNAIL_GENERATED", "QC_READY", "EXPORT_READY", "FAILED"},
    "THUMBNAIL_GENERATED": {"SOCIAL_POST_GENERATED", "QC_READY", "EXPORT_READY", "FAILED"},
    "SOCIAL_POST_GENERATED": {"QC_READY", "EXPORT_READY", "FAILED"},
    "QC_READY": {"QC_APPROVED", "FAILED"},
    "QC_APPROVED": {"EXPORT_READY", "FAILED"},
    "EXPORT_READY": set(),
    "FAILED": set(),
}


def validate_state(state: str) -> str:
    if state not in STATES:
        raise InvalidStateError(f"invalid pipeline state: {state}")
    return state


def can_transition(from_state: str, to_state: str) -> bool:
    validate_state(from_state)
    validate_state(to_state)
    return to_state in TRANSITIONS[from_state]


def transition(project, to_state: str):
    validate_state(to_state)
    if not can_transition(project.status, to_state):
        raise InvalidPipelineTransition(f"{project.status} -> {to_state}")
    project.status = to_state
    project.touch()
    save_project(project)
    return project


def state_order() -> list[str]:
    return list(STATES)


def is_terminal_state(state: str) -> bool:
    validate_state(state)
    return state in TERMINAL_STATES
