import django_filters
from jobs.models import Job

class JobFilter(django_filters.FilterSet):
    class Meta:
        model = Job
        fields = {
            'title' : ['iexact','icontains'],
            'budget' : ['iexact','lte','gte','range'],
            'status' : ['iexact','icontains'],
            'created_at' : ['date','day','month','year'],
        }