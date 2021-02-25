from django.urls import path
from .views import *
from django.contrib.auth import views as authViews

app_name = 'users'                                                                                                      # our url will look like: localhost:8000/users/register

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('password-change/', authViews.PasswordChangeView.as_view(), name='password_change'),                           # we add our url after we create the reference from html in base.html
    path('password-change-done/', authViews.PasswordChangeDoneView.as_view(), name='password_change_done'),


    path('update-profile/<int:pk>/', UserUpdateView.as_view(), name='update_profile'),                                  # NB becuase we are updating, we need to reference the item via its existing pk
    path('employee-profile/<int:employee_id>/<int:job_id>', EmployeeProfileView.as_view(), name='employee_profile'),    # where we have just created class EmployeeProfileView in .views
                                                                                                                        # changed employee-profile <int:id> to <int:employee_id> & <int:job_id>
    path('employer-jobs/', EmployerPostedJobsView.as_view(), name='employer_jobs'),                                     # where we have just created class EmployeeProfileView in .views
    path('employee-messages/<int:pk>/', EmployeeMessagesView.as_view(), name='employee_messages'),                      # where we have just created class EmployeeMessagesView in .views added pk
    path('employee-display-messages/<int:pk>/', EmployeeDisplayMessages.as_view(), name='employee_display_messages'),   # where we have just created class EmployeeDisplayMessages in .views added pk
    path('add-wishlist/<int:pk>/', AddWishListView.as_view(), name='add_wishlist'),                                     # urls inserted after creating Ajax functions for index.html wishlist buttons
    path('remove-from-wishlist/<int:pk>/', RemoveFromWishListView.as_view(), name='remove_from_wishlist'),              # urls inserted after creating Ajax functions for index.html wishlist buttons
    path('mywishlist/<int:pk>/', MyWishListView.as_view(), name='my_wish_list'),                                        # urls inserted after creating Ajax functions for index.html wishlist buttons
]


