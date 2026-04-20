import django_filters
from jobs.models import Job

class JobFilter(django_filters.FilterSet):

    min_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="gte")
    max_budget = django_filters.NumberFilter(field_name="budget", lookup_expr="lte")

    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = Job
        fields = ["status"]