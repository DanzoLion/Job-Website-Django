from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from PIL import Image
from ckeditor.fields import RichTextField



# Create your models here.
from jobs.models import Job


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):                        # this manages users: employee and employer defined below
        if not email:
            raise ValueError('Your email is not correct!')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):                    # create_user = we are creating users here
        extra_fields.setdefault('is_superuser', False)                              # we create user/ and specify not superuser
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):                    # manages our super_user
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self._create_user(email,password,**extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):                                  # this will be our user account model
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=50, blank=False)
    last_name = models.CharField(_('last name'), max_length=50, blank=False)
    date_joined = models.DateField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('is_staff'), default=False)
    is_employee = models.BooleanField(default=False)
    is_employer = models.BooleanField(default=False)


    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_profile_id(self):
        return self.profile.id                                                      # we use profile because user is defined below with related id / relation name

    def count_unread_messages(self):
        return self.invites.filter(unread=True).count()                             # we created .invites below and are able to filter with inherited class via related name 'invites'

    def unread_messages(self):                                                      # if we remove .count() then we will return our invite model
        return self.invites.filter(unread=True).values_list('job_id',flat=True)     # we need to use .values_list() because we are filtering via job_id that must be unique



class Profile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(upload_to="media/users", default="media/users/kazuky-akayashi-pF4iSe6NVkI-unsplash.jpg")  # path where our images will be stored # path image will become default
    birth_day = models.DateField(default=None, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    resume = RichTextField(blank=True)                                                                                  # field only belongs to employee
    company = models.CharField(max_length=250, blank=True)                                                              # field only belongs to employer
    wish_list = models.ManyToManyField(Job,default=None,blank=True,related_name="wish_list")                            # ManyToMany because the wish list can contain many jobs and jobs can be in other wishlists

    def __str__(self):
        return self.user.first_name +" "+ self.user.last_name+" " +self.user.email

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image)
        if img.height > 200 or img.width > 200:
            new_size = (200, 200)
            img.thumbnail(new_size)
            img.save(self.image.path)


@receiver(models.signals.post_save, sender=Account)
def post_save_user_signal(sender, instance, created, **kwargs):
    if created:
        instance.save()

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=Account)


class Invite(models.Model):                                                                 # this is our message system between the employer and employee
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="invites")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="invites")
    date = models.DateField(default=None, blank=True, null=True)
    message = RichTextField(blank=True)                                                     # with this item we can use CK Editor
    unread = models.BooleanField(default=True)                                              # our database will display this as default unread when message is created

    def __str__(self):
        return self.job.title