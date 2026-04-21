from django.urls import path,include

urlpatterns = [
    path("auth/",include("api.auth.urls")),
    path("contracts/",include("api.contracts.urls")),
    path("jobs/",include("api.jobs.urls")),
    path("bids/",include("api.bids.urls")),

]