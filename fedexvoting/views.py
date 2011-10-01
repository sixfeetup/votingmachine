from pyramid.view import view_config
from fedexvoting.models import PollingPlace


@view_config(context=PollingPlace,
    renderer='fedexvoting:templates/polling_place.pt')
def polling_view(request):
    return {}
