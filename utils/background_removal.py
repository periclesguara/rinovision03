import cv2
import numpy as np
import mediapipe as mp


class BackgroundRemover:
    def __init__(self):
        self.selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(
            model_selection=1
        )

    def remove_background(self, frame, bg_color=(0, 0, 0), transparent=False):
        """
        Remove o fundo de uma imagem/frame.

        Parâmetros:
        - frame: imagem numpy (BGR)
        - bg_color: cor do fundo (se não for transparente)
        - transparent: True para fundo transparente (RGBA)

        Retorna:
        - imagem com fundo removido (BGR ou RGBA)
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.selfie_segmentation.process(frame_rgb)

        mask = results.segmentation_mask
        condition = mask > 0.5

        bg_image = np.zeros(frame.shape, dtype=np.uint8)
        bg_image[:] = bg_color

        output_image = np.where(condition[:, :, None], frame, bg_image)

        if transparent:
            # Adiciona canal alpha
            alpha_channel = (condition * 255).astype(np.uint8)
            b, g, r = cv2.split(output_image)
            rgba = cv2.merge((b, g, r, alpha_channel))
            return rgba
        else:
            return output_image

    def apply_blur_background(self, frame):
        """
        Remove o fundo e aplica blur no fundo.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.selfie_segmentation.process(frame_rgb)

        mask = results.segmentation_mask
        condition = mask > 0.5

        blurred = cv2.GaussianBlur(frame, (55, 55), 0)

        output_image = np.where(condition[:, :, None], frame, blurred)

        return output_image
