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
    parser.add_argument(
        "--webcam-probe",
        action="store_true",
        help="probe available webcam devices without opening a preview window",
    )
    parser.add_argument(
        "--webcam-preview",
        action="store_true",
        help="open a live read-only webcam preview window",
    )
    parser.add_argument(
        "--studio-composer",
        action="store_true",
        help="open the RinoVision Studio Composer window",
    )
    parser.add_argument(
        "--studio-composer-demo-layout",
        action="store_true",
        help="create a Studio Composer demo layout JSON without opening GUI",
    )
    parser.add_argument(
        "--studio-composer-demo-multilayer",
        action="store_true",
        help="create a multilayer Studio Composer demo scene without opening GUI",
    )
    parser.add_argument(
        "--camera-id",
        type=int,
        default=0,
        help="camera id for --webcam-preview",
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


def run_webcam_probe(max_devices: int = 5):
    from rinovision.capture.webcam import probe_webcams

    print("RinoVision Webcam Probe")
    results = probe_webcams(max_devices=max_devices)
    for item in results:
        if item.get("camera_id") is None:
            print(item.get("message", "Webcam probing unavailable."))
            continue
        status = "available" if item.get("available") else "unavailable"
        detail = ""
        if item.get("available"):
            detail = f" ({item.get('width', 0)}x{item.get('height', 0)} @ {item.get('fps', 0):g} fps)"
        print(f"Camera {item['camera_id']}: {status}{detail}")
    return 0


def run_webcam_preview(camera_id: int = 0):
    from rinovision.capture.webcam import preview_webcam

    print(f"Opening RinoVision webcam preview on camera {camera_id}.")
    print("Press Q or ESC to close.")
    result = preview_webcam(camera_id=camera_id)
    if result.get("ok"):
        return 0
    error = result.get("error", "Unknown webcam preview error")
    if "OpenCV is missing" in error:
        print("OpenCV is missing. Install with:")
        print("pip install opencv-python")
    elif error == "Could not open camera":
        print(f"Could not open camera {camera_id}. Try:")
        print("python main.py --webcam-probe")
        print("python main.py --webcam-preview --camera-id 1")
    else:
        print(error)
    return 1


def run_studio_composer():
    from rinovision.studio_composer.ui.studio_window import launch_studio_composer

    return launch_studio_composer()


def run_studio_composer_demo_layout():
    from rinovision.studio_composer import create_demo_layout

    result = create_demo_layout()
    print("Studio Composer demo layout complete")
    print(f"project_id: {result['project_id']}")
    print(f"layout_path: {result['layout_path']}")
    print("locked: true")
    print("recording: not enabled")
    return 0


def run_studio_composer_demo_multilayer():
    from rinovision.studio_composer import create_demo_multilayer

    result = create_demo_multilayer()
    print("Studio Composer multilayer demo complete")
    print(f"project_id: {result['project_id']}")
    print(f"layout_path: {result['layout_path']}")
    print(f"layer_count: {result['layer_count']}")
    print("recording: not enabled")
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
    if args.webcam_probe:
        sys.exit(run_webcam_probe())
    if args.webcam_preview:
        sys.exit(run_webcam_preview(args.camera_id))
    if args.studio_composer_demo_layout:
        sys.exit(run_studio_composer_demo_layout())
    if args.studio_composer_demo_multilayer:
        sys.exit(run_studio_composer_demo_multilayer())
    if args.studio_composer:
        sys.exit(run_studio_composer())
    if args.safe_foundation or args.safe_mode:
        from rinovision.ui.main_window_adapter import launch_safe_mode

        sys.exit(launch_safe_mode())
    sys.exit(launch_legacy_compositor())
