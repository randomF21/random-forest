import os
import pandas as pd
import joblib
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import Counter


# Cargar el modelo completo al inicio
modelo_path = os.path.join(os.path.dirname(__file__), 'models', 'random_forest_model_final.joblib')
modelo_completo = joblib.load(modelo_path)

# Ruta a la carpeta "dataset" dentro del proyecto
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset')

# Archivos CSV específicos
CONTROL_FILE = os.path.join(DATA_PATH, 'control1df.csv')
CASO_FILE = os.path.join(DATA_PATH, 'casodf.csv')

class FeatureImportanceAPIView(APIView):
    def get(self, request):
        # Obtener las importancias de las características
        feature_importances = pd.DataFrame({
            'Feature': modelo_completo['columns_used'],
            'Importance': modelo_completo['model'].feature_importances_
        }).sort_values(by='Importance', ascending=False)

        return Response(feature_importances.to_dict(orient='records'))

# Simula cargar la matriz de confusión
conf_matrix = modelo_completo['confusion_matrix']
categories = ['False', 'True']

# Mapear la matriz
mapped_conf_matrix = pd.DataFrame(
    conf_matrix,
    index=[f'Actual {cat}' for cat in categories],
    columns=[f'Predicted {cat}' for cat in categories]
)

class ModelStatisticsAPIView(APIView):
    def get(self, request):
        try:
            # Extraer el modelo y las métricas
            modelo = modelo_completo['model']
            conf_matrix = modelo_completo['confusion_matrix']
            roc_curve_data = modelo_completo.get('roc_curve', None)

            # Etiquetas de categorías
            categories = ['False', 'True']

            # Mapear la matriz de confusión a un DataFrame con etiquetas
            mapped_conf_matrix = pd.DataFrame(
                conf_matrix,
                index=[f'Actual {cat}' for cat in categories],  # Etiquetas de filas
                columns=[f'Predicted {cat}' for cat in categories]  # Etiquetas de columnas
            )

           # Retornar las métricas incluyendo la curva ROC si está disponible
            response_data = {
                'status': 'success',
                'confusion_matrix': mapped_conf_matrix.to_dict(orient='split'),
                'classification_report': modelo_completo['classification_report'],
            }

            if roc_curve_data:
                response_data['roc_curve'] = roc_curve_data

            return Response(response_data)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'type': str(type(e))
            }, status=500)


# Función para procesar la columna EDAD
def procesar_edad(valor):
    import re

    # Asegurarse de que el valor sea una cadena
    if not isinstance(valor, str):
        return 'Sin dato'

    # Dividir el texto en líneas y procesar cada línea
    for linea in valor.split('\n'):
        # Buscar rango de edades en la línea
        match = re.search(r'\d+\s*-\s*\d+\s*años', linea)
        if match:
            return match.group(0)

        # Buscar una sola edad en la línea
        match = re.search(r'\d+\s*años', linea)
        if match:
            print(f"Edad única encontrada: {match.group(0)}")
            return match.group(0)

    return 'Sin dato'


# Función para extraer totales de género (Femenino/Masculino) de la columna SEXO_BIOLOGICO
def extraer_totales_genero(sexo_biologico):
    femenino = 0
    masculino = 0
    # Buscar patrones "Femenino X" o "Masculino X"
    matches = re.findall(r"(Femenino|Masculino)\s(\d+)", sexo_biologico)
    for genero, cantidad in matches:
        if genero == "Femenino":
            femenino += int(cantidad)
        elif genero == "Masculino":
            masculino += int(cantidad)
    return pd.Series({"Femenino": femenino, "Masculino": masculino})

def procesar_estrato_socieconomico(estrato):
    """
    Procesa una cadena de estrato socioeconómico y extrae los totales para Bajo, Medio y Alto.
    """
    estrato_totales = {'Bajo': 0, 'Medio': 0, 'Alto': 0}
    if pd.notnull(estrato):
        matches = re.findall(r"(Bajo|Medio|Alto)\s+(\d+)", estrato)
        for match in matches:
            categoria, valor = match
            estrato_totales[categoria] += int(valor)
    return estrato_totales




class GeneratePredictionsAPIView(APIView):
    def get(self, request):
        try:
            modelo = modelo_completo['model']
            columns_used = modelo_completo['columns_used']

            # Validar la existencia de los archivos
            if not os.path.exists(CONTROL_FILE) or not os.path.exists(CASO_FILE):
                return Response({'status': 'error', 'message': 'Archivos CSV no encontrados'}, status=404)

            # Cargar los datos
            control_df = pd.read_csv(CONTROL_FILE)
            caso_df = pd.read_csv(CASO_FILE)

            # Limpiar nombres de columnas
            control_df.columns = control_df.columns.str.strip().str.upper().str.replace(' ', '_')
            caso_df.columns = caso_df.columns.str.strip().str.upper().str.replace(' ', '_')

            # Agregar columna de target y concatenar
            control_df['CATEGORIA'] = 0
            caso_df['CATEGORIA'] = 1
            data = pd.concat([control_df, caso_df], ignore_index=True)

            # Verificar columnas necesarias
            required_columns = ['EDAD', 'SEXO_BIOLOGICO', 'ESCOLARIDAD', 'ESTRATO_SOCIOECONOMICO']
            for col in required_columns:
                if col not in data.columns:
                    data[col] = 'No describe'  # Agregar columna faltante con valor predeterminado

            # Guardar columnas originales necesarias para la respuesta
            original_columns = data[required_columns].copy()

            # Procesar columna EDAD
            if 'EDAD' in data.columns:
                data['EDAD'] = data['EDAD'].apply(procesar_edad)
                
             # Procesar estrato socioeconómico
            estrato_totales = Counter()
            data['ESTRATO_SOCIOECONOMICO'].apply(lambda x: estrato_totales.update(procesar_estrato_socieconomico(x)))

            # Rellenar valores nulos
            data = data.fillna('No describe')

            # Codificar variables categóricas
            data_encoded = pd.get_dummies(data, drop_first=True)

            # Asegurar que todas las columnas del modelo estén presentes
            for col in columns_used:
                if col not in data_encoded.columns:
                    data_encoded[col] = 0
            data_encoded = data_encoded[columns_used]  # Ordenar las columnas

            # Generar predicciones
            predictions = modelo.predict(data_encoded)
            probabilities = modelo.predict_proba(data_encoded)

            # Mapear predicciones a texto
            pred_mapping = {0: "No Suicidio", 1: "Suicidio"}
            mapped_predictions = [pred_mapping[pred] for pred in predictions]

            # Agregar resultados al DataFrame original
            original_columns['EDAD'] = data['EDAD']  # Actualizar con EDAD procesada
            original_columns['Prediccion'] = mapped_predictions
            original_columns['Probabilidad_Clase_1'] = probabilities[:, 1]

            # Extraer totales de género
            totales_genero = original_columns['SEXO_BIOLOGICO'].apply(extraer_totales_genero)
            original_columns = pd.concat([original_columns, totales_genero], axis=1)
            
            # Calcular tasa de suicidio por género
            suicidio_hombres = original_columns[(original_columns['Prediccion'] == "Suicidio") & (original_columns['Masculino'] > 0)]['Masculino'].sum()
            total_hombres = original_columns['Masculino'].sum()
            
            suicidio_mujeres = original_columns[(original_columns['Prediccion'] == "Suicidio") & (original_columns['Femenino'] > 0)]['Femenino'].sum()
            total_mujeres = original_columns['Femenino'].sum()

            tasa_suicidio_genero = {
                'Hombres': suicidio_hombres / total_hombres if total_hombres > 0 else 0,
                'Mujeres': suicidio_mujeres / total_mujeres if total_mujeres > 0 else 0
            }

            # Reemplazar valores NaN o infinitos
            original_columns = original_columns.replace([float('inf'), float('-inf'), float('nan')], 0).fillna('No describe')

            # Generar estadísticas para gráficos
            stats = {
                'genero': {
                    'Femenino': totales_genero['Femenino'].sum(),
                    'Masculino': totales_genero['Masculino'].sum()
                },
                'prediccion': dict(Counter(mapped_predictions)),
                'escolaridad': dict(Counter(original_columns['ESCOLARIDAD'])),
                'estrato': dict(estrato_totales),  # Agregar datos procesados
                'tasa_suicidio_genero': tasa_suicidio_genero
            }

            # Responder con las predicciones
            return Response({
                'status': 'success',
                'predictions': original_columns.to_dict(orient='records'),
                'stats': stats
            })

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'type': str(type(e))
            }, status=500)



