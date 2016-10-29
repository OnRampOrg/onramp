from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template


@login_required
def main(request):
    """ Renders the main Admin dashboard on login

        URL: /public/Workspace/

    :param request:
    :return:
    """
    context = Context({'username': request.user})
    template = get_template('workspace.html')
    return HttpResponse(template.render(context))