from rest_framework.decorators import parser_classes
from rest_framework.decorators import renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

import collections
import skimage.io

from env import *
from ResNet import set_meta, Meta, QueueProducer, Preprocess, Batch, Net, ResNet50, Postprocess, Timer


def _(x):
    return round(x, 4)


class NetWrapper(object):
    def __init__(self, working_dir):
        if working_dir is None:
            return

        meta = Meta.test(working_dir=working_dir)
        set_meta(meta)

        self.meta = meta
        self.producer = QueueProducer()
        self.preprocess = Preprocess(num_test_crops=NUM_TEST_CROPS)
        self.batch = Batch(batch_size=BATCH_SIZE, num_test_crops=NUM_TEST_CROPS)
        self.net = ResNet50(num_test_crops=NUM_TEST_CROPS, gpu_frac=GPU_FRAC)
        self.postprocess = Postprocess()

        with Timer('Building network...'):
            self.producer.blob().func(self.preprocess.test).func(self.batch.test).func(self.net.build)
            self.blob = self.postprocess.blob([self.net.prob, self.net.consistency])
            self.net.start(default_phase=Net.Phase.TEST)

    def get_results(self, request):
        urls = request.data.get('images', [])
        num_urls = len(urls)

        self.net.online(**self.batch.kwargs(total_size=num_urls, phase=Net.Phase.TEST))

        with Timer('ResNet50 running prediction on %d images... ' % num_urls):
            for url in urls:
                self.net.online(**self.producer.kwargs(image=skimage.io.imread(url)))

            flag = True
            results = list()
            while flag:
                fetch = self.net.online(**self.blob.kwargs())

                for (prob, consistency) in zip(*[fetch[value.name] for value in self.blob.values]):
                    indices = sorted(xrange(len(self.meta.class_names)), key=prob.__getitem__)[:-(TOP_K + 1):-1]
                    classes = collections.OrderedDict([(self.meta.class_names[index], _(prob[index])) for index in indices])
                    results.append(dict(status='ok', classes=classes, consistency=_(consistency)))

                flag = (fetch[self.net.prob.name].size != 0)

        return results


class ContentClassifyService(APIView):
    NET_WRAPPER = NetWrapper(working_dir=WORKING_DIR_CONTENT_TYPE)

    @parser_classes((JSONParser,))
    @renderer_classes((JSONRenderer,))
    def post(self, request, format=None):
        content = dict(results=ContentClassifyService.NET_WRAPPER.get_results(request))
        return Response(content)


class FoodClassifyService(APIView):
    NET_WRAPPER = NetWrapper(working_dir=WORKING_DIR_FOOD_TYPE)

    @parser_classes((JSONParser,))
    @renderer_classes((JSONRenderer,))
    def post(self, request, format=None):
        content = dict(results=FoodClassifyService.NET_WRAPPER.get_results(request))
        return Response(content)
