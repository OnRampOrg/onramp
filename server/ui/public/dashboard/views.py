from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template


@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /admin/Dashboard

    :param request:
    :return:
    """
    context = Context({'username': request.user})
    template = get_template('user_dashboard.html')
    return HttpResponse(template.render(context))