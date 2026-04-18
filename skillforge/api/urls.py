from django.urls import path,include

urlpatterns = [
    path("contracts/",include("api.contracts.urls")),
    path("jobs/",include("api.jobs.urls")),
    path("auth/",include("api.auth.urls"))

]