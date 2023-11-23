import numpy as np
import os
import matplotlib.pyplot as plt
import cv2
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from imageio import imread
from skimage.transform import resize
import joblib 
import inception_model_keras as facenet

cascade_path = "./haarcascade_frontalface_alt2.xml"
image_size = 160

model_path = './facenet_keras.h5'
# model = load_model(model_path)
print("Building Model")
model = facenet.InceptionResNetV1(weights_path="./facenet_keras_weights.h5")
print("Built Facenet Model and loaded weights succesfully")
print("Model Summary:")
print(model.summary())

def prewhiten(x):
    if x.ndim == 4:
        axis = (1, 2, 3)
        size = x[0].size
    elif x.ndim == 3:
        axis = (0, 1, 2)
        size = x.size
    else:
        raise ValueError('Dimension should be 3 or 4')

    mean = np.mean(x, axis=axis, keepdims=True)
    std = np.std(x, axis=axis, keepdims=True)
    std_adj = np.maximum(std, 1.0/np.sqrt(size))
    y = (x - mean) / std_adj
    return y

def l2_normalize(x, axis=-1, epsilon=1e-10):
    output = x / np.sqrt(np.maximum(np.sum(np.square(x), axis=axis, keepdims=True), epsilon))
    return output

def load_and_align_images(filepaths, margin):
    cascade = cv2.CascadeClassifier(cascade_path)
    i = 0
    aligned_images = []
    for filepath in filepaths:
        img = imread(filepath)

        faces = cascade.detectMultiScale(img,scaleFactor=1.1,minNeighbors=3)
        try:
            if len(faces)>0:
                (x, y, w, h) = faces[0]
                cropped = img[y-margin//2:y+h+margin//2,x-margin//2:x+w+margin//2, :]
                aligned = resize(cropped, (image_size, image_size), mode='reflect')
                aligned_images.append(aligned)
        except:
            continue
    return np.array(aligned_images)

def calc_embs_live(imgs, margin, batch_size):
    aligned_images = prewhiten(imgs)
    pd = []
    for start in range(0, len(aligned_images), batch_size):
        pd.append(model.predict_on_batch(aligned_images[start:start+batch_size]))
    embs = l2_normalize(np.concatenate(pd))

    return embs

loaded_classifier = joblib.load(r'svm_classifier_model.pkl')
loaded_label_encoder = joblib.load(r'label_encoder.pkl')

def infer(le,clf,margin = 10):
        cascade = cv2.CascadeClassifier(cascade_path)
        vc = cv2.VideoCapture(0)
        if vc.isOpened():
            is_capturing, _ = vc.read()
            h,w,c = _.shape
        else:
            is_capturing = False

        while is_capturing:
            is_capturing, frame = vc.read()
            height, width, channels = frame.shape
            # Calculate the starting and ending horizontal pixels for cropping
            start_x = (width - 320) // 2  # Start from the middle
            end_x = start_x + 320  # Crop 320 pixels from the middle
            # Crop the frame to keep only the center part
            cropped_frame = frame[:, start_x:end_x, :]
            faces = cascade.detectMultiScale(cropped_frame,scaleFactor=1.1,minNeighbors=3,minSize=(100, 100))
            pred = None
            if len(faces) != 0:
                face = faces[0]
                (x, y, w, h) = face
                left = x - margin // 2
                right = x + w + margin // 2
                bottom = y - margin // 2
                top = y + h + margin // 2
                try:
                    img = resize(cropped_frame[bottom:top, left:right, :],(160, 160), mode='reflect')
                    embs = calc_embs_live(img[np.newaxis], margin, 1)
                    pred = le.inverse_transform(clf.predict(embs))
                    cv2.rectangle(cropped_frame,(left-1, bottom-1),(right+1, top+1),(255, 0, 0), thickness=2)
                    cv2.rectangle(cropped_frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(cropped_frame, pred[0], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                    print(pred[0])
                except:
                    pass
            cv2.imshow('Video', cropped_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        vc.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    infer(le = loaded_label_encoder, clf = loaded_classifier)