import os
from flood_predictor import get_flood_predictor
from tensorflow.keras.models import load_model

print('MODEL_PATH exists:', os.path.exists('models/AlexNet_best.h5'))
print('FLOOD_MODEL exists:', os.path.exists('models/flood_model.pkl'))

f = get_flood_predictor()
print('flood_predictor type:', type(f) if f else 'None')

try:
    load_model('models/AlexNet_best.h5')
    print('cloudburst loaded OK')
except Exception as e:
    print('cloudburst load error', e)
