from django.core.paginator import Paginator

from .constants import PAGINATOR_LIMIT


def paginator_func(request, object_list):
    paginator = Paginator(object_list, PAGINATOR_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
