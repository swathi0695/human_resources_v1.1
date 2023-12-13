
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet


router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('average-age-per-industry/', 
        EmployeeViewSet.as_view({'get': 'calculate_average_age_per_industry'}), 
        name='average-age-per-industry'),

    path('average-salary-per-industry/', 
        EmployeeViewSet.as_view({'get': 'calculate_average_salary_per_industry'}), 
        name='average-salary-per-industry'),

    path('get_average_salary_per_years_of_exp/', 
        EmployeeViewSet.as_view({'get': 'get_average_salary_per_years_of_exp'}), 
        name='get_average_salary_per_years_of_exp'),

    path('get_other_interesting_stats/', 
        EmployeeViewSet.as_view({'get': 'get_other_interesting_stats'}),
        name='get_other_interesting_stats')
]
