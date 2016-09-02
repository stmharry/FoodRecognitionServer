import collections
import json
import requests
import sys
import time

start = time.time()
response = requests.post(sys.argv[1], json={
    'images': [
        'http://a.ecimg.tw/pic/v1/data/item/201608/D/G/C/F/0/7/DGCF07-A900665NY000_57c406ec5d958.jpg',
        'http://a.ecimg.tw/pic/v1/data/item/201608/D/G/C/F/0/7/DGCF07-A900665NY000_57c406ec5d958.jpg',
        'http://a.ecimg.tw/pic/v1/data/item/201608/D/G/C/F/0/7/DGCF07-A900665NY000_57c406ec5d958.jpg',
        'http://a.ecimg.tw/pic/v1/data/item/201608/D/G/C/F/0/7/DGCF07-A900665NY000_57c406ec5d958.jpg',
    ]
})

print('%.3f s' % (time.time() - start))
print(json.dumps(json.loads(response.text, object_pairs_hook=collections.OrderedDict), indent=4))
