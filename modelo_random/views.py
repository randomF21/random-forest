import os
import pandas as pd
import joblib
import re
from datetime import datetime  # Importar datetime
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import Counter
from django.db.models import Count, Q
from .models import Prediccion  # Asegúrate de importar el modelo Prediccion
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


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


class CargarCSVAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            # Obtener el archivo desde la solicitud
            file = request.FILES.get('file')
            if not file:
                return Response({'status': 'error', 'message': 'No se proporcionó ningún archivo'}, status=400)

            # Leer el CSV en un DataFrame
            df = pd.read_csv(file)
            
            # Normalizar los nombres de las columnas
            df.columns = df.columns.str.strip().str.upper().str.replace(' ', '_')

            # Validar columnas necesarias
            required_columns = ['EDAD', 'SEXO_BIOLOGICO', 'ESCOLARIDAD', 'ESTRATO_SOCIOECONOMICO']
            for col in required_columns:
                if col not in df.columns:
                    return Response({'status': 'error', 'message': f'Falta la columna {col}'}, status=400)

            # Procesar el DataFrame (similar a cómo lo hiciste para entrenar el modelo)
            df['EDAD'] = df['EDAD'].apply(procesar_edad)
            df = df.fillna('No describe')
            data_encoded = pd.get_dummies(df, drop_first=True)

            # Asegurar que todas las columnas del modelo estén presentes
            columns_used = modelo_completo['columns_used']
            for col in columns_used:
                if col not in data_encoded.columns:
                    data_encoded[col] = 0
            data_encoded = data_encoded[columns_used]

            # Generar predicciones
            modelo = modelo_completo['model']
            predictions = modelo.predict(data_encoded)
            probabilities = modelo.predict_proba(data_encoded)

            # Mapear predicciones a texto
            pred_mapping = {0: "No Suicidio", 1: "Suicidio"}
            df['Prediccion'] = [pred_mapping[pred] for pred in predictions]
            df['Probabilidad_Clase_1'] = probabilities[:, 1]
            
             # Guardar predicciones en la base de datos
            for _, row in df.iterrows():
                Prediccion.objects.create(
                    edad=row['EDAD'],
                    sexo_biologico=row['SEXO_BIOLOGICO'],
                    escolaridad=row['ESCOLARIDAD'],
                    estrato_socioeconomico=row['ESTRATO_SOCIOECONOMICO'],
                    prediccion=row['Prediccion'],
                    probabilidad_clase_1=row['Probabilidad_Clase_1'],
                    fecha=datetime.now()
                )

            # Responder con las predicciones
            return Response({
                'status': 'success',
                'predicciones': df.to_dict(orient='records')
            })

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=500)
        
 


class ConsultarPrediccionesGuardadasAPIView(APIView):
    def get(self, request):
        try:
            # Obtener el parámetro de fecha desde la solicitud
            fecha = request.query_params.get('fecha', None)

            if fecha:
                try:
                    fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
                except ValueError:
                    return Response({
                        'status': 'error',
                        'message': 'El formato de fecha debe ser YYYY-MM-DD'
                    }, status=400)
                
                predicciones = Prediccion.objects.filter(fecha__date=fecha_datetime)
            else:
                predicciones = Prediccion.objects.filter(es_entrenamiento=True)

            # Validar si existen predicciones
            if not predicciones.exists():
                return Response({
                    'status': 'error',
                    'message': 'No se encontraron predicciones para la fecha seleccionada o de entrenamiento.'
                }, status=404)

            # Convertir las predicciones a DataFrame para procesamiento
            predicciones_list = list(predicciones.values(
                'edad',
                'sexo_biologico',
                'escolaridad',
                'estrato_socioeconomico',
                'prediccion',
                'probabilidad_clase_1'
            ))
            df = pd.DataFrame(predicciones_list)

            # Validar columnas requeridas
            required_columns = ['edad', 'sexo_biologico', 'escolaridad', 'estrato_socioeconomico', 'prediccion']
            for col in required_columns:
                if col not in df.columns or df[col].isnull().all():
                    return Response({
                        'status': 'error',
                        'message': f'La columna {col} no tiene datos válidos.'
                    }, status=400)

            # Procesar edad
            df['edad'] = df['edad'].apply(procesar_edad)

            # Procesar género
            totales_genero = df['sexo_biologico'].apply(extraer_totales_genero)
            df = pd.concat([df, totales_genero], axis=1)

            # Calcular tasa de suicidio por género
            suicidio_mask = df['prediccion'] == 'Suicidio'
            
            suicidio_hombres = df[suicidio_mask]['Masculino'].sum()
            total_hombres = df['Masculino'].sum()
            
            suicidio_mujeres = df[suicidio_mask]['Femenino'].sum()
            total_mujeres = df['Femenino'].sum()

            tasa_suicidio_genero = {
                'Hombres': suicidio_hombres / total_hombres if total_hombres > 0 else 0,
                'Mujeres': suicidio_mujeres / total_mujeres if total_mujeres > 0 else 0
            }

            # Procesar estrato socioeconómico
            estrato_totales = Counter()
            df['estrato_socioeconomico'].apply(lambda x: estrato_totales.update(procesar_estrato_socieconomico(x)))

            # Calcular estadísticas para gráficos
            stats = {
                'genero': {
                    'Femenino': int(total_mujeres),
                    'Masculino': int(total_hombres)
                },
                'prediccion': dict(df['prediccion'].value_counts()),
                'estrato': dict(estrato_totales),
                'escolaridad': dict(df['escolaridad'].value_counts()),
                'tasa_suicidio_genero': tasa_suicidio_genero
            }

            # Obtener las fechas únicas de las predicciones
            fechas_disponibles = Prediccion.objects.dates('fecha', 'day').distinct()

            return Response({
                'status': 'success',
                'stats': stats,
                'fechas_disponibles': [fecha.strftime('%Y-%m-%d') for fecha in fechas_disponibles],
                'data': df.to_dict(orient='records')  # Incluir datos procesados si son necesarios
            })

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'type': str(type(e))
            }, status=500)



class FechasPrediccionesAPIView(APIView):
    def get(self, request):
        try:
            # Obtener solo las fechas únicas de las predicciones
            fechas_disponibles = Prediccion.objects.dates('fecha', 'day').distinct()
            
            return Response({
                'status': 'success',
                'fechas_disponibles': [fecha.strftime('%Y-%m-%d') for fecha in fechas_disponibles]
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
def procesar_edades(edad):
    try:
        edad = int(edad)
        if edad <= 10:
            return '0 - 10 años'
        elif edad <= 20:
            return '11 - 20 años'
        elif edad <= 30:
            return '21 - 30 años'
        elif edad <= 40:
            return '31 - 40 años'
        else:
            return '>40 años'
    except ValueError:
        return 'Sin dato'  # Manejar valores no numéricos

    
class RealizarPrediccionAPIView(APIView):
    def post(self, request):
        try:
            # Obtener los datos del formulario
            datos = request.data

            # Validar campos obligatorios
            required_fields = ['edad', 'sexo_biologico', 'escolaridad', 'estrato_socioeconomico']
            for field in required_fields:
                if field not in datos:
                    return Response({'error': f'El campo {field} es obligatorio.'}, status=400)

            # Mapeo de valores para las columnas categóricas
            mapeo_edad = {
                (0, 10): 'EDAD_0 - 10 años',
                (11, 20): 'EDAD_11 - 20 años',
                (21, 30): 'EDAD_21 - 30 años',
                (31, 40): 'EDAD_31 - 40 años',
                (41, 150): 'EDAD_>40 años'
            }
            def mapear_edad(edad):
                for rango, categoria in mapeo_edad.items():
                    if rango[0] <= edad <= rango[1]:
                        return categoria
                return 'EDAD_Desconocida'

            mapeo_sexo = {'Masculino': 'SEXO_BIOLOGICO_Masculino', 'Femenino': 'SEXO_BIOLOGICO_Femenino'}
            mapeo_escolaridad = {
                'Primaria': 'ESCOLARIDAD_Primaria',
                'Secundaria': 'ESCOLARIDAD_Secundaria',
                'Universitario': 'ESCOLARIDAD_Universitario'
            }
            mapeo_estrato = {
                'Bajo': 'ESTRATO_SOCIOECONOMICO_Bajo',
                'Medio': 'ESTRATO_SOCIOECONOMICO_Medio',
                'Alto': 'ESTRATO_SOCIOECONOMICO_Alto'
            }

            # Crear el DataFrame
            df = pd.DataFrame([datos])
        

            # Mapear valores a nombres de columnas del modelo
            df['EDAD'] = df['edad'].astype(int).apply(mapear_edad)
            df['SEXO_BIOLOGICO'] = df['sexo_biologico'].map(mapeo_sexo)
            df['ESCOLARIDAD'] = df['escolaridad'].map(mapeo_escolaridad)
            df['ESTRATO_SOCIOECONOMICO'] = df['estrato_socioeconomico'].map(mapeo_estrato)
            

            # Crear un DataFrame con las columnas esperadas por el modelo
            columnas_usadas = modelo_completo['columns_used']
            df_final = pd.DataFrame(0, index=[0], columns=columnas_usadas)

            # Rellenar las columnas correspondientes
            for col in ['EDAD', 'SEXO_BIOLOGICO', 'ESCOLARIDAD', 'ESTRATO_SOCIOECONOMICO']:
                if df[col][0] in columnas_usadas:
                    df_final.loc[0, df[col][0]] = 1

            

            # Realizar la predicción
            modelo = modelo_completo['model']
            prediccion = modelo.predict(df_final)[0]
            probabilidad = modelo.predict_proba(df_final)[0][1]
            

            # Responder con el resultado
            resultado = {
                'prediccion': "Suicidio" if prediccion == 1 else "No Suicidio",
                'probabilidad': probabilidad,
            }
            return Response(resultado, status=200)

        except KeyError as e:
            return Response({'error': f"Columna faltante: {str(e)}"}, status=500)
        except ValueError as e:
            return Response({'error': f"Error en los datos: {str(e)}"}, status=500)
        except Exception as e:
            return Response({'error': f"Error inesperado: {str(e)}"}, status=500)


from django.http import HttpResponse
import pandas as pd

class DescargarPrediccionesExcelAPIView(APIView):
    def get(self, request):
        try:
            # Obtener el parámetro de fecha
            fecha = request.query_params.get('fecha', None)

            if fecha:
                try:
                    fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
                except ValueError:
                    return Response({
                        'status': 'error',
                        'message': 'El formato de fecha debe ser YYYY-MM-DD'
                    }, status=400)
                
                predicciones = Prediccion.objects.filter(fecha__date=fecha_datetime)
            else:
                return Response({
                    'status': 'error',
                    'message': 'La fecha es requerida para generar el archivo.'
                }, status=400)

            # Validar si existen predicciones
            if not predicciones.exists():
                return Response({
                    'status': 'error',
                    'message': 'No se encontraron predicciones para la fecha seleccionada.'
                }, status=404)

            # Convertir las predicciones a DataFrame
            predicciones_list = list(predicciones.values(
                'edad',
                'sexo_biologico',
                'escolaridad',
                'estrato_socioeconomico',
                'prediccion',
                'probabilidad_clase_1'
            ))
            df = pd.DataFrame(predicciones_list)

            # Crear archivo Excel
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=predicciones_{fecha}.xlsx'
            df.to_excel(response, index=False)

            return response
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)


from reportlab.pdfgen import canvas

class DescargarPrediccionesPDFAPIView(APIView):
    def get(self, request):
        try:
            # Obtener el parámetro de fecha
            fecha = request.query_params.get('fecha', None)

            if fecha:
                try:
                    fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
                except ValueError:
                    return Response({
                        'status': 'error',
                        'message': 'El formato de fecha debe ser YYYY-MM-DD'
                    }, status=400)
                
                predicciones = Prediccion.objects.filter(fecha__date=fecha_datetime)
            else:
                return Response({
                    'status': 'error',
                    'message': 'La fecha es requerida para generar el archivo.'
                }, status=400)

            # Validar si existen predicciones
            if not predicciones.exists():
                return Response({
                    'status': 'error',
                    'message': 'No se encontraron predicciones para la fecha seleccionada.'
                }, status=404)

            # Crear archivo PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename=predicciones_{fecha}.pdf'

            # Crear el documento PDF
            doc = SimpleDocTemplate(response, pagesize=letter)
            elements = []

            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=20,
                alignment=1  # Centrado
            )
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.white,
                alignment=1
            )
            cell_style = ParagraphStyle(
                'Cell',
                parent=styles['Normal'],
                fontSize=10,
                alignment=1
            )

            # Título del PDF
            title = Paragraph(f"Predicciones para la fecha: {fecha}", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))  # Espacio después del título

            # Datos de la tabla
            data = [
                ["Edad", "Sexo", "Predicción", "Probabilidad (Clase 1)"]
            ]

            for prediccion in predicciones:
                row = [
                    prediccion.edad,
                    prediccion.sexo_biologico,
                    prediccion.prediccion,
                    f"{prediccion.probabilidad_clase_1:.4f}"
                ]
                data.append(row)

            # Crear la tabla
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # Fondo del encabezado
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Color del texto del encabezado
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinear todo al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente del encabezado
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Espaciado inferior del encabezado
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Fondo de las filas
                ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Líneas de la tabla
            ]))

            elements.append(table)

            # Construir el PDF
            doc.build(elements)

            return response
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

















