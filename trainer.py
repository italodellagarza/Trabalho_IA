'''
trainer.py
Treina um modelo de SVM a partir de embedding vectors extraídos das imagens
Adaptado de <http://krasserm.github.io/2018/02/07/deep-face-recognition/>
'''
from model import create_model
import numpy as np
import os
from joblib import dump
from person import Person
from image_align import align_image
import cv2 as cv
from matplotlib import pyplot as plt
from sklearn.svm import LinearSVC
from sklearn.preprocessing import LabelEncoder

'''Função para carregar uma imagem pelo OpenCV'''
def load_image(path):
    img = cv.imread(path, 1)
    # OpenCV carrega as imagens no canal de cores
    # na ordem BGR. Então, é necessário invertê-las
    return img[...,::-1]

'''Função para carregar as pessoas no dataset'''
def load_persons(path):
    persons = []
    for i in os.listdir(path):
        for f in os.listdir(os.path.join(path, i)):
            persons.append(Person(path, i, f))
    return np.array(persons)

# Cria o modelo de rede neural Inception
nn4_small2_pretrained = create_model()
# Carrega os pesos para essa rede neural já treinada
nn4_small2_pretrained.load_weights('weights/nn4.small2.v1.h5')
# carrega as pessoas (faces) registradas no dataset
persons = load_persons("dataset")

# calcula o embedding vector utilizando a rede pré-treinada
embedded = np.zeros((persons.shape[0], 128))

for i, m in enumerate(persons):
    img = load_image(m.image_path())
    img = align_image(img)
    if img is None:
        pass
    else:
        # escala os valores RGB no intervalo [0,1]
        img = (img / 255.).astype(np.float32)
        # obter os vetores embedding por imagem
        embedded[i] = nn4_small2_pretrained.predict(np.expand_dims(img, axis=0))[0]
        # grava no vetor persons o seu embeddign vecor
        m.embedded = embedded[i]

persons = [p for p in persons if p.embedded.any()]
embedded = [p.embedded for p in persons]

targets = np.array([p.name for p in persons])

# Transforma os nomes das pessoas em números
encoder = LabelEncoder()
encoder.fit(targets)
y = encoder.transform(targets)

# Treina o modelo SVM
svc = LinearSVC()
svc.fit(embedded, y)

# Salva os modelos
dump(svc, 'saved_model.joblib')
dump (encoder, 'saved_encoder.joblib')
dump (persons, 'saved_persons.joblib')
