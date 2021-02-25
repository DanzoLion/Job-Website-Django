from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, DeleteView

from users.models import Account, Profile
from .models import Job, Category
from .forms import *

from django.core.mail import send_mail


class HomeView(ListView):                                           # within index.html we are only using this singe generic view currently / 'jobs'
    template_name = 'jobs/index.html'  # our tags are a key/value pair used for defining our context data
    context_object_name = 'jobs'
    model = Job
    paginate_by = 3                                                 # we can adjust the size of our pagination depending on number of jobs

    def get_context_data(self, **kwargs):                                               # we use this context function to add additional context data for our html files / where we use template tags to insert the context {{ tag }}
        context = super(HomeView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()                                  # this will retrieve all our categories from our database
        context['all_jobs'] = Job.objects.all().count()                                 # to count our jobs for accurate statistical display
        context['candidates'] = Account.objects.filter(is_employee=True).count() * 101  # to count employees for accurate statistical display
        context['resumes'] = Profile.objects.exclude(resume="").count() * 15            # counts the users_profile resume field in our database
        context['employers'] = Account.objects.filter(is_employer=True).count() * 101  # to count employees for accurate statistical display
        if self.request.user.is_authenticated:
            context['wish_list'] = Job.objects.filter(wish_list__user_id = self.request.user.id).values_list('id', flat=True)   # ['wishlist'] returns a list of our job_id and filters required id
        return context



@method_decorator(login_required(login_url='/'), name='dispatch')   # checks the user is logged in, redirecting to the log-in page if necessary.
class CreateJobView(SuccessMessageMixin, CreateView):               # CreateView - where we create a new job
    model = Job
    template_name = 'jobs/create-jobs.html'
    form_class = CreateJobForm
    success_url = '/'                                               # '/' = homepage
    success_message = 'Your job is now posted'

    def form_valid(self, form):
        job = form.save(commit=False)                               # commit=False because our job doesn't have an employer
        job.employer = self.request.user                            # with self.request.user we need to add an additional method decorator to hand this variable
        job.save()                                                  # because job now has an employer
        return super(CreateJobView, self).form_valid(form)


class SingleJobView(SuccessMessageMixin, UpdateView):               # changed to UpdateView once our Apply Job Button has been created / removed DetailView // added SuccessMessageMixin
    template_name = 'jobs/single.html'
    model = Job
    context_object_name = 'job'
    form_class = ApplyJobForm                                       # we are now able to ApplyJobForm
    success_message = 'Great, you have now applied for this job!'   # we can also apply our success message

    def get_context_data(self, **kwargs):                                                                                       # we use this context function to add additional context data for our html files / where we use template tags to insert the context {{ tag }}
        context = super(SingleJobView, self).get_context_data(**kwargs)                                                         # Amend to take in arguments from SingleJobView
        context['categories'] = Category.objects.all()                                                                          # this will retrieve all our categories from our database
        context['employee_applied']=Job.objects.get(pk=self.kwargs['pk']).employee.all().filter(id=self.request.user.id)        # where get refers to a single job and we specify which job via its pk / where employee.all() references one job to many employees field
        context['in_my_list']=Job.objects.get(pk=self.kwargs['pk']).wish_list.all().filter(user_id=self.request.user.id)             # where pk is the id of our job we are retrieving
        try:                                                                                                                    # try for employer_id if not pass

            context['applied_employees'] = Job.objects.get(pk=self.kwargs['pk'], employer_id=self.request.user.id).employee.all()
            context['employer_id'] = Job.objects.get(pk=self.kwargs['pk']).employer_id                                           # where we have a field employer_id in our database table
        except:
            pass
        return context                                                                                                          # where request.user.id == user id then employee already applied the job

    def form_valid(self, form):                                                 # this will validate that we are an employee 100% and not an employer
        employee = self.request.user
        form.instance.employee.add(employee)
        form.save()
        return super(SingleJobView, self).form_valid(form)

    def get_success_url(self):                                                  # jobs:single_job references .urls path detail, name=single_job
        return reverse('jobs:single_job',
                       kwargs={'slug':self.object.slug,                         # slug & pk taken from .urls path detail, slug & pk
                               "pk":self.object.pk})


class CategoryDetailView(ListView):                                             # ListView so that we can list our jobs // it is a MultipleObjectTemplateResultMixin
    model = Job
    template_name = 'jobs/category-detail.html'                                 # create relative category-detail.html
    context_object_name = 'jobs'
    paginate_by = 2

    def get_queryset(self):                                                     # so that we create our detail view page
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])       # the pk is used and referenced in our URL
        return Job.objects.filter(category=self.category)                       # where we filter our jobs by Category / found in .models.jobs // category filtered will be the above selected

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])               # the pk is used and referenced in our URL
        context['categories'] = Category.objects.all()
        context['category'] = self.category                                             # added and we can use this category context in our index.html file
        return context


class SearchJobView(ListView):                                                          # we use ListView because we are going to list our jobs - the job results
    model = Job
    template_name = 'jobs/search.html'                                                  # we need to create this html file
    paginate_by = 2
    context_object_name = 'jobs'

    def get_queryset(self):                                                             # where we retrieve the name attribues from html file to return our results
        q1 = self.request.GET.get("job_title")                                          # q1 == our search query
        q2 = self.request.GET.get("job_type")
        q3 = self.request.GET.get("job_location")

        if q1 or q2 or q3:                                                              # if any item is true then search our database
            return Job.objects.filter(Q(title__icontains=q1) |                          # where we return the filter by our query
                   Q(description__icontains=q1),                                        # this is where we will be able to search via key word .. i.e. single word
                                      job_type=q2,                                      # job_type is an option so we don't use underscore // i.e. it is not a text value, an option value rather
                                      location__icontains=q3                            # the query fields come from .models // title; job_type; location
                                      ).order_by('-id')
        return Job.objects.all().order_by('-id')                                        # where if there are no results return all objects via negative id result

    def get_context_data(self, *args, **kwargs):
        context = super(SearchJobView, self).get_context_data(*args, **kwargs)
        context['categories'] = Category.objects.all()                                  # added and we can use this category context in our index.html file
                                                                                        # removed category line: context['category'] = self.category
        return context

class UpdateJobView(SuccessMessageMixin, UpdateView):                       # UpdateView because we are updating jobs here
    model = Job
    template_name = 'jobs/update.html'
    form_class = UpdateJobForm                                              # we need to create a form for this form_class in .jobs.forms
    success_message = "You have updated your job"                           # we import SuccessMessageMixin to use success_message

    def form_valid(self, form):
        form.instance.employer = self.request.user                          # verifies instance.employer is authenticated user
        return super(UpdateJobView, self).form_valid(form)

    def get(self, request, *args, **kwargs):                                # this function will check and determine if the user is requested user or not
        self.object = self.get_object()
        if self.object.employer != request.user:
            return HttpResponseRedirect('/')
        return super(UpdateJobView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('jobs:single_job', kwargs={"pk":self.object.pk, "slug":self.object.slug})


class DeleteJobView(SuccessMessageMixin, DeleteView):
    model = Job
    success_url = '/'
    template_name = 'jobs/delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.employer == request.user:                               # where we check if the requested user is the correct user to delete the job
            self.object.delete()                                               # implement delete if employer == request.user
            return HttpResponseRedirect(self.success_url)
        else:
            return HttpResponseRedirect(self.success_url)

    def get(self, request, *args, **kwargs):                                    # this function will check and determine if the user is requested user or not
        self.object = self.get_object()
        if self.object.employer != request.user:
            return HttpResponseRedirect('/')
        return super(DeleteJobView, self).get(request, *args, **kwargs)         # copied the get function and changed to DeleteJobView attribute