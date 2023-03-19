from rest_framework import filters


class DateRangeFilter(filters.OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            if ordering[0] == 'date_range':
                start_date = request.query_params.get('start_date')
                end_date = request.query_params.get('end_date')
                if start_date and end_date:
                    queryset = queryset.filter(created_at__range=[start_date, end_date])
        return queryset
