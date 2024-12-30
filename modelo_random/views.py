import os
import pandas as pd
import joblib
from rest_framework.views import APIView
from rest_framework.response import Response

# Cargar el modelo completo al inicio
modelo_path = os.path.join(os.path.dirname(__file__), 'models', 'random_forest_model_final.joblib')
modelo_completo = joblib.load(modelo_path)

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

