from rest_framework.decorators import parser_classes
from rest_framework.decorators import renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

import collections
import skimage.io
import sys

RESNET_ROOT = ''  # TODO
WORKING_DIR_6 = ''  # TODO
WORKING_DIR_36 = '' # TODO
GPU_FRAC = 0.5
BATCH_SIZE = int(32 * GPU_FRAC)
NUM_TEST_CROPS = 8
TOP_K = 6

if RESNET_ROOT not in sys.path:
    sys.path.append(RESNET_ROOT)


from ResNet import Meta, QueueProducer, Preprocess, Batch, Net, ResNet50, Postprocess, Timer


class NetWrapper(object):
    def __init__(self, working_dir):
        Meta.test(working_dir=working_dir)
        self.producer = QueueProducer()
        self.preprocess = Preprocess(num_test_crops=NUM_TEST_CROPS)
        self.batch = Batch(batch_size=BATCH_SIZE, num_test_crops=NUM_TEST_CROPS)
        self.net = ResNet50(num_test_crops=NUM_TEST_CROPS, gpu_frac=GPU_FRAC)
        self.postprocess = Postprocess()

        with Timer('Building network...'):
            self.producer.blob().func(self.preprocess.test).func(self.batch.test).func(self.net.build)
            self.blob = self.postprocess.blob(self.net.prob)
            self.net.start(default_phase=Net.Phase.TEST)

    def get_results(self, urls):
        num_urls = len(urls)
        self.net.online(**self.batch.kwargs(total_size=num_urls, phase=Net.Phase.TEST))

        with Timer('ResNet50 running prediction on %d images... ' % num_urls):
            for url in urls:
                self.net.online(**self.producer.kwargs(image=skimage.io.imread(url)))

            results = list()
            while True:
                fetch = self.net.online(**self.blob.kwargs())
                probs = fetch[self.net.prob.name]
                for prob in probs:
                    indices = sorted(xrange(len(Meta.CLASS_NAMES)), key=prob.__getitem__)[:-(TOP_K + 1):-1]
                    classes = collections.OrderedDict([(Meta.CLASS_NAMES[index], round(prob[index], 4)) for index in indices])
                    results.append(dict(status='ok', classes=classes))
                if probs.size == 0:
                    break

        return results


class BaseClassifyService(APIView):
    @parser_classes((JSONParser,))
    @renderer_classes((JSONRenderer,))
    def post(self, request, format=None):
        content = dict(results=self.NET_WRAPPER.get_results(request.data['images']))

        return Response(content)


class ClassifyService_6(BaseClassifyService):
    NET_WRAPPER = NetWrapper(working_dir=WORKING_DIR_6)


class ClassifyService_36(BaseClassifyService):
    NET_WRAPPER = NetWrapper(working_dir=WORKING_DIR_36)
