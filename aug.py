
import xml.etree.ElementTree as ET
import os
import imgaug as ia
import numpy as np
import shutil
from tqdm import tqdm
from PIL import Image
from imgaug import augmenters as iaa

ia.seed(311)

def read_xml_annotation(root, image_id):
    in_file = open(os.path.join(root, image_id))
    tree = ET.parse(in_file)
    root = tree.getroot()
    bndboxlist = []
    for object in root.findall('object'):
        bndbox = object.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        xmax = int(bndbox.find('xmax').text)
        ymin = int(bndbox.find('ymin').text)
        ymax = int(bndbox.find('ymax').text)
        bndboxlist.append([xmin, ymin, xmax, ymax])
    bndbox = root.find('object').find('bndbox')
    return bndboxlist


def change_xml_annotation(root, image_id, new_target):
    new_xmin = new_target[0]
    new_ymin = new_target[1]
    new_xmax = new_target[2]
    new_ymax = new_target[3]
    in_file = open(os.path.join(root, str(image_id) + '.xml'))
    tree = ET.parse(in_file)
    xmlroot = tree.getroot()
    object = xmlroot.find('object')
    bndbox = object.find('bndbox')
    xmin = bndbox.find('xmin')
    xmin.text = str(new_xmin)
    ymin = bndbox.find('ymin')
    ymin.text = str(new_ymin)
    xmax = bndbox.find('xmax')
    xmax.text = str(new_xmax)
    ymax = bndbox.find('ymax')
    ymax.text = str(new_ymax)
    tree.write(os.path.join(root, str("%06d" % (str(id) + '.xml'))))


def change_xml_list_annotation(root, image_id, new_target, saveroot, id):
    in_file = open(os.path.join(root, str(image_id) + '.xml')) 
    tree = ET.parse(in_file)
    #修改增强后的xml文件中的filename
    elem = tree.find('filename')
    elem.text = (str(id) + '.jpg')
    xmlroot = tree.getroot()
    #修改增强后的xml文件中的path
    elem = tree.find('path')
    if elem != None:
        elem.text = (saveroot + str(id) + '.jpg')

    index = 0
    for object in xmlroot.findall('object'): 
        bndbox = object.find('bndbox') 

        new_xmin = new_target[index][0]
        new_ymin = new_target[index][1]
        new_xmax = new_target[index][2]
        new_ymax = new_target[index][3]

        xmin = bndbox.find('xmin')
        xmin.text = str(new_xmin)
        ymin = bndbox.find('ymin')
        ymin.text = str(new_ymin)
        xmax = bndbox.find('xmax')
        xmax.text = str(new_xmax)
        ymax = bndbox.find('ymax')
        ymax.text = str(new_ymax)
        index = index + 1
    tree.write(os.path.join(saveroot, str(id + '.xml')))

def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path + ' successfully created')
        return True
    else:
        print(path + ' already exist')
        return False
    
def read_train_valid():
    file=[]
    with open('trainval.txt', 'r') as f:
        data = f.readlines()
        for item in data:
            file.append(item.strip())
    return file

def check_train(item,trainlist):
    if item in trainlist:
        return True
    return False


def aug():
    
    try:
        shutil.rmtree(AUG_XML_DIR)
    except FileNotFoundError as e:
        a = 1
    mkdir(AUG_XML_DIR)

    try:
        shutil.rmtree(AUG_IMG_DIR)
    except FileNotFoundError as e:
        a = 1
    mkdir(AUG_IMG_DIR)

    boxes_img_aug_list = []
    new_bndbox = []
    new_bndbox_list = []
    trainlist=read_train_valid()

    for name in tqdm(os.listdir(XML_DIR), desc='Processing'):
        if not check_train(name[:-4],trainlist):
            continue
        bndbox = read_xml_annotation(XML_DIR, name)
        # 保存原xml文件
        shutil.copy(os.path.join(XML_DIR, name), AUG_XML_DIR)
        # 保存原图
        og_img = Image.open(IMG_DIR+'/'+name[:-4] + '.jpg')
        og_img.convert('RGB').save(AUG_IMG_DIR + name[:-4] + '.jpg', 'JPEG')
        og_xml = open(os.path.join(XML_DIR, name)) 
        tree = ET.parse(og_xml)
        #修改增强后的xml文件中的filename
        elem = tree.find('filename')
        elem.text = (name[:-4] + '.jpg')
        tree.write(os.path.join(AUG_XML_DIR, name))
        
        for epoch in range(AUGLOOP):
            seq_det = seq.to_deterministic()  # 保持坐标和图像同步改变，而不是随机
            # 读取图片
            img = Image.open(os.path.join(IMG_DIR, name[:-4] + '.jpg'))
            # sp = img.size
            img = np.asarray(img)
            # bndbox 坐标增强
            for i in range(len(bndbox)):
                bbs = ia.BoundingBoxesOnImage([
                    ia.BoundingBox(x1=bndbox[i][0], y1=bndbox[i][1], x2=bndbox[i][2], y2=bndbox[i][3]),
                ], shape=img.shape)

                bbs_aug = seq_det.augment_bounding_boxes([bbs])[0]
                boxes_img_aug_list.append(bbs_aug)

                # new_bndbox_list:[[x1,y1,x2,y2],...[],[]]
                n_x1 = int(max(1, min(img.shape[1], bbs_aug.bounding_boxes[0].x1)))
                n_y1 = int(max(1, min(img.shape[0], bbs_aug.bounding_boxes[0].y1)))
                n_x2 = int(max(1, min(img.shape[1], bbs_aug.bounding_boxes[0].x2)))
                n_y2 = int(max(1, min(img.shape[0], bbs_aug.bounding_boxes[0].y2)))
                if n_x1 == 1 and n_x1 == n_x2:n_x2 += 1
                if n_y1 == 1 and n_y2 == n_y1:n_y2 += 1
                if n_x1 >= n_x2 or n_y1 >= n_y2:print('error', name)
                new_bndbox_list.append([n_x1, n_y1, n_x2, n_y2])
            #save img
            image_aug = seq_det.augment_images([img])[0]
            path = os.path.join(AUG_IMG_DIR,str(str(name[:-4]) + '_' + str(epoch)) + '.jpg')
            image_auged = bbs.draw_on_image(image_aug, size=0)
            Image.fromarray(image_auged).convert('RGB').save(path) 
            #saveXML
            change_xml_list_annotation(XML_DIR, name[:-4], new_bndbox_list, AUG_XML_DIR,str(name[:-4]) + '_' + str(epoch))
            # print(str(str(name[:-4]) + '_' + str(epoch)) + '.jpg')
            new_bndbox_list = []
    print('Finish!')


if __name__ == "__main__":

    '''
    workfolder
        ---src_img_dir
        ---new_img_dir
        ---cut_pad.py
    '''

    #TODO filename set
    IMG_DIR = "image"
    XML_DIR = "voc_annotation"
    AUG_XML_DIR = "augvoc/"
    AUG_IMG_DIR = "augimg/" 
    AUGLOOP = 1
    

    #TODO augmentation rule & style
    seq = iaa.Sequential([
        iaa.Fliplr(0.5), 
        iaa.Affine(translate_px={"x": 15, "y": 15},scale=(0.8, 0.95),),
        iaa.CoarseSaltAndPepper(0.05, size_percent=(0.01, 0.1)),
        iaa.JpegCompression(compression=(70, 99)),
        iaa.Cutout(nb_iterations=2),
        iaa.Dropout(p=(0, 0.2))  
    ])
    
    aug()

    