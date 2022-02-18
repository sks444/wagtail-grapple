import graphene

from graphene_django.types import DjangoObjectType

from wagtailsvg.models import Svg

from ..registry import registry
from ..utils import get_media_item_url, resolve_queryset
from .collections import CollectionObjectType
from .structures import QuerySetList
from .tags import TagObjectType


class SvgObjectType(DjangoObjectType):
    """
    Base document type used if one isn't generated for the current model.
    All other node types extend this.
    """

    id = graphene.ID(required=True)
    title = graphene.String(required=True)
    file = graphene.String(required=True)
    url = graphene.String(required=True)
    collection = graphene.Field(lambda: CollectionObjectType, required=True)
    tags = graphene.List(graphene.NonNull(lambda: TagObjectType), required=True)

    def resolve_url(self, info, **kwargs):
        """
        Get document file url.
        """
        return get_media_item_url(self)

    def resolve_tags(self, info, **kwargs):
        return self.tags.all()

    class Meta:
        model = Svg


def get_svg_model():
    return "wagtailsvg.Svg"


def get_svg_type():
    mdl = get_svg_model()
    return registry.svgs.get(mdl, SvgObjectType)


def SvgsQuery():
    mdl = get_svg_model()
    mdl_type = get_svg_type()

    class Mixin:
        svg = graphene.Field(mdl_type, id=graphene.ID())
        svgs = QuerySetList(
            graphene.NonNull(mdl_type),
            enable_search=True,
            required=True,
            collection=graphene.Argument(
                graphene.ID, description="Filter by collection id"
            ),
        )
        svg_type = graphene.String(required=True)

        def resolve_svg(self, info, id, **kwargs):
            """Returns a svg given the id, if in a public collection"""
            try:
                return mdl.objects.filter(
                    collection__view_restrictions__isnull=True
                ).get(pk=id)
            except BaseException:
                return None

        def resolve_svgs(self, info, **kwargs):
            """Returns all svgs in a public collection"""
            qs = mdl.objects.filter(collection__view_restrictions__isnull=True)
            return resolve_queryset(qs, info, **kwargs)

        def resolve_svg_type(self, info, **kwargs):
            return get_svg_type()

    return Mixin
