import cv2
import numpy as np
import mediapipe as mp

class MeasurementError(Exception):
    pass

def measure_clothes(image_file):
    """
    Process the uploaded image and return clothing measurements.
    
    Args:
        image_file: File object containing the image
    
    Returns:
        dict: Dictionary containing arm_size and chest_size measurements
    """
    # Read image file
    image_stream = image_file.read()
    nparr = np.frombuffer(image_stream, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise MeasurementError("Failed to process image")

    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    
    # Convert image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        raise MeasurementError("No person detected in the image")

    # Get landmarks
    landmarks = results.pose_landmarks.landmark
    
    # Calculate arm size (right arm)
    shoulder = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * image.shape[1],
                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * image.shape[0]])
    wrist = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x * image.shape[1],
                      landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y * image.shape[0]])
    arm_size = np.linalg.norm(shoulder - wrist)  # in pixels

    # Calculate chest size
    left_shoulder = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * image.shape[1],
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * image.shape[0]])
    right_shoulder = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * image.shape[1],
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * image.shape[0]])
    
    # Chest width is the distance between shoulders
    chest_width = np.linalg.norm(left_shoulder - right_shoulder)
    
    # Estimate chest size (circumference) using an approximation
    # Assuming chest depth is roughly 70% of chest width
    chest_depth = chest_width * 0.7
    chest_size = 2 * (chest_width + chest_depth)  # approximate circumference

    # Convert measurements from pixels to centimeters (approximate conversion)
    # Assuming average shoulder width of 45cm for calibration
    SHOULDER_WIDTH_CM = 45.0
    pixel_to_cm = SHOULDER_WIDTH_CM / chest_width
    
    measurements = {
        'arm_size': round(arm_size * pixel_to_cm, 1),  # in cm
        'chest_size': round(chest_size * pixel_to_cm, 1)  # in cm
    }

    return measurements
