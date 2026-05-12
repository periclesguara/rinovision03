from abc import ABC, abstractmethod

from rinovision.ai_video_creator.job_models import AIVideoJob


class AIVideoProvider(ABC):
    name: str

    @abstractmethod
    def create_video_job(self, prompt_payload: dict) -> AIVideoJob:
        raise NotImplementedError

    @abstractmethod
    def get_video_job(self, job_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def download_video(self, job_id: str, destination_path: str) -> dict:
        raise NotImplementedError
