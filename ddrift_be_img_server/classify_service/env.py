import sys

RESNET_ROOT = '/home/harry/Repository/FoodRecognitionV2'
if RESNET_ROOT not in sys.path:
    sys.path.append(RESNET_ROOT)

WORKING_DIR_CONTENT_TYPE = None  # '/mnt/data/content-save/2016-09-06-155356'
WORKING_DIR_FOOD_TYPE = '/mnt/data/food-save/2016-09-05-181554'

GPU_FRAC = 1.0
BATCH_SIZE = int(64 * GPU_FRAC)
NUM_TEST_CROPS = 16
TOP_K = 6
