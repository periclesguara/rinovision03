class RinoVisionError(Exception):
    """Base exception for the RinoVision foundation."""


class PathSafetyError(RinoVisionError, ValueError):
    """Raised when a path escapes an allowed base directory."""


class InvalidStateError(RinoVisionError, ValueError):
    """Raised when a pipeline state is unknown or invalid."""


class InvalidPipelineTransition(InvalidStateError):
    """Raised when a project state transition is not allowed."""


class ArtifactError(RinoVisionError, ValueError):
    """Raised when artifact persistence or validation fails."""


class ProjectError(RinoVisionError, ValueError):
    """Raised when project persistence or validation fails."""


class ProviderError(RinoVisionError):
    """Raised when a provider adapter fails."""
