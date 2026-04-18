from api.jobs.permissions import JobAccessPermission
from rest_framework import generics,status
from jobs.models import Job
from api.jobs.serializers import JobSerializer,JobUpdateSerializer
from rest_framework.permissions import AllowAny
from api.jobs.filters import JobFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from jobs.services import * 

class JobListAPIView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filterset_class = JobFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['budget','status']
    ordering_fields = ['budget']

class JobDetailAPIView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_url_kwarg = 'job_id'
    permission_classes = [JobAccessPermission(),]


# Jobs created by me
class JobAsClientAPIView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filterset_class = JobFilter
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['budget','status']
    ordering_fields = ['budget']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(client=self.request.user)

class JobCreateAPIView(generics.CreateAPIView):
    serializer_class = JobSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data['title']
        description = serializer.validated_data['description']
        budget = serializer.validated_data['budget']
        user = request.user

        job = create_job(title,description,user,budget)

        return Response({
            "message" : "Job Created",
            "job_id" : job.id,
            "status" : job.status
        },status.HTTP_201_CREATED)

class JobUpdateAPIView(generics.UpdateAPIView):
    serializer = JobUpdateSerializer

    def update(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job_id = serializer.validated_data['job_id']
        job = Job.objects.get(job_id)
        user = request.user

        updated_job = update_job(user,job,title,description,budget)

        return Response({
            "message" : "Job Updated",
            "job_id" : updated_job.id,
            "status" : updated_job.status
        })


class JobCancelAPIView(generics.DestroyAPIView):

    def destroy(self,request,*args,**kwargs):
        job = self.get_object()
        user = request.user

        cancel_job(user,job)

        return Response({
            "message": "Job Cancelled",
            "job_id" : job.id,
            "job_status" : job.status
        })

    

