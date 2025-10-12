# faceapp/utils.py
import os
import io
import numpy as np
from PIL import Image
import cv2
from django.conf import settings
from sklearn.decomposition import PCA
from sklearn.svm import SVC
import pickle
from .models import FaceSample, User

# config
IMG_SIZE = (100, 100)  # resize face region (width, height)
CLASSIFIER_PATH = os.path.join(settings.BASE_DIR, "classifier.pkl")
PCA_PATH = os.path.join(settings.BASE_DIR, "pca.pkl")

# face detector (OpenCV Haar cascade)
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

def read_imagefile(file_bytes):
    # file_bytes: binary bytes (from request.FILES or base64 decoded)
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return np.array(image)

def detect_and_crop_face(rgb_image):
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    x,y,w,h = faces[0]  # take first detected face
    face = rgb_image[y:y+h, x:x+w]
    face = cv2.resize(face, IMG_SIZE)
    gray_face = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)
    return gray_face

def preprocess_image_array(gray_face):
    # flatten, normalize
    arr = gray_face.flatten().astype(np.float32) / 255.0
    return arr

def build_dataset():
    # return X (n_samples, n_features), y (labels)
    samples = FaceSample.objects.select_related("user").all()
    X, y = [], []
    for s in samples:
        fpath = s.image.path
        img = Image.open(fpath).convert("RGB")
        arr = np.array(img)
        face = detect_and_crop_face(arr)
        if face is None:
            continue
        X.append(preprocess_image_array(face))
        y.append(s.user.username)
    if len(X) == 0:
        return None, None
    X = np.vstack(X)
    y = np.array(y)
    return X, y

def train_and_save_classifier():
    X, y = build_dataset()
    if X is None:
        return False, "No face samples to train."
    # PCA to reduce dimensionality
    pca = PCA(n_components=min(100, X.shape[1], X.shape[0]-1))
    Xp = pca.fit_transform(X)
    clf = SVC(kernel="linear", probability=True)
    clf.fit(Xp, y)
    # save
    with open(CLASSIFIER_PATH, "wb") as f:
        pickle.dump(clf, f)
    with open(PCA_PATH, "wb") as f:
        pickle.dump(pca, f)
    return True, "Trained"

def load_models():
    if not (os.path.exists(CLASSIFIER_PATH) and os.path.exists(PCA_PATH)):
        return None, None
    with open(CLASSIFIER_PATH, "rb") as f:
        clf = pickle.load(f)
    with open(PCA_PATH, "rb") as f:
        pca = pickle.load(f)
    return clf, pca

def predict_user_from_image_bytes(img_bytes):
    rgb = read_imagefile(img_bytes)
    face = detect_and_crop_face(rgb)
    if face is None:
        return None, 0.0, "No face detected"
    x = preprocess_image_array(face).reshape(1, -1)
    clf, pca = load_models()
    if clf is None:
        return None, 0.0, "No classifier trained"
    xp = pca.transform(x)
    probs = clf.predict_proba(xp)[0]
    pred = clf.classes_[np.argmax(probs)]
    confidence = float(np.max(probs))
    return pred, confidence, None
