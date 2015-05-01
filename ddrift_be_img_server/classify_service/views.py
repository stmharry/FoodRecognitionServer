from rest_framework.decorators import parser_classes
from rest_framework.decorators import renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

import numpy
import skimage.io
from itertools import izip

DJANGO_ROOT = '/vol/django_server'
CAFFE_ROOT = DJANGO_ROOT + '/caffe'
CAFFE_PYTHON = CAFFE_ROOT + '/python'
MODEL_FILE = CAFFE_ROOT + '/models/ddrift/deploy.prototxt'
PRETRAINED = CAFFE_ROOT + '/models/ddrift/models/caffenet_ddrift.caffemodel'

import sys
if CAFFE_PYTHON not in sys.path:
  sys.path.insert(0, CAFFE_PYTHON)
import caffe

CLASS_DEF = ['Undefined', 'Look', 'Menu', 'People', 'Dish', 'Drink', 'Dessert']

class ClassifyService(APIView):
  net = caffe.Classifier(
      MODEL_FILE,
      PRETRAINED,
      mean = numpy.load('/vol/proto/ddrift_mean_1_5_1.npy'),
      channel_swap = (2,1,0),
      raw_scale = 255,
      image_dims = (227, 227))
  net.set_mode_gpu()

  @parser_classes((JSONParser,))
  @renderer_classes((JSONRenderer,))
  def post(self, request, format=None):
    images = request.data['images']
    image_array = []
    ret_content = []
    for image_url in images:
      input_image = skimage.io.imread(image_url)
      input_image = numpy.array(input_image, dtype = numpy.float)
      input_image /= 255.0
      image_array.append(input_image)
    predictions = ClassifyService.net.predict(image_array)
    for prediction in predictions:
      classes = {k: '{:.4f}'.format(v) for k, v in izip(CLASS_DEF, prediction)}
      ret_content.append({'status': 'ok', 'classes': classes})

    ret_content = {'results' : ret_content}

    return Response(ret_content)
