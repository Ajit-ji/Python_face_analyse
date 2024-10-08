from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os
import cvlib as cv

# load model
model = load_model('gender_detection.model')

# open webcam
webcam = cv2.VideoCapture(0)

# Set the resolution to 1280x720 (HD)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

classes = ['man', 'woman']

# loop through frames
while webcam.isOpened():

    # read frame from webcam
    status, frame = webcam.read()

    # apply face detection
    face, confidence = cv.detect_face(frame)

    # initialize counters for male and female in the current frame
    frame_male_count = 0
    frame_female_count = 0

    # loop through detected faces
    for idx, f in enumerate(face):

        # get corner points of face rectangle
        (startX, startY) = f[0], f[1]
        (endX, endY) = f[2], f[3]

        # draw rectangle over face
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

        # crop the detected face region
        face_crop = np.copy(frame[startY:endY, startX:endX])

        if face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
            continue

        # preprocessing for gender detection model
        face_crop = cv2.resize(face_crop, (96, 96))
        face_crop = face_crop.astype("float") / 255.0
        face_crop = img_to_array(face_crop)
        face_crop = np.expand_dims(face_crop, axis=0)

        # apply gender detection on face
        conf = model.predict(face_crop)[0]  # model.predict returns a 2D matrix

        # get label with max accuracy
        idx = np.argmax(conf)
        label = classes[idx]

        if label == 'man':
            frame_male_count += 1
        else:
            frame_female_count += 1

        label_text = "{}: {:.2f}%".format(label, conf[idx] * 100)
        Y = startY - 10 if startY - 10 > 10 else startY + 10

        # write label and confidence above face rectangle
        cv2.putText(frame, label_text, (startX, Y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Calculate the ratio of males to females
    if frame_female_count > 0:
        male_female_ratio = frame_male_count / frame_female_count
    else:
        male_female_ratio = 0  # Avoid division by zero if no females detected

    # Display male-female counts and ratio
    cv2.putText(frame, f"Males in frame: {frame_male_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Females in frame: {frame_female_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Male/Female Ratio: {male_female_ratio:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Show alert if there is more than 5 males and at least 1 female
    if frame_male_count > 5 and frame_female_count >= 1:
        cv2.putText(frame, "ALERT: More than 5 males and 1 female!", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

    # display output
    cv2.imshow("gender detection", frame)

    # press "Q" to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release resources
webcam.release()
cv2.destroyAllWindows()
