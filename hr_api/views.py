
from rest_framework import viewsets, filters
from .models import Employees
from .serializers import EmployeeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col
from django_pandas.io import read_frame
from pyspark.sql import SparkSession
from datetime import datetime
import pandas as pd
import numpy as np
import functools


class StandardResultsSetPagination(PageNumberPagination):
    """
    A pagination class that provides standard page size and pagination behavior.
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for performing CRUD operations on the Employees model and calculating average statistics.

    Attributes:
        queryset (QuerySet): Queryset representing all instances of the Employees model.
        serializer_class (Serializer): Serializer class to handle serialization for Employees model.
    """
    queryset = Employees.objects.all()
    serializer_class = EmployeeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]


    def create(self, request, *args, **kwargs):
        """
        Create a new employee instance.
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @functools.lru_cache(maxsize=3) 
    def get_spark_session(self):
        spark = SparkSession.builder.appName("DjangoDataToSpark").getOrCreate()
        return spark


    def calculate_average_age_per_industry(self, request):
        spark = self.get_spark_session()
        data  = Employees.objects.all().values()
        df = read_frame(data)

        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])

        # Calculate age based on current date
        current_date = datetime.now()
        df['age'] = (current_date - df['date_of_birth']) // pd.Timedelta(days=365.25)
        df.drop(columns=['date_of_birth'], inplace=True)

        spark = SparkSession.builder.appName("DjangoDataToSpark").getOrCreate()
        spark_df = spark.createDataFrame(df)
        result = spark_df.groupBy("industry").agg(avg(spark_df["age"]).alias("average_age")).collect()
        # spark.stop()
        return Response([row.asDict() for row in result])


    def calculate_average_salary_per_industry(self, request):
        result = {}

        data  = Employees.objects.all().values()
        df = read_frame(data)
        # spark = SparkSession.builder.appName("DjangoDataToSpark").getOrCreate()
        spark = self.get_spark_session()
        spark_df = spark.createDataFrame(df)

        # Calculate average salaries per industry
        avg_salary_per_industry = spark_df.groupBy("industry").agg({"salary": "avg"}).collect()
        for i in range(len(avg_salary_per_industry)):
            result[avg_salary_per_industry[i][0]] = avg_salary_per_industry[i][1]
        return Response(result)


    def get_average_salary_per_years_of_exp(self, request):
        data  = Employees.objects.all().values()
        df = read_frame(data)
        spark = self.get_spark_session()
        spark_df = spark.createDataFrame(df)

        spark_df = self.get_spark_dataframe()
        final_res = []
        # Calculate average salaries per years of experience
        avg_salary_per_experience = spark_df.groupBy("years_of_experience").\
                                    agg({"salary": "avg"}).collect()
        for i in range(len(avg_salary_per_experience)):
            result_data = {
                "years_of_experience" : avg_salary_per_experience[i][0],
                "avg_salary" : avg_salary_per_experience[i][1]
            }
            final_res.append(result_data)
        return Response({"average_salary_per_years_of_exp" : final_res})


    def get_other_interesting_stats(self, request):
        data  = Employees.objects.all().values()
        df = read_frame(data)
        spark = self.get_spark_session()
        spark_df = spark.createDataFrame(df)

        spark_df = self.get_spark_dataframe()

        gender_count = spark_df.groupBy("gender").count().collect()
        avg_salary_by_gender = spark_df.groupBy("gender").\
                                agg({"salary": "avg"}).collect()
        top_industries = spark_df.groupBy("industry").count().\
                                orderBy(col("count").desc()).limit(10).collect()
        
        gender_count_dict = {}
        for i in range(len(gender_count)):
            gender_count_dict[gender_count[i][0]] = gender_count[i][1]
        
        avg_salary_by_gender_dict = {}
        for i in range(len(avg_salary_by_gender)):
            avg_salary_by_gender_dict[avg_salary_by_gender[i][0]] = avg_salary_by_gender[i][1]
        
        top_industries_dict = {}
        for i in range(len(top_industries)):
            top_industries_dict[top_industries[i][0]] = top_industries[i][1]

        result = {
            "gender_count" : gender_count_dict,
            "avg_salary_by_gender" : avg_salary_by_gender_dict,
            "top_industries" : top_industries_dict
        }
        return Response(result)

