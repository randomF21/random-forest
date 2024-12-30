import pandas as pd
from sklearn.model_selection import train_test_split


control_df = pd.read_csv('modelo_random/dataset/control1df.csv')  
caso_df = pd.read_csv('modelo_random/dataset/casodf.csv')  

# Asignar categorías
control_df['CATEGORIA'] = 0  # Control
caso_df['CATEGORIA'] = 1  # Caso

# Combinar control y caso en un solo dataframe
data = pd.concat([control_df, caso_df], ignore_index=True)

# Separar características (X) y etiquetas (y)
X = data.drop('CATEGORIA', axis=1)  # Eliminar la columna objetivo
y = data['CATEGORIA']  # Variable objetivo

# Dividir los datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Crear carpeta si no existe
import os
output_dir = 'modelo_random/data'
os.makedirs(output_dir, exist_ok=True)

# Guardar los datos de prueba en CSV
X_test.to_csv(os.path.join(output_dir, 'X_test.csv'), index=False)  # Características de prueba
y_test.to_csv(os.path.join(output_dir, 'y_test.csv'), index=False)  # Etiquetas de prueba

print("Archivos X_test.csv e y_test.csv generados exitosamente en la carpeta Api/data/")
