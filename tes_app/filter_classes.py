from django_filters import rest_framework as filters
from tes_app.models import User

class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass

class UserFilterClass(filters.FilterSet):
    user_id = NumberInFilter(field_name='id', lookup_expr='in', required=False, distinct=True)
    user_email = filters.CharFilter(method='filter_user_email',required=False),
    user_name = filters.CharFilter(method='filter_user_name',required=False),

    class Meta:
        model = User
        fields = ["id", 'email', 'name']

    def filter_user_email(self,querset, name, value):
        querset = querset.filter(user_email__email=value)
        return querset

    def filter_user_name(self,querset, name, value):
        querset = querset.filter(user_name__name=value)
        return querset

