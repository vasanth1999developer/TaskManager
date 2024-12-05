from  rest_framework import pagination
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
       page_size=10
       def get_paginated_response(self, data):
              return Response(
                     {
                        'navigation': {                              
                               'next_page': self.get_next_link(),
                               'previous_page': self.get_previous_link(),
                               'current_page': self.page.number,
                               'total_pages': self.page.paginator.num_pages,
                               'total_items': self.page.paginator.count                             
                        },
                        'result': data
                     }
              )