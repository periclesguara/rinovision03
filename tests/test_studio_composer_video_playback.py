from rinovision.studio_composer.video_playback import VideoLayerPlayer


class FakeCapture:
    opened = 0
    released = 0

    def __init__(self, path):
        self.path = path
        FakeCapture.opened += 1
        self.read_count = 0

    def isOpened(self):
        return True

    def read(self):
        self.read_count += 1
        if self.read_count > 1:
            return False, None
        return True, "frame"

    def release(self):
        FakeCapture.released += 1


class FakeCv2:
    VideoCapture = FakeCapture


def test_video_player_does_not_open_until_play(tmp_path, monkeypatch):
    FakeCapture.opened = 0
    path = tmp_path / "video.mp4"
    path.write_bytes(b"placeholder")
    monkeypatch.setattr("rinovision.studio_composer.video_playback._import_cv2", lambda: FakeCv2)

    player = VideoLayerPlayer(path)

    assert FakeCapture.opened == 0
    assert player.is_playing() is False


def test_video_player_play_read_pause(tmp_path, monkeypatch):
    FakeCapture.opened = 0
    FakeCapture.released = 0
    path = tmp_path / "video.mp4"
    path.write_bytes(b"placeholder")
    monkeypatch.setattr("rinovision.studio_composer.video_playback._import_cv2", lambda: FakeCv2)

    player = VideoLayerPlayer(path)

    assert player.play()["ok"] is True
    assert FakeCapture.opened == 1
    assert player.read_frame() == "frame"
    assert player.pause()["playing"] is False
    assert FakeCapture.released == 1


def test_video_player_missing_cv2_does_not_crash(tmp_path, monkeypatch):
    path = tmp_path / "video.mp4"
    path.write_bytes(b"placeholder")
    monkeypatch.setattr("rinovision.studio_composer.video_playback._import_cv2", lambda: None)

    player = VideoLayerPlayer(path)
    status = player.play()

    assert status["ok"] is False
    assert "opencv-python" in status["missing_dependencies"]
