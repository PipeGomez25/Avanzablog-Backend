from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class LikesPagination(PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'total_count': self.page.paginator.count,
            'next_page_url': self.get_next_link(),
            'previous_page_url': self.get_previous_link(),
            'results': data
        })