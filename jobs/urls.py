from django.urls import path
from .views import *


app_name = 'jobs'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('create-job/', CreateJobView.as_view(), name="create_job"),                            # path = url create-job/ # taken from .views.CreateJobView # create_job used in our html references
    path('search/', SearchJobView.as_view(), name="search"),                                    # path = url search/ # taken from .views.SearchJobView # create_job used in our html references
    path('detail/<slug>/<int:pk>', SingleJobView.as_view(), name="single_job"),                 # SingleJobView from views.py -> 'detail' our html template reference 'url:single_job'
    path('update/<slug>/<int:pk>', UpdateJobView.as_view(), name="update_job"),                 # SingleJobView from views.py -> 'detail' our html template reference 'url:single_job'
    path('delete/<slug>/<int:pk>', DeleteJobView.as_view(), name="delete_job"),                 # SingleJobView from views.py -> 'detail' our html template reference 'url:single_job'
    path('category-detail/<slug>/<int:pk>', CategoryDetailView.as_view(), name="category_detail"),  # CategoryDetailView from jobs.views -> 'category' our html template reference 'url:category_detail'
]