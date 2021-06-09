from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.fields import get_error_detail


def exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(detail=get_error_detail(exc))

    return drf_exception_handler(exc, context)


def get_or_404(klass, title=None, **kwargs):
    """
    This provides a better custom serializer validation error

    Use get() to return an object, or raise better custom serializer validation error
    klass is be a Model. title is the subject of the error message if raised,
    All other passed arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.

    Args:
        klass(Class): A model class
        title(str): Title string
        kwargs(dic): Keyword argument
    """
    title = title if title else klass.__name__
    if not kwargs:
        raise serializers.ValidationError("include atleast one kwarg search parameter")
    kwargs_length = len(kwargs)
    try:
        return klass.objects.get(**kwargs)
    except klass.DoesNotExist:
        search_key, search_value = kwargs.popitem()
        search_key = search_key.replace("_", " ")
        if kwargs_length == 1:
            raise serializers.ValidationError(
                "{} with {} `{}` does not exist".format(title, search_key, search_value)
            )
        raise serializers.ValidationError(
            "{} with {} `{}` and more search parameters does not exit".format(
                title, search_key, search_value
            )
        )


FAILURE_MSGS = {
    "insufficient_funds": "insufficient funds",
    "must_be_greater": "{} amount must be greater than {}",
    "no_self_p2p" : "You cannot make p2p transfer to yourself"
}
