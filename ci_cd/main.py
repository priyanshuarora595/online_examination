from django.http import HttpResponse
# import git
import os
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def webhook(request):
    if request.method == "POST":
        os.system("ci_cd/main_script.sh")
        return HttpResponse("Updated Succesfully", status=200)
    else:
        return HttpResponse("Wrong event type", status=400)
