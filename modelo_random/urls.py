from django.urls import path
from .views import FeatureImportanceAPIView, ModelStatisticsAPIView
from .views import GeneratePredictionsAPIView

urlpatterns = [
    path('feature-importance/', FeatureImportanceAPIView.as_view(), name='feature_importance'),
    path('model-statistics/', ModelStatisticsAPIView.as_view(), name='model_statistics'),
    path('generate-predictions/', GeneratePredictionsAPIView.as_view(), name='generate-predictions'),
]
