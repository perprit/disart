import os
import cv2

import numpy as np

from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext

from main.AreaChartRecog import *
from main.models import Image
from main.forms import ImageForm

def draw(request, id=-1):
    image = get_object_or_404(Image, pk=id)
    #result = areaChartRecog(image.imgfile.path);
    return render(
        request,
        'main/draw.html',
        {'image': image,},
    )

def upload(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            newimg = Image(imgfile = request.FILES['imgfile'])
            newimg.save()

            return HttpResponseRedirect(reverse('upload'))
    else:
        form  = ImageForm()

    images = Image.objects.all()

    return render(
        request,
        'main/upload.html',
        {'images': images, 'form': form},
    )

def delete(request, id=-1):
    image = get_object_or_404(Image, pk=id)
    os.remove(image.imgfile.path)
    image.delete()

    return HttpResponseRedirect(reverse('upload'));

def chartrecog(request):
    requestData = json.loads(request.body)
    image_id = requestData['image_id']
    image = get_object_or_404(Image, pk=image_id)
    if(requestData['type'] == "null"):  # recognition without sketch info
        result = areaChartRecog(image.imgfile.path);
    else:   # recognition with sketch info
        coord = requestData['coord']
        result = areaChartRecog(image.imgfile.path, coord);

    if request.is_ajax():
        return HttpResponse(result);
    else:
        return HttpResponse(json.dumps({"error":"recog failed(main.views.chartrecog)"}))
