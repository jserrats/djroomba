from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from matrix.models import Image
import matrix.matrix as m


@login_required
def index(request):
    images = Image.objects.order_by("-date")
    context = {"images": images}
    return render(request, "matrix/index.html", context)


@require_POST
@login_required
def print(request, image_name):
    image = get_object_or_404(Image, photo="matrix/" + image_name)
    im = m.open_as_image(image.photo)
    m.send_image(m.process_image(im))
    return HttpResponse("OK")


@require_POST
@login_required
def delete(request, image_name):
    image = get_object_or_404(Image, photo="matrix/" + image_name)
    image.delete()
    return HttpResponse("OK")


@require_POST
@login_required
def clear(request):
    m.clear()
    return HttpResponse("OK")
