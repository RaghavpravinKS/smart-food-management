import face_recognition as fr
from hx711 import HX711  
import RPi.GPIO as GPIO
import cv2
import numpy as np
import joblib
import os
import csv
from datetime import datetime

cascade_path = "./haarcascade_frontalface_alt2.xml"
image_size = 160

GPIO.setmode(GPIO.BCM) 
hx = HX711(dout_pin=21, pd_sck_pin=20, gain_channel_A=128, select_channel='B')

err = hx.reset()  
if err:  
    print('not ready')
else:
    print('Ready to use')

hx.set_gain_A( gain=64)  
hx.select_channel(channel='A')

ratio = 1000

hx.set_scale_ratio(ratio)

# while True:
#     try:
#         wasted = hx.get_weight_mean(30)
#         if wasted > 100:
#             person = fr.infer(le="./label_encoder.pkl",clf="./svm_classifier_model.pkl")
#             print(f"{person} wasted {wasted} grams of food.")
#     except:
#         pass

current_date = datetime.now().strftime(r"%Y%m%d")
csv_file_name = f'Data_{current_date}.csv'
header = ['Time', 'Mail ID','Name', 'Roll No', 'Amount Wasted']

def infer(le,clf,header,margin = 10):
        with open(csv_file_name, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if os.path.getsize(csv_file_name) == 0:
                csv_writer.writerow(header)
        cascade = cv2.CascadeClassifier(cascade_path)
        vc = cv2.VideoCapture(0)
        if vc.isOpened():
            is_capturing, _ = vc.read()
            h,w,c = _.shape
        else:
            is_capturing = False

        while is_capturing:
            wasted = hx.get_weight_mean(30)
            is_capturing, frame = vc.read()
            height, width, channels = frame.shape
            # Calculate the starting and ending horizontal pixels for cropping
            start_x = (width - 320) // 2  # Start from the middle
            end_x = start_x + 320  # Crop 320 pixels from the middle
            # Crop the frame to keep only the center part
            cropped_frame = frame[:, start_x:end_x, :]
            faces = cascade.detectMultiScale(cropped_frame,scaleFactor=1.1,minNeighbors=3,minSize=(100, 100))
            pred = None
            if len(faces) != 0 :
                face = faces[0]
                (x, y, w, h) = face
                left = x - margin // 2
                right = x + w + margin // 2
                bottom = y - margin // 2
                top = y + h + margin // 2
                try:
                    img = fr.resize(cropped_frame[bottom:top, left:right, :],(160, 160), mode='reflect')
                    embs = fr.calc_embs_live(img[np.newaxis], margin, 1)
                    predicted_probabilities = clf.predict_proba(embs)
                    confidence_scores = predicted_probabilities.max(axis=1)
                    confidence_scores_percentage = confidence_scores * 100
                    pred = le.inverse_transform(clf.predict(embs))
                    cv2.rectangle(cropped_frame,(left-1, bottom-1),(right+1, top+1),(255, 0, 0), thickness=2)
                    cv2.rectangle(cropped_frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(cropped_frame, pred[0], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                    # print(f"{predicted_labels_original[0]} wasted {wasted} grams of food.")
                    if wasted > 100 and (confidence_scores_percentage[0] > 53.0):
                        print(f"{pred[0]}, Confidence: {confidence_scores_percentage[0]}, Food Wasted: {wasted}g")
                        data = [datetime.now().strftime(r"%H:%M:%S"),"mail",pred[0],"roll no",wasted]
                        csv_writer.writerow(data)

                except:
                    pass
            cv2.imshow('Video', cropped_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        vc.release()
        cv2.destroyAllWindows()

label_encoder = joblib.load("./label_encoder.pkl")
classifier = joblib.load("./svm_classifier_model.pkl")
infer(le=label_encoder,clf=classifier,header=header)