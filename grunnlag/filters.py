from logging import logMultiprocessing
from typing_extensions import Required
from attr import field
import django
import graphene
from graphene.types.scalars import Int, String
from graphene.types.structures import List
from balder.enum import InputEnum
import django_filters
from django_filters.filters import ChoiceFilter
from graphene.types.dynamic import Dynamic
from taggit.models import Tag
from .models import ROI, Experiment, Metric, OmeroFile, Representation, Sample
from .enums import RepresentationVariety, RepresentationVarietyInput, RoiTypeInput
from django import forms
from graphene_django.forms.converter import convert_form_field
from balder.filters import EnumFilter, MultiEnumFilter
import json


class EnumChoiceField(forms.CharField):
    def __init__(self, *args, choices=None, type=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__choices = choices
        self.__type = type

    @property
    def overwritten_type(self):
        if self.__type:
            return self.__type
        return InputEnum.from_choices(self.__choices)


@convert_form_field.register(EnumChoiceField)
def convert_form_field_to_string_list(field):
    return field.overwritten_type(required=field.required)


class EnumFilter(django_filters.CharFilter):
    field_class = EnumChoiceField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.field_name

    def filter(self, qs, value):
        """Convert the filter value to a primary key before filtering"""
        if value:
            return qs.filter(**{self.field_name: value})
        return qs


class IDChoiceField(forms.JSONField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def overwritten_type(self, **kwargs):
        return graphene.List(graphene.ID, **kwargs)


@convert_form_field.register(IDChoiceField)
def convert_form_field_to_string_list(field):
    return field.overwritten_type(required=field.required)


class IDChoiceFilter(django_filters.MultipleChoiceFilter):
    field_class = IDChoiceField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, field_name="pk")


class ExperimentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Search for substring of name"
    )
    creator = django_filters.NumberFilter(field_name="creator")
    tags = django_filters.BaseInFilter(
        label="The tags you want to filter by", field_name="tags__name"
    )


class ThumbnailFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="representation__name",
        lookup_expr="icontains",
        label="Search for substring of name",
    )
    creator = django_filters.NumberFilter(field_name="creator")
    tags = django_filters.BaseInFilter(
        label="The tags you want to filter by", field_name="tags__name"
    )


class ROIFilter(django_filters.FilterSet):
    representation = django_filters.ModelChoiceFilter(
        queryset=Representation.objects.all(), field_name="representation"
    )
    creator = django_filters.NumberFilter(field_name="creator")
    tags = django_filters.BaseInFilter(
        label="The tags you want to filter by", field_name="tags__name"
    )
    type = MultiEnumFilter(type=RoiTypeInput, field_name="type")


class LabelFilter(django_filters.FilterSet):
    representation = django_filters.ModelChoiceFilter(
        queryset=Representation.objects.all(), field_name="representation"
    )
    creator = django_filters.NumberFilter(field_name="creator")


class RepresentationFilter(django_filters.FilterSet):
    tags = django_filters.BaseInFilter(
        method="my_tag_filter", label="The tags you want to filter by"
    )
    ids = django_filters.MultipleChoiceFilter(
        method="my_ids_filter", label="The ids you want to filter by"
    )
    experiments = django_filters.ModelMultipleChoiceFilter(
        queryset=Experiment.objects.all(),
        field_name="sample__experiments",
        label="The Experiment the Sample of this Representation belongs to",
    )
    samples = django_filters.ModelMultipleChoiceFilter(
        queryset=Sample.objects.all(), field_name="sample"
    )
    ordering = django_filters.OrderingFilter(fields={"created_at": "time"})
    has_metric = django_filters.CharFilter(
        method="metric_filter", label="Filter by required Metric Keys (seperated by ,)"
    )
    order = django_filters.BaseInFilter(method="order_filter", label="Order by Keys")
    variety = EnumFilter(type=RepresentationVarietyInput, field_name="variety")
    forceThumbnail = django_filters.BooleanFilter(
        field_name="thumbnail", method="thumbnail_filter"
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr=("gt"),
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr=("lt")
    )
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Search for substring of name"
    )
    derived_tags = django_filters.BaseInFilter(
        method="derived_tag_filter", label="The tags you want to filter by"
    )

    class Meta:
        model = Representation
        fields = ["name"]

    def my_tag_filter(self, queryset, name, value):
        if value:
            return queryset.filter(tags__name__in=value)
        return queryset

    def my_ids_filter(self, queryset, name, value):
        if value:
            return queryset.filter(id__in=value)
        return queryset

    def derived_tag_filter(self, queryset, name, value):
        return queryset.filter(derived__tags__name__in=value).distinct()

    def order_filter(self, queryset, name, value):
        return queryset.order_by(*value)

    def thumbnail_filter(self, queryset, name, value):
        if value:
            return queryset.exclude(thumbnail__isnull=True).exclude(thumbnail__exact="")
        return queryset

    def metric_filter(self, queryset, name, value):
        tag_list = [item.strip() for item in value.split(",")]

        return queryset.filter(metrics__key__in=tag_list)


class MetricFilter(django_filters.FilterSet):
    keys = django_filters.BaseInFilter(
        method="my_key_filter", label="The key you want to filter by"
    )
    sample = django_filters.ModelChoiceFilter(
        queryset=Sample.objects.all(), field_name="sample"
    )
    experiment = django_filters.ModelChoiceFilter(
        queryset=Sample.objects.all(), field_name="experiment"
    )
    representation = django_filters.ModelChoiceFilter(
        queryset=Representation.objects.all(), field_name="rep"
    )
    order = django_filters.BaseInFilter(method="order_filter", label="Order by Keys")

    def my_key_filter(self, queryset, name, value):
        return queryset.filter(key__in=value)

    def order_filter(self, queryset, name, value):
        return queryset.order_by(*value)


class SampleFilter(django_filters.FilterSet):
    experiments = django_filters.ModelMultipleChoiceFilter(
        queryset=Experiment.objects.all(), field_name="experiments"
    )
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    bioseries = django_filters.CharFilter(
        field_name="bioseries__name", label="The name of the desired BioSeries"
    )
    ids = IDChoiceFilter(
        label="The ids you want to filter by",
    )
    representations = django_filters.ModelMultipleChoiceFilter(
        queryset=Representation.objects.all(),
        field_name="representations",
        label="The ids you want to filter by",
    )
    order = django_filters.BaseInFilter(method="order_filter", label="Order by Keys")

    def order_filter(self, queryset, name, value):
        return queryset.order_by(*value)

    def my_ids_filter(self, queryset, name, value):
        if value:
            return queryset.filter(id__in=value)
        return queryset

    def my_repids_filter(self, queryset, name, value):
        print(value)
        if value:
            return queryset.filter(representations__id__in=value)
        return queryset

    class Meta:
        model = Sample
        fields = ["creator", "experiments", "bioseries", "name"]


class TagFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    def order_filter(self, queryset, name, value):
        return queryset.order_by(*value)

    class Meta:
        model = Tag
        fields = ["name"]


class OmeroFileFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    def order_filter(self, queryset, name, value):
        return queryset.order_by(*value)

    class Meta:
        model = OmeroFile
        fields = ["name"]
