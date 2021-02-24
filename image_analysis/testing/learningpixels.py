import pixellib
from pixellib.instance import instance_segmentation

segment_image = instance_segmentation()
segment_image.load_model("C:/Users/Laurence/Documents/GitHub/internship-code/testing/mask_rcnn_coco.h5")
segment_image.segmentImage("C:/Users/Laurence/Documents/GitHub/internship-code/testing/131647945_794079061324350_3606323282681870501_o.jpg", show_bboxes=True, output_image_name="C:/Users/Laurence/Documents/GitHub/internship-code/testing/image_new.jpg")
