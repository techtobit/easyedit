import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from utils.viewLog import logger
from mediapipe.tasks.python import vision

# -----------------------------
# Load Face Landmarker Model
# -----------------------------
base_options = python.BaseOptions(
	model_asset_path="models/face_landmarker.task"
)

options = vision.FaceLandmarkerOptions(
	base_options=base_options,
	num_faces=1,
	output_face_blendshapes=True,
	output_facial_transformation_matrixes=True,
)

landmarker = vision.FaceLandmarker.create_from_options(options)


# -----------------------------
# Detect landmarks
# -----------------------------
def detect_landmarks(image: np.ndarray):

	mp_image = mp.Image(
		image_format=mp.ImageFormat.SRGB,
		data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
	)
	result = landmarker.detect(mp_image)
	if not result.face_landmarks:
		return None
	return result.face_landmarks[0]


# -----------------------------
# Extract key face points
# -----------------------------
def get_face_points(landmarks, img_w, img_h):
    """
    Extract eye center and chin using MediaPipe landmark indices.
    """

    def p(i):
        return np.array([
            landmarks[i].x * img_w,
            landmarks[i].y * img_h
        ])

    left_eye = p(33)
    right_eye = p(263)
    chin = p(152)

    eye_center = (left_eye + right_eye) / 2
    return eye_center, chin


# -----------------------------
# Crop face
# -----------------------------
def crop_face(image, eye_center, chin, input_width, input_height):
    img_h, img_w = image.shape[:2]

    face_height = np.linalg.norm(chin - eye_center) * 2.0
    crop_h = face_height / 0.5
    crop_w = crop_h * (input_width / input_height)

    cx, cy = eye_center

    top = int(cy - crop_h * 0.4)
    bottom = int(top + crop_h)
    left = int(cx - crop_w / 2)
    right = int(left + crop_w)

    # Clamp
    top = max(0, top)
    left = max(0, left)
    bottom = min(img_h, bottom)
    right = min(img_w, right)

    return image[top:bottom, left:right]


# -----------------------------
# Resize
# -----------------------------
def resize_image(image, width, height):
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)


# -----------------------------
# Full pipeline
# -----------------------------
async def detect_and_crop(image, input_width, input_height):
	landmarks = detect_landmarks(image)
	if landmarks is None:
		return None
	img_h, img_w = image.shape[:2]
	eye_center, chin = get_face_points(landmarks, img_w, img_h)
	
	cropped = crop_face(image, eye_center, chin, input_width, input_height)
	cv2.imwrite("cropped_face.jpg", cropped)
	return resize_image(cropped, input_width, input_height)
