from __future__ import annotations

import pickle


def dependencies_available() -> bool:
    try:
        import cv2  # noqa: F401
        import face_recognition  # noqa: F401

        return True
    except Exception:
        return False


def capture_face_encoding() -> bytes:
    import cv2
    import face_recognition

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Could not access camera.")

    try:
        for _ in range(80):
            ok, frame = cam.read()
            if not ok:
                continue
            rgb = frame[:, :, ::-1]
            locations = face_recognition.face_locations(rgb)
            if not locations:
                continue
            encodings = face_recognition.face_encodings(rgb, locations)
            if encodings:
                return pickle.dumps(encodings[0])
        raise RuntimeError("No face detected. Try better lighting.")
    finally:
        cam.release()


def verify_face(stored_blob: bytes, tolerance: float = 0.5) -> bool:
    import cv2
    import face_recognition

    stored_encoding = pickle.loads(stored_blob)
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Could not access camera.")

    try:
        for _ in range(80):
            ok, frame = cam.read()
            if not ok:
                continue
            rgb = frame[:, :, ::-1]
            locations = face_recognition.face_locations(rgb)
            if not locations:
                continue
            encodings = face_recognition.face_encodings(rgb, locations)
            if encodings:
                result = face_recognition.compare_faces(
                    [stored_encoding], encodings[0], tolerance=tolerance
                )
                return bool(result[0])
        return False
    finally:
        cam.release()
