from pyramid.view import view_config
from fedexvoting.models import PollingPlace
from fedexvoting.models import VotingBoothFolder
from fedexvoting.models import VotingBooth


@view_config(context=PollingPlace,
    renderer='fedexvoting:templates/polling_place.pt')
def polling_view(request):
    return {}


@view_config(context=VotingBoothFolder,
    renderer='fedexvoting:templates/voting_booth_folder.pt')
def voting_booth_folder(request):
    return {}


@view_config(context=VotingBooth,
    renderer='fedexvoting:templates/voting_booth.pt')
def voting_booth_view(request):
    return {}
