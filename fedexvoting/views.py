from pyramid.view import view_config
from fedexvoting.models import MyModel

@view_config(context=MyModel, renderer='fedexvoting:templates/mytemplate.pt')
def my_view(request):
    return {'project':'fedexvoting'}
