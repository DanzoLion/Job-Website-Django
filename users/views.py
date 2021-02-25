from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DetailView, ListView

from jobs.models import Category, Job
from .forms import AccountRegisterForm, UserUpdateForm, InviteEmployeeForm
from django.http import HttpResponseRedirect

# Create your views here.
from .models import Profile, Account, Invite  # Account: AbstractBaseUser; PermissionsMixin from .models


class UserRegisterView(SuccessMessageMixin, CreateView):
    template_name = 'users/user-register.html'
    form_class = AccountRegisterForm
    success_url = '/'
    success_message = "Your user account is active and created!"

    def form_valid(self, form):                                         # NB our logic is working on our forms data/variables defined in forms.py
        user = form.save(commit=False)
        user_type = form.cleaned_data['user_types']                     # user_types is derived from our forms.py variable user_types
        if user_type == 'is_employee':
            user.is_employee = True                                     # this object is obtained from models.py/Account.is_employee as True
        elif user_type == 'is_employer':
            user.is_employer = True

        user.save()                                                     # where we save our user at the end == (save=True)

        return redirect(self.success_url)

class UserLoginView(LoginView):                                         # this creates a user login view
    template_name = 'users/login.html'

class UserLogoutView(LogoutView):                                       # this creates a user login view
    template_name = 'users/login.html'


@method_decorator(login_required(login_url='/users/login'), name='dispatch')        # we user this method_decorator when we are using form.instance.user
class UserUpdateView(SuccessMessageMixin, UpdateView):
    model = Profile
    success_message = "You updated your profile!"
    template_name = 'users/update.html'                                 # we will need to create this html file in ./templates/users
    form_class = UserUpdateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UserUpdateView, self).form_valid(form)             # this saves our form, but we need to add a function below to firewall our users

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()                                 # this retrieves the profile
        if self.object.user != request.user:
            return HttpResponseRedirect('/')
        return super(UserUpdateView, self).get(request,*args,*kwargs)   # once we use update view, we need to use success url function

    def get_success_url(self):
        return reverse('users:update_profile', kwargs={'pk':self.object.pk})    # pk is referenced from urls.py


class EmployeeProfileView(CreateView):                                  # changed from DetailView to CreateView to suit newly created form in .users.forms.InviteEmployeeForm
    template_name = 'users/employee-profile.html'
    model = Account                                                     # we use this template format because we are inheriting DetailView into our class
    form_class = InviteEmployeeForm                                     # we can now add this once we import CreateView

    def get_context_data(self, **kwargs):
        context = super(EmployeeProfileView, self).get_context_data(**kwargs)
        context['account'] = Account.objects.get(pk=self.kwargs['employee_id'])         # where we change ['pk'] to ['employee_id']
        context['profile'] = Profile.objects.get(user_id=self.kwargs['employee_id'])    # where every users_profile in our database has user_id we can now connect between both contexts
        context['job'] = Job.objects.get(id=self.kwargs['job_id'])                      # job_id links with URL employee-profile
        context['categories'] = Category.objects.all()                                  # we will need to import Category and this is our employee profile data used in employee-profile
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = Account.objects.get(pk=self.kwargs['employee_id'])
        instance.job = Job.objects.get(pk=self.kwargs['job_id'])
        instance.save()
        return super (EmployeeProfileView, self).form_valid(form)           # because we use create view we also need to create a success URL message below

    def get_success_url(self):
        return reverse('users:employer_jobs')                               # referenced from .users.urls.urlpatterns[employee-jobs]


@method_decorator(login_required(login_url='/users/login'), name='dispatch')        # we user this method_decorator when we filter our jobs for EmployerPostedJobsView in get_queryset
class EmployerPostedJobsView(ListView):
    template_name = 'users/employer-posted-jobs.html'
    context_object_name = 'employer_jobs'
    model = Job
    paginate_by = 3

    def get_queryset(self):                                                     # because we use self.request.user we need to use the required decorator
        return Job.objects.filter(employer=self.request.user).order_by('-id')   # where attribute is imported from .models.Job.employer


@method_decorator(login_required(login_url='/users/login'), name='dispatch')    # we use self.request.user below so we need to use method decorator here
class EmployeeMessagesView(ListView):                                           # ListView because we are going to display jobs data
    model = Job
    template_name = 'users/employee-messages.html'
    paginate_by = 5
    context_object_name = 'jobs'

    def get_queryset(self):                                                                                             # where we filter jobs based on invitation only
        return Job.objects.filter(invites__isnull=False, invites__user_id=self.request.user).order_by('-invites')      # we select all jobs here and return only those with invitations for our user__id
                                                                                                                        # ('-invites') orders from last to first


class EmployeeDisplayMessages(DetailView):                                        # DetailView becausee we are to display message detail page
    model = Invite                                                                # Invite is where are messages are kept
    template_name = 'users/employee-display-messages.html'
    context_object_name = 'invite'

    def get_queryset(self):
        invite = self.model.objects.filter(id=self.kwargs['pk'])                  # where object is our messages we are going to filter // pk required as we are using id in url patterns
        invite.update(unread=False)                                               # invite is our message
        return invite

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user != request.user:
            return HttpResponseRedirect('/')
        return super(EmployeeDisplayMessages, self).get(request, *args, **kwargs)


@method_decorator(login_required(login_url='/users/login'), name='dispatch')        # we use method decorator here because we use object user=request.user below
class AddWishListView(UpdateView):                                                  # UpdateView used here because we are using many-to-many relationship
    template_name = 'jobs/index.html'
    model = Profile

    def get(self, request, *args, **kwargs):
        if self.request.user.is_employee:                                           # get only if request from employee
            job = Job.objects.get(id=self.kwargs['pk'])                             # Job.objects.get -> only retrieve a single job
            profile = Profile.objects.get(user=request.user)                        # Profile.objects.get -> retrieve only the single matching Profile of user/authenticated user
            profile.wish_list.add(job)                                              # adds job to profile.wish_list
            return redirect('jobs:home')                                            # however we use Ajax function so not necessary but required to complete the class

        else:
            return redirect('jobs:home')


@method_decorator(login_required(login_url='/users/login'), name='dispatch')        # we use method decorator here because we use object user=request.user below
class RemoveFromWishListView(UpdateView):                                           # UpdateView used here because we are using many-to-many relationship
    template_name = 'jobs/index.html'
    model = Profile

    def get(self, request, *args, **kwargs):
        if self.request.user.is_employee:                                           # get only if request from employee
            job = Job.objects.get(id=self.kwargs['pk'])                             # Job.objects.get -> only retrieve a single job
            profile = Profile.objects.get(user=request.user)                        # Profile.objects.get -> retrieve only the single matching Profile of user/authenticated user
            profile.wish_list.remove(job)                                           # removes job to profile.wish_list
            return redirect('jobs:home')                                            # however we use Ajax function so not necessary but required to complete the class

        else:
            return redirect('jobs:home')


class MyWishListView(ListView):
    template_name = 'users/my-wish-list.html'
    context_object_name = 'jobs'
    model = Job
    paginate_by = 5

    def get_queryset(self):
        return Job.objects.filter(wish_list__user_id = self.request.user.id)

    def get_context_data(self, **kwargs):                                               # we use this context function to add additional context data for our html files / where we use template tags to insert the context {{ tag }}
        context = super(MyWishListView, self).get_context_data(**kwargs)                # copied get_context_data from jobs.views.HomeView

        if self.request.user.is_authenticated:
            context['wish_list'] = Job.objects.filter(wish_list__user_id = self.request.user.id).values_list('id', flat=True)   # ['wishlist'] returns a list of our job_id and filters required id
        return context

