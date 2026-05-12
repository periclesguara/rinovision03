from rinovision.core.artifact_registry import load_artifacts


def build_context(project) -> dict:
    return {
        "project": project.to_dict(),
        "artifacts": [artifact.to_dict() for artifact in load_artifacts(project.id)],
    }
