from django.db import models
from django.db.models import ManyToManyField
from django.template.defaultfilters import slugify
from Job import settings
from ckeditor.fields import RichTextField



# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(default=None,editable=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)                                     # our slug field is used to store and generate urls for our dynamically created pages
        super(Category, self).save(*args, **kwargs)

    def job_count(self):                                                    # we can then add this function to our html class as {{ category.job_count }}
        return self.jobs.all().count()  * 50                                # jobs appears later in our models.py process .. where our related name is 'jobs' below / category




class Job(models.Model):
    title = models.CharField(max_length=300)
    company = models.CharField(max_length=300)
    CHOICES = (                                                             # WHERE WE CREATE A RADIO BUTTON FOR OUR CHOICES FIELD
        ('full_time', 'Full Time'),                                         # we will have 5 different job types here
        ('part_time', 'Part Time'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),

    )

    job_type = models.CharField(max_length=20, blank=False,default=None,choices=CHOICES)
    location = models.CharField(max_length=200, blank=False, default=None)
    description = RichTextField(blank=False, default=None)                                                       # changed to RichTextField
    publishing_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default=None, editable=False)
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None)               # relationship of one to many
    employee = ManyToManyField(settings.AUTH_USER_MODEL, default=None, blank=True, related_name="job_employee")  # employee is a user so we use: settings.AUTH_USER_MODEL
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="jobs", default=None)          # relationship of one to many .. defined by ForeignKey(); 1 will be default as none won't work

    
    def __str__(self):
        return self.title
    
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Job, self).save(*args,**kwargs)


    class Meta:
        ordering = ('-id',)                                                  # -id means we are listing jobs from last to first # we then need to register jobs in admin panel admin.py

