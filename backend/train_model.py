import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models

# -----------------------------
# DATASET PATHS
# -----------------------------
train_dir = r"C:\Users\allam\Downloads\archive (1)\chest_xray\train"
test_dir = r"C:\Users\allam\Downloads\archive (1)\chest_xray\test"

# -----------------------------
# IMAGE PREPROCESSING
# -----------------------------
train_datagen = ImageDataGenerator(rescale=1./255)

test_datagen = ImageDataGenerator(rescale=1./255)

train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(150,150),
    batch_size=32,
    class_mode='binary'
)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(150,150),
    batch_size=32,
    class_mode='binary'
)

# -----------------------------
# CNN MODEL
# -----------------------------
model = models.Sequential()

model.add(layers.Conv2D(32, (3,3), activation='relu', input_shape=(150,150,3)))
model.add(layers.MaxPooling2D(2,2))

model.add(layers.Conv2D(64, (3,3), activation='relu'))
model.add(layers.MaxPooling2D(2,2))

model.add(layers.Conv2D(128, (3,3), activation='relu'))
model.add(layers.MaxPooling2D(2,2))

model.add(layers.Flatten())

model.add(layers.Dense(128, activation='relu'))

model.add(layers.Dense(1, activation='sigmoid'))

# -----------------------------
# COMPILE MODEL
# -----------------------------
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# -----------------------------
# TRAIN MODEL
# -----------------------------
model.fit(
    train_data,
    validation_data=test_data,
    epochs=5
)

# -----------------------------
# SAVE MODEL
# -----------------------------
model.save("pneumonia_model.h5")

print("✅ Model trained and saved!")