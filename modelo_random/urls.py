from django.urls import path
from .views import FeatureImportanceAPIView, ModelStatisticsAPIView
from .views import GeneratePredictionsAPIView
from .views import CargarCSVAPIView
from .views import ConsultarPrediccionesGuardadasAPIView
from .views import FechasPrediccionesAPIView
from .views import RealizarPrediccionAPIView
from .views import DescargarPrediccionesExcelAPIView
from .views import DescargarPrediccionesPDFAPIView

urlpatterns = [
    path('feature-importance/', FeatureImportanceAPIView.as_view(), name='feature_importance'),
    path('model-statistics/', ModelStatisticsAPIView.as_view(), name='model_statistics'),
    path('generate-predictions/', GeneratePredictionsAPIView.as_view(), name='generate-predictions'),
    path('cargar-csv/', CargarCSVAPIView.as_view(), name='cargar_csv'),
    path('cargar-predicciones/', ConsultarPrediccionesGuardadasAPIView.as_view(), name='cargar_predicciones'),
    path('fechas-predicciones/', FechasPrediccionesAPIView.as_view(), name = 'fechas_predicciones'),
    path('realizar-prediccion', RealizarPrediccionAPIView.as_view(), name='realiza_prediccion'),
    path('descargar-predicciones-excel', DescargarPrediccionesExcelAPIView.as_view(), name='descargar_excel'),
    path('descargar-predicciones-pdf', DescargarPrediccionesPDFAPIView.as_view(), name='descargar_pdf')
]
