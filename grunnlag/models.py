from grunnlag.managers import RepresentationManager
from django.db import models

# Create your models here.
from .enums import RepresentationVariety
import logging

from django.contrib.auth import get_user_model
from django.db import models

from taggit.managers import TaggableManager
from matrise.models import  Matrise

logger = logging.getLogger(__name__)

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class Antibody(models.Model):

    name = models.CharField(max_length=100)
    creator = models.ForeignKey(get_user_model(), blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        identifiers = ["model"]


class Experiment(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    description_long = models.TextField(null=True,blank=True)
    linked_paper = models.URLField(null=True,blank=True)
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    image = models.ImageField(upload_to='experiment_banner',null=True,blank=True)

    def __str__(self):
        return "Experiment {0} by {1}".format(self.name,self.creator.username)

    class Meta:
        identifiers = ["model"]

class ExperimentalGroup(models.Model):
    name = models.CharField(max_length=200, help_text="The experimental groups name")
    description = models.CharField(max_length=1000,  help_text="A brief summary of applied techniques in this group")
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, help_text="The experiment this Group belongs too")
    iscontrol = models.BooleanField(help_text="Is this Experimental Group a ControlGroup?")

    def __str__(self):
        return "ExperimentalGroup {0} on Experiment {1}".format(self.name,self.experiment.name)

    class Meta:
        identifiers = ["model"]


class Animal(models.Model):
    name = models.CharField(max_length=100)
    age = models.CharField(max_length=400)
    type = models.CharField(max_length=500)
    creator = models.ForeignKey(get_user_model(), blank=True, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, blank=True, on_delete=models.CASCADE, null=True)
    experimentalgroup = models.ForeignKey(ExperimentalGroup, blank=True, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        identifiers = ["model"]


class Sample(models.Model):
    """ A sgfsefsef is a multi-dimensional Array that can do what ever it wants """
    creator = models.ForeignKey(get_user_model(), on_delete=models.SET(get_sentinel_user))
    name = models.CharField(max_length=1000)
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, blank=True, null=True)
    nodeid = models.CharField(max_length=400, null=True, blank=True)
    experimentalgroup = models.ForeignKey(ExperimentalGroup, on_delete=models.SET_NULL, blank=True, null=True)
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, blank=True, null=True)


    class Meta:
        identifiers = ["model"]


    def __str__(self):
        return "{0} by User: {1}".format(self.name,self.creator.username)


    def delete(self, *args, **kwargs):
        logger.info("Trying to remove Sample H5File")
        super(Sample, self).delete(*args, **kwargs)


    



class Representation(Matrise):
    group = "representation"

    ''' A Representation is 5-dimensional representation of a microscopic image '''
    origin = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null= True, related_name="derived", related_query_name="derived")
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='representations', help_text="The Sample this representation belongs to")
    type = models.CharField(max_length=400, blank=True, null=True, help_text="The Representation can have varying types, consult your API")
    variety = models.CharField(max_length=400, help_text="The Representation can have varying types, consult your API", choices=RepresentationVariety.choices, default=RepresentationVariety.UNKNOWN)
    chain = models.CharField(max_length=9000, blank=True, null=True)
    nodeid = models.CharField(max_length=400, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    objects = RepresentationManager()

    class Meta:
        permissions = [
            ('download_representation', 'Can download Presentation')
        ]
        identifiers = ["array","model"]

    def __str__(self):
        return f'Representation of {self.name}'



class ROI(models.Model):
    nodeid = models.CharField(max_length=400, null=True, blank=True)
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    vectors = models.CharField(max_length=3000, help_text= "A json dump of the ROI Vectors (specific for each type)")
    color = models.CharField(max_length=100, blank=True, null=True)
    signature = models.CharField(max_length=300,null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    representation = models.ForeignKey(Representation, on_delete=models.CASCADE,blank=True, null=True, related_name="rois")
    experimentalgroup = models.ForeignKey(ExperimentalGroup, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        identifiers = ["model","roi"]


    def __str__(self):
        return f"ROI created by {self.creator.username} on {self.representation.name}"


