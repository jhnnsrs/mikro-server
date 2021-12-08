from django.contrib.auth import get_user_model
from grunnlag.omero import OmeroRepresentationInput
from grunnlag.types import OmeroRepresentation
from lok import bounced
from grunnlag.enums import RepresentationVariety, RepresentationVarietyInput
from balder.enum import InputEnum
from balder.types import BalderMutation
import graphene
from grunnlag import models, types
import logging
import namegenerator
from graphene.types.generic import GenericScalar


logger = logging.getLogger(__name__)


class UpdateRepresentation(BalderMutation):
    """Updates an Representation (also retriggers meta-data retrieval from data stored in)"""

    class Arguments:
        rep = graphene.ID(
            required=True, description="Which sample does this representation belong to"
        )

    @bounced()
    def mutate(root, info, *args, **kwargs):
        rep = models.Representation.objects.get(id=kwargs.pop("rep"))
        rep.save()
        return rep

    class Meta:
        type = types.Representation


class CreateRepresentation(BalderMutation):
    """Creates a Representation"""

    class Arguments:
        sample = graphene.ID(
            required=False,
            description="Which sample does this representation belong to",
        )
        name = graphene.String(
            required=False,
            description="A cleartext description what this representation represents as data",
        )
        creator = graphene.String(
            required=False,
            description="The Email of the user creating the Representation (only for backend apps)",
        )
        variety = graphene.Argument(
            RepresentationVarietyInput,
            required=False,
            description="A description of the variety",
        )
        tags = graphene.List(
            graphene.String,
            required=False,
            description="Do you want to tag the representation?",
        )
        origin = graphene.ID(
            required=False,
            description="Which representation was used to create this representation",
        )
        meta = GenericScalar(required=False, description="Meta Parameters")
        omero = graphene.Argument(OmeroRepresentationInput)

    @bounced()
    def mutate(root, info, *args, creator=None, **kwargs):
        sampleid = kwargs.pop("sample", None)
        variety = kwargs.pop("variety", RepresentationVariety.UNKNOWN.value)
        name = kwargs.pop("name", namegenerator.gen())
        tags = kwargs.pop("tags", [])
        meta = kwargs.pop("meta", None)
        omero = kwargs.pop("omero", None)
        origin = kwargs.pop("origin", None)
        creator = info.context.user or (
            get_user_model().objects.get(email=creator) if creator else None
        )

        print("oiNAOINSOINSAOISNOASNOASINOASINS")

        print(omero)

        rep = models.Representation.objects.create(
            name=name,
            sample_id=sampleid,
            variety=variety,
            creator=creator,
            meta=meta,
            omero=omero,
            origin_id=origin,
        )
        if tags:
            rep.tags.add(*tags)

        rep.save()

        return rep

    class Meta:
        type = types.Representation


class DeleteRepresentationResult(graphene.ObjectType):
    id = graphene.String()


class DeleteRepresentation(BalderMutation):
    """Create an experiment (only signed in users)"""

    class Arguments:
        id = graphene.ID(
            description="The ID of the two deletet Representation", required=True
        )

    @bounced()
    def mutate(root, info, id, **kwargs):
        rep = models.Representation.objects.get(id=id)
        rep.delete()
        return {"id": id}

    class Meta:
        type = DeleteRepresentationResult
