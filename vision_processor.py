import cv2
import mediapipe as mp
import numpy as np

class VisionProcessor:
    """
    Handles pose estimation and exercise rep counting using MediaPipe.
    """
    def __init__(self):
        # Initialize MediaPipe Pose solution
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # Rep counting variables for different exercises
        self.counters = {
            'bicep_curl': 0,
            'squat': 0,
            'push_up': 0
        }
        self.states = {
            'bicep_curl': 'down',
            'squat': 'up',
            'push_up': 'up'
        }
        self.feedback = {
            'bicep_curl': '',
            'squat': '',
            'push_up': ''
        }

    @staticmethod
    def calculate_angle(a, b, c):
        """Calculates the angle between three points."""
        a = np.array(a)  # First point
        b = np.array(b)  # Mid point
        c = np.array(c)  # End point

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle
        return angle

    def process_frame(self, frame, exercise_type):
        """Processes a single video frame to detect pose and count reps."""
        # Recolor image to RGB for MediaPipe
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        results = self.pose.process(image)

        # Recolor back to BGR for OpenCV
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks and perform exercise logic
        try:
            landmarks = results.pose_landmarks.landmark
            if exercise_type == 'bicep_curl':
                self._process_bicep_curl(landmarks)
            elif exercise_type == 'squat':
                self._process_squat(landmarks)
            elif exercise_type == 'push_up':
                self._process_push_up(landmarks)

        except Exception as e:
            # This can happen if no pose is detected in the frame
            pass

        # Draw the pose annotations on the image.
        self.mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
            self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2),
        )

        return {
            "frame": image,
            "rep_count": self.counters[exercise_type],
            "feedback": self.feedback[exercise_type]
        }

    def _process_bicep_curl(self, landmarks):
        """Logic for counting bicep curls."""
        lm = self.mp_pose.PoseLandmark
        
        # Get coordinates for right arm
        shoulder = [landmarks[lm.RIGHT_SHOULDER.value].x, landmarks[lm.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[lm.RIGHT_ELBOW.value].x, landmarks[lm.RIGHT_ELBOW.value].y]
        wrist = [landmarks[lm.RIGHT_WRIST.value].x, landmarks[lm.RIGHT_WRIST.value].y]

        # Calculate angle
        angle = self.calculate_angle(shoulder, elbow, wrist)
        
        # Curl counter logic
        if angle > 160:
            self.states['bicep_curl'] = "down"
            self.feedback['bicep_curl'] = "Ready to curl"
        if angle < 30 and self.states['bicep_curl'] == 'down':
            self.states['bicep_curl'] = "up"
            self.counters['bicep_curl'] += 1
            self.feedback['bicep_curl'] = "Great rep!"

    def _process_squat(self, landmarks):
        """Logic for counting squats."""
        lm = self.mp_pose.PoseLandmark
        
        # Get coordinates
        hip = [landmarks[lm.RIGHT_HIP.value].x, landmarks[lm.RIGHT_HIP.value].y]
        knee = [landmarks[lm.RIGHT_KNEE.value].x, landmarks[lm.RIGHT_KNEE.value].y]
        ankle = [landmarks[lm.RIGHT_ANKLE.value].x, landmarks[lm.RIGHT_ANKLE.value].y]

        # Calculate angle
        angle = self.calculate_angle(hip, knee, ankle)

        # Squat counter logic
        if angle > 160:
            self.states['squat'] = "up"
            self.feedback['squat'] = "Ready to squat"
        if angle < 90 and self.states['squat'] == 'up':
            self.states['squat'] = 'down'
            self.counters['squat'] += 1
            self.feedback['squat'] = "Nice depth!"

    def _process_push_up(self, landmarks):
        """Logic for counting push-ups."""
        lm = self.mp_pose.PoseLandmark
        
        # Get coordinates
        shoulder = [landmarks[lm.RIGHT_SHOULDER.value].x, landmarks[lm.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[lm.RIGHT_ELBOW.value].x, landmarks[lm.RIGHT_ELBOW.value].y]
        wrist = [landmarks[lm.RIGHT_WRIST.value].x, landmarks[lm.RIGHT_WRIST.value].y]

        # Calculate angle
        angle = self.calculate_angle(shoulder, elbow, wrist)

        # Push-up counter logic
        if angle > 160:
            self.states['push_up'] = "up"
            self.feedback['push_up'] = "Ready"
        if angle < 90 and self.states['push_up'] == 'up':
            self.states['push_up'] = 'down'
            self.counters['push_up'] += 1
            self.feedback['push_up'] = "Solid push-up!"
