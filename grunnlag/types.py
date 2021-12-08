from django.contrib.auth import get_user_model
from graphene.types.scalars import String
from bord.filters import TableFilter
from grunnlag.omero import Channel, OmeroRepresentation, PhysicalSize, Plane
from graphene.types.generic import GenericScalar
from grunnlag.filters import (
    MetricFilter,
    RepresentationFilter,
    SampleFilter,
)
from balder.fields.filtered import BalderFiltered
from balder.fields.offsetfiltered import BalderFilteredWithOffset
from balder.types.object import BalderObject
import graphene
from grunnlag import models
from taggit.managers import TaggableManager
from taggit.models import Tag
from graphene_django.converter import convert_django_field
from django.conf import settings
from grunnlag.enums import OmeroFileType
from bord import models as bordmodels


class Tag(BalderObject):
    class Meta:
        model = Tag


@convert_django_field.register(TaggableManager)
def convert_field_to_string(field, registry=None):
    return graphene.List(String, description=field.help_text, required=not field.null)


class Thumbnail(BalderObject):
    def resolve_image(root, info, *args, **kwargs):
        return root.image.url if root.image else None

    class Meta:
        model = models.Thumbnail
        description = models.Thumbnail.__doc__


class DataModel(graphene.ObjectType):
    identifier = graphene.String(description="Name")
    extenders = graphene.List(graphene.String)


class Node(graphene.ObjectType):
    name = graphene.String(description="Name")
    interface = graphene.String(description="Name")
    package = graphene.String(description="Name")
    type = graphene.String(description="Name")
    args = graphene.List(GenericScalar)
    kwargs = graphene.List(GenericScalar)
    returns = graphene.List(GenericScalar)


class Metric(BalderObject):
    class Meta:
        model = models.Metric


class OmeroFile(BalderObject):
    thumbnail = graphene.String(description="Url of a thumbnail")

    def resolve_file(root, info, *args, **kwargs):
        return root.file.url if root.file else None

    class Meta:
        model = models.OmeroFile


class Column(graphene.ObjectType):
    name = graphene.String()
    field_name = graphene.String()
    pandas_type = graphene.String()
    numpy_type = graphene.String()
    metadata = GenericScalar()


class Table(BalderObject):
    query = graphene.List(
        lambda: graphene.List(GenericScalar),
        description="List of List",
        columns=graphene.List(
            graphene.String, description="Columns you want to select", required=False
        ),
        offset=graphene.Int(required=False, description="The Offset for the query"),
        limit=graphene.Int(required=False, description="The Offset for the query"),
    )
    columns = graphene.List(Column, description="Columns Data")

    def resolve_query(root, info, *args, columns=[], offset=0, limit=200):
        pd_thing = root.store.data.read_pandas().to_pandas()
        pd_thing = pd_thing[columns] if columns else pd_thing
        return pd_thing.head(limit).values.tolist()

    class Meta:
        model = bordmodels.Table


class Representation(BalderObject):
    """A Representation is a multi-dimensional Array that can do what ever it wants


    @elements/rep:latest


    """

    metrics = BalderFilteredWithOffset(
        Metric,
        filterset_class=MetricFilter,
        related_field="metrics",
    )
    latest_thumbnail = graphene.Field(Thumbnail)
    omero = graphene.Field(OmeroRepresentation)
    tables = BalderFilteredWithOffset(
        Table,
        filterset_class=TableFilter,
        related_field="tables",
    )
    derived = BalderFilteredWithOffset(
        lambda: Representation,
        model=models.Representation,
        filterset_class=RepresentationFilter,
        related_field="derived",
    )

    def resolve_latest_thumbnail(root, info, *args, **kwargs):
        return root.thumbnails.last()

    class Meta:
        model = models.Representation


class Sample(BalderObject):
    """Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure),
    was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of
    the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample @elements/sample"""

    representations = BalderFilteredWithOffset(
        Representation,
        filterset_class=RepresentationFilter,
        related_field="representations",
    )

    class Meta:
        model = models.Sample
        description = models.Sample.__doc__


class Experiment(BalderObject):
    """A Representation is a multi-dimensional Array that can do what ever it wants @elements/experiment"""

    samples = BalderFilteredWithOffset(
        Sample, filterset_class=SampleFilter, related_field="samples"
    )

    class Meta:
        model = models.Experiment


class User(BalderObject):
    class Meta:
        model = get_user_model()
        description = get_user_model().__doc__
