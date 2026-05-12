import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from utils.logger import setup_logger

logger = setup_logger()
logger.info("🚀 RinoVision iniciado com sucesso!")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="RinoVision03 legacy launcher")
    parser.add_argument(
        "--safe-foundation",
        action="store_true",
        help="alias for --safe-mode",
    )
    parser.add_argument(
        "--safe-mode",
        action="store_true",
        help="launch the safe RinoVision foundation adapter or print a CLI fallback",
    )
    parser.add_argument(
        "--healthcheck",
        action="store_true",
        help="run the RinoVision healthcheck",
    )
    parser.add_argument(
        "--ai-video-demo",
        action="store_true",
        help="run the AI Video Maker stub flow",
    )
    parser.add_argument(
        "--editing-demo",
        action="store_true",
        help="run the editing pipeline stub flow",
    )
    parser.add_argument(
        "--ai-video-creator-demo",
        action="store_true",
        help="run the AI Video Creator brief-to-editing local stub flow",
    )
    return parser.parse_args(argv)


def launch_legacy_compositor():
    from PySide6.QtWidgets import QApplication
    from windows.compositor_window import CompositorWindow

    app = QApplication(sys.argv)
    window = CompositorWindow()
    window.show()
    return app.exec()


def run_healthcheck():
    from scripts.rinovision_healthcheck import main as healthcheck_main

    return healthcheck_main()


def run_ai_video_demo():
    from rinovision.ai_video.prompt_builder import generate_prompts
    from rinovision.ai_video.raw_video_importer import (
        create_provider_request,
        import_raw_ai_video,
        send_to_editing,
        simulate_provider_response,
    )
    from rinovision.ai_video.script_generator import generate_script
    from rinovision.ai_video.storyboard import generate_storyboard
    from rinovision.core.project import create_project

    project = create_project("AI Video Demo", "AI_VIDEO", {"source": "main.py --ai-video-demo"})
    script = generate_script(project, "RinoVision creator pipeline demo")
    storyboard = generate_storyboard(project, script)
    prompts = generate_prompts(project, storyboard)
    request = create_provider_request(project, prompts)
    simulate_provider_response(project, request)
    raw = import_raw_ai_video(project)
    imported = send_to_editing(project, raw)
    print("AI Video Maker demo complete")
    print(f"project_id: {project.id}")
    print(f"status: {project.status}")
    print(f"editing_input: {imported.path}")
    return 0


def run_editing_demo():
    from rinovision.core.artifact_registry import register_artifact
    from rinovision.core.project import create_project
    from rinovision.editing.compositor import render_basic_edit
    from rinovision.editing.edit_plan import create_edit_plan
    from rinovision.editing.exporter import export_package, generate_thumbnail_placeholder
    from rinovision.editing.subtitles import generate_subtitles_placeholder
    from rinovision.paths import make_artifact_path

    project = create_project("Editing Demo", "EDITING_ONLY", {"source": "main.py --editing-demo"})
    source_path = make_artifact_path("input", f"{project.id}_editing_demo_source.placeholder")
    source_path.write_text("RinoVision editing demo source placeholder.\n", encoding="utf-8")
    source = register_artifact(project, "RAW_VIDEO", source_path, "Editing demo source", {"stub": True})
    plan = create_edit_plan(project, source)
    edited = render_basic_edit(project, plan)
    subtitle = generate_subtitles_placeholder(project, "RinoVision editing demo")
    thumbnail = generate_thumbnail_placeholder(project)
    package = export_package(project, [edited, subtitle, thumbnail])
    print("Editing pipeline demo complete")
    print(f"project_id: {project.id}")
    print(f"status: {project.status}")
    print(f"export_package: {package.path}")
    return 0


def run_ai_video_creator_demo():
    from rinovision.ai_video_creator import run_ai_video_creator_flow

    result = run_ai_video_creator_flow()
    project = result["project"]
    job = result["job"]
    editing_input = result["artifacts"]["editing_input"]
    print("AI Video Creator demo complete")
    print(f"project_id: {project.id}")
    print(f"job_id: {job.id}")
    print(f"status: {project.status}")
    print(f"raw_video_path: {job.raw_video_path}")
    print(f"editing_input: {editing_input.path}")
    print(f"social_package_path: {result['social_package_path']}")
    return 0

if __name__ == "__main__":
    args = parse_args()
    if args.healthcheck:
        sys.exit(run_healthcheck())
    if args.ai_video_demo:
        sys.exit(run_ai_video_demo())
    if args.editing_demo:
        sys.exit(run_editing_demo())
    if args.ai_video_creator_demo:
        sys.exit(run_ai_video_creator_demo())
    if args.safe_foundation or args.safe_mode:
        from rinovision.ui.main_window_adapter import launch_safe_mode

        sys.exit(launch_safe_mode())
    sys.exit(launch_legacy_compositor())
