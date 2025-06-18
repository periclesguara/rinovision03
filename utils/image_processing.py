import cv2
import numpy as np


def apply_blur(frame, ksize=(15, 15)):
    """
    Aplica blur (desfoque) na imagem.
    """
    return cv2.GaussianBlur(frame, ksize, 0)


def apply_grayscale(frame):
    """
    Converte a imagem para preto e branco.
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def apply_contrast_brightness(frame, contrast=1.0, brightness=0):
    """
    Ajusta contraste e brilho.
    contrast: 1.0 = neutro (maior que 1 = mais contraste, menor = menos)
    brightness: 0 = neutro (positivo = mais claro, negativo = mais escuro)
    """
    return cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)


def apply_invert(frame):
    """
    Inverte as cores da imagem.
    """
    return cv2.bitwise_not(frame)


def apply_sepia(frame):
    """
    Aplica efeito sépia na imagem.
    """
    kernel = np.array(
        [[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]]
    )
    sepia_frame = cv2.transform(frame, kernel)
    sepia_frame = np.clip(sepia_frame, 0, 255)
    return sepia_frame.astype(np.uint8)


def resize_frame(frame, width, height):
    """
    Redimensiona o frame para o tamanho desejado.
    """
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)


def rotate_frame(frame, angle):
    """
    Rotaciona o frame no ângulo desejado (graus).
    """
    h, w = frame.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(frame, matrix, (w, h))
