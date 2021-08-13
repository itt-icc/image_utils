import cv2
import numpy as np
import xml.etree.ElementTree as ET
import glob
import os
from PIL import Image
import numpy as np



# TODO change by your classnames
classes = ['class1', 'class2']
class_dict = {'class1': 0,"class2":1}

imgpath=list()
def get_all_img(path_name):
    #TODO recursion
    for dir_image in os.listdir(path_name):
        full_path = os.path.abspath(os.path.join(path_name,dir_image))
        if '全景' in full_path.split("\\"):continue
        if os.path.isdir(full_path):get_all_img(full_path)
        else:imgpath.append(full_path)
    print("All the img path:",*imgpath,sep="\n")


def cv2_letterbox_image(image, expected_size):
    ih, iw = image.shape[0:2]
    ew, eh = expected_size
    scale = min(eh / ih, ew / iw)
    # TODO redfine size
    nh = int(ih * scale)
    nw = int(iw * scale)
    image = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_CUBIC)
    top = (eh - nh) // 2
    bottom = eh - nh - top
    left = (ew - nw) // 2
    right = ew - nw - left
    new_img = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT)
    return new_img


def parse_xml(path):
    tree = ET.parse(path)
    root = tree.findall('outputs')[0].findall("object")[0].findall("item")
    print(len(root))
    class_list = []
    boxes_list = []
    # difficult_list = []
    for sub in root:
        xmin = float(sub.find('bndbox').find('xmin').text)
        xmax = float(sub.find('bndbox').find('xmax').text)
        ymin = float(sub.find('bndbox').find('ymin').text)
        ymax = float(sub.find('bndbox').find('ymax').text)
        boxes_list.append([xmin, ymin, xmax, ymax])
        class_list.append(class_dict[sub.find('name').text])
        #difficult_list.append(int(sub.find('difficult').text))
    return np.array(class_list), np.array(boxes_list).astype(np.int32)

def get_cls_box_w_h(path):
    tree = ET.parse(path)
    root = tree.findall('outputs')[0].findall("object")[0].findall("item")
    class_list = []
    boxes_list = []
    for sub in root:
        xmin = float(sub.find('bndbox').find('xmin').text)
        xmax = float(sub.find('bndbox').find('xmax').text)
        ymin = float(sub.find('bndbox').find('ymin').text)
        ymax = float(sub.find('bndbox').find('ymax').text)
        boxes_list.append([xmin, ymin, xmax, ymax])
        class_list.append(sub.find('name').text)
    size=tree.find("size")
    w=int(size[0].text)
    h=int(size[1].text)
    return class_list, np.array(boxes_list).astype(np.int32),w,h

def trans_cut(image,boxes,h):
    minymin=np.min(boxes[:,1])
    maxymax=np.max(boxes[:,3])
    uptol=300
    downtol=200
    uph  =minymin-uptol if minymin-uptol>0 else 0
    downh=maxymax+downtol if maxymax+downtol<h-1 else h-1
    img=image[uph:downh,:,:]
    boxes[:,1]-=uph
    boxes[:,3]-=uph
    return img,boxes,downh

def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True):
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)
    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, 64), np.mod(dh, 64)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios
    dw /= 2  # divide padding into 2 sides
    dh /= 2
    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)

def letterboxxml(boxes,ratio,pad):
    new_boxes = np.zeros_like(boxes)
    new_boxes[:, 0] = ratio[0] * boxes[:, 0] + pad[0]  # pad width
    new_boxes[:, 1] = ratio[1] * boxes[:, 1] + pad[1]  # pad height
    new_boxes[:, 2] = ratio[0] * boxes[:, 2] + pad[0]
    new_boxes[:, 3] = ratio[1] * boxes[:, 3] + pad[1]
    return new_boxes

def test(imgPath,xmlPath):
    
    img = cv2.imread(imgPath)
    _, boxes,_,h = get_cls_box_w_h(xmlPath)
    cut_img,cut_box,h=trans_cut(img,boxes,h)

    shape = (480, 640)
    padimg, ratio, pad = letterbox(cut_img.copy(), shape, auto=False, scaleup=False)
    new_boxes = letterboxxml(cut_box,ratio,pad)
    return padimg,new_boxes

def cut_box(imgPath,xmlPath):
    
    img = cv2.imread(imgPath)
    labels, boxes,w,h = get_cls_box_w_h(xmlPath)
    cut_img,cut_box,h=trans_cut(img,boxes,h)

    shape = (480, 640)
    padimg, ratio, pad = letterbox(cut_img.copy(), shape, auto=False, scaleup=False)
    new_boxes = letterboxxml(cut_box,ratio,pad)

    clsid=[classes.index(cls) for cls in labels]
    return padimg,new_boxes,clsid
    

def makexml(src_img_dir,new_img_dir,src_txt_dir,src_xml_dir):
    img_Lists = glob.glob(src_img_dir + '/*.jpg')

    img_basenames = []
    for item in img_Lists:
        img_basenames.append(os.path.basename(item))

    img_names = []
    for item in img_basenames:
        temp1, temp2 = os.path.splitext(item)
        img_names.append(temp1)

    for img in img_names:
        try:
            img_path = src_img_dir + '\\' + img + '.jpg'
            xml_path = src_txt_dir + '/%s.xml' % (img)
            im = Image.open(img_path)
            width, height = im.size
            padimg,gt, cls_id = cut_box(img_path, xml_path)

            cv2.imwrite(new_img_dir + '/' + img + '.jpg', padimg)

            xml_file = open((src_xml_dir + '/' + img + '.xml'), 'w')
            xml_file.write('<?xml version="1.0" ?>\n')
            xml_file.write('<doc>\n')
            xml_file.write(f'<folder>{src_img_dir}]</folder>\n')
            xml_file.write(f'<filename>{img}.jpg</filename>\n')
            xml_file.write('    <path>' + img_path + '</path>\n')
            xml_file.write('    <outputs>\n')
            xml_file.write('        <object>\n')

            count = 0
            for spt in gt:
                xml_file.write('            <item>\n')
                xml_file.write(f'                <name>{classes[int(cls_id[count])]}</name>\n')
                xml_file.write('                <bndbox>\n')
                xml_file.write('                    <xmin>' + str(int(spt[0])) + '</xmin>\n')
                xml_file.write('                    <ymin>' + str(int(spt[1])) + '</ymin>\n')
                xml_file.write('                    <xmax>' + str(int(spt[2])) + '</xmax>\n')
                xml_file.write('                    <ymax>' + str(int(spt[3])) + '</ymax>\n')
                xml_file.write('                </bndbox>\n')
                xml_file.write('            </item>\n')
                count += 1

            xml_file.write('        </object>\n')
            xml_file.write('    </outputs>\n')
            xml_file.write('    <labeled>true</labeled>\n')
            xml_file.write('    <size>\n')
            xml_file.write('        <width>' + str(width) + '</width>\n')
            xml_file.write('        <height>' + str(height) + '</height>\n')
            xml_file.write('        <depth>3</depth>\n')
            xml_file.write('    </size>\n')
            xml_file.write('</doc>')
        except:
            print(img_path,"go wrong. This image was not labelled! I just delete it.")

def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)            


if __name__=="__main__":

    '''
    workfolder
    ---src_img_dir
    ---new_img_dir
    ---cut_pad.py
    '''

    src_img_dir = r"raw"   #The relative path of the original picture (the picture used for labeling)
    new_img_dir = r"cutimg"#The relative path of the new picture, create one if not
    mkdir(new_img_dir)

    src_txt_dir = r"outputs_0810"  # Source xml folder
    src_xml_dir = r"cutxml"        # Save the xml folder, create one if not
    mkdir(src_xml_dir)

    makexml(src_img_dir,new_img_dir,src_txt_dir,src_xml_dir)



# TODO to test the image cut ,xml cut and letterbox function
# imgPath = r'test\2021-7-12-7_120.jpg'
# xmlPath = r'test\2021-7-12-7_120.xml'
# padimg,new_boxes=test(imgPath,xmlPath)

# sample = padimg.copy()
# for box in new_boxes:
#     cv2.rectangle(sample, (box[0], box[1]), (box[2], box[3]), (1, 0, 0), 1)

# cv2.imshow("sample",sample)
# cv2.waitKey (0)  
# cv2.destroyAllWindows()
