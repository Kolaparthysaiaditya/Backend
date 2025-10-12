# faceapp/views.py
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from .forms import RegisterForm
from .models import FaceSample
from .utils import detect_and_crop_face, preprocess_image_array, train_and_save_classifier, predict_user_from_image_bytes
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from django.core.files.base import ContentFile

def home(request):
    return render(request, "capture.html")

def register_page(request):
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "register.html", {"form": form})
    # POST handled via ajax for captured images
    return HttpResponse(status=405)

@csrf_exempt
def register_capture(request):
    """
    Receives: JSON { username, email, password, images: [dataURL,...] }
    Saves user and images as FaceSample and retrains classifier.
    """
    import json
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = json.loads(request.body.decode())
    username = data.get("username")
    email = data.get("email","")
    password = data.get("password")
    images = data.get("images", [])
    if not username or not password or len(images) < 3:
        return JsonResponse({"error": "require username, password and at least 3 images"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "username exists"}, status=400)
    user = User.objects.create_user(username=username, email=email, password=password)
    # save face images
    for idx, dataurl in enumerate(images):
        header, encoded = dataurl.split(",", 1)
        data_bytes = base64.b64decode(encoded)
        fname = f"{username}_{idx}.jpg"
        fs = FaceSample(user=user)
        fs.image.save(fname, ContentFile(data_bytes))
        fs.save()
    # retrain classifier
    ok, msg = train_and_save_classifier()
    if not ok:
        return JsonResponse({"error": msg}, status=500)
    return JsonResponse({"status": "registered"})

@csrf_exempt
def login_capture(request):
    """
    Receives JSON: { image: dataURL }
    Returns: { predicted_user, confidence } if recognized above threshold
    """
    import json
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    
    data = json.loads(request.body.decode())
    dataurl = data.get("image")
    if not dataurl:
        return JsonResponse({"error": "no image"}, status=400)
    
    header, encoded = dataurl.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    pred, conf, err = predict_user_from_image_bytes(img_bytes)
    if err:
        return JsonResponse({"error": err}, status=400)
    
    # choose threshold; adjust as needed
    if conf < 0.5:
        return JsonResponse({"status": "unknown", "confidence": conf})
    
    # Authenticate and log user in
    user = None
    try:
        user = User.objects.get(username=pred)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
    # Optionally log them in (session-based)
    # auth_login(request, user)  # if you want to set Django session
    
    auth_login(request, user)

    return JsonResponse({
        "status": "ok",
        "predicted_user": pred,
        "confidence": conf
    })

def hello(request):
    return render(request, "eee.html")