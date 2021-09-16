
import os
import re
import xml.etree.ElementTree as ET
from PIL import Image
import random


def img4to1(image_names):
    # image_names 是一个含有四个图片名的list
    to_image = Image.new('RGB', (IMAGE_COLUMN * IMAGE_SIZE, IMAGE_ROW * IMAGE_SIZE))
    for y in range(1, IMAGE_ROW + 1):
        for x in range(1, IMAGE_COLUMN + 1):
            from_image = Image.open(allimgreadpath + image_names[IMAGE_COLUMN * (y - 1) + x - 1]).resize((IMAGE_SIZE, IMAGE_SIZE), Image.ANTIALIAS)
            to_image.paste(from_image, ((x - 1) * IMAGE_SIZE, (y - 1) * IMAGE_SIZE))
    to_image.save(ximgwritepath + 'ximg' + str(NUM) + '.jpg')
    return 'ximg' + str(NUM) + '.jpg'


def xml4to1(image_names, xxmlname):
    f_test = open(xxmlwritepath + xxmlname.split('.')[-2] + '.xml', 'w')
    f_test.write('<annotation>\n')
    f_test.write('	<folder>' + ximgwritepath + '</folder>\n')
    f_test.write('	<filename>' + xxmlname + '</filename>\n')
    f_test.write('	<size>\n')
    f_test.write('		<width>' + str(IMAGE_COLUMN * IMAGE_SIZE) + '</width>\n')
    f_test.write('		<height>' + str(IMAGE_ROW * IMAGE_SIZE) + '</height>\n')
    f_test.write('		<depth>' + str(3) + '</depth>\n')
    f_test.write('	</size>\n')

    for i in range(len(image_names)):
        if i == 0:
            img = Image.open(allimgreadpath + image_names[i])
            width, height = img.size
            scalewidth = IMAGE_SIZE / width
            scaleheight = IMAGE_SIZE / height

            text = open(allxmlreadpath + image_names[i].split('.')[-2] + '.xml').read()
            text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u"", text)
            root = ET.fromstring(text)

            if root.findall('object') == []:
                print("no object filename:", image_names[i])
            else:
                for object in root.findall('object'):
                    label = object.findtext('name')
                    x1 = object.findtext('bndbox/xmin')
                    y1 = object.findtext('bndbox/ymin')
                    x2 = object.findtext('bndbox/xmax')
                    y2 = object.findtext('bndbox/ymax')

                    newx1 = int(int(x1) * scalewidth)
                    newy1 = int(int(y1) * scaleheight)
                    newx2 = int(int(x2) * scalewidth)
                    newy2 = int(int(y2) * scaleheight)

                    # if (newx2-newx1)>MINISCALE and (newy2-newy1)>MINISCALE:
                    if (newy2 - newy1) > MINISCALE:
                        f_test.write('	<object>\n')
                        f_test.write('		<name>' + label + '</name>\n')
                        f_test.write('		<bndbox>\n')
                        f_test.write('			<xmin>' + str(newx1) + '</xmin>\n')
                        f_test.write('			<ymin>' + str(newy1) + '</ymin>\n')
                        f_test.write('			<xmax>' + str(newx2) + '</xmax>\n')
                        f_test.write('			<ymax>' + str(newy2) + '</ymax>\n')
                        f_test.write('		</bndbox>\n')
                        f_test.write('	</object>\n')
                    else:
                        continue

        elif i == 1:
            img = Image.open(allimgreadpath + image_names[i])
            width, height = img.size
            scalewidth = IMAGE_SIZE / width
            scaleheight = IMAGE_SIZE / height

            text = open(allxmlreadpath + image_names[i].split('.')[-2] + '.xml').read()
            text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u"", text)
            root = ET.fromstring(text)

            if root.findall('object') == []:
                print("no object filename:", image_names[i])
            else:
                for object in root.findall('object'):
                    label = object.findtext('name')
                    x1 = object.findtext('bndbox/xmin')
                    y1 = object.findtext('bndbox/ymin')
                    x2 = object.findtext('bndbox/xmax')
                    y2 = object.findtext('bndbox/ymax')

                    newx1 = int(int(x1) * scalewidth)
                    newy1 = int(int(y1) * scaleheight)
                    newx2 = int(int(x2) * scalewidth)
                    newy2 = int(int(y2) * scaleheight)

                    # if (newx2-newx1)>MINISCALE and (newy2-newy1)>MINISCALE:
                    if (newy2 - newy1) > MINISCALE:
                        f_test.write('	<object>\n')
                        f_test.write('		<name>' + label + '</name>\n')
                        f_test.write('		<bndbox>\n')
                        f_test.write('			<xmin>' + str(IMAGE_SIZE + newx1) + '</xmin>\n')
                        f_test.write('			<ymin>' + str(newy1) + '</ymin>\n')
                        f_test.write('			<xmax>' + str(IMAGE_SIZE + newx2) + '</xmax>\n')
                        f_test.write('			<ymax>' + str(newy2) + '</ymax>\n')
                        f_test.write('		</bndbox>\n')
                        f_test.write('	</object>\n')
                    else:
                        continue

        elif i == 2:
            img = Image.open(allimgreadpath + image_names[i])
            width, height = img.size
            scalewidth = IMAGE_SIZE / width
            scaleheight = IMAGE_SIZE / height

            text = open(allxmlreadpath + image_names[i].split('.')[-2] + '.xml').read()
            text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u"", text)
            root = ET.fromstring(text)

            if root.findall('object') == []:
                print("no object filename:", image_names[i])
            else:
                for object in root.findall('object'):
                    label = object.findtext('name')
                    x1 = object.findtext('bndbox/xmin')
                    y1 = object.findtext('bndbox/ymin')
                    x2 = object.findtext('bndbox/xmax')
                    y2 = object.findtext('bndbox/ymax')

                    newx1 = int(int(x1) * scalewidth)
                    newy1 = int(int(y1) * scaleheight)
                    newx2 = int(int(x2) * scalewidth)
                    newy2 = int(int(y2) * scaleheight)

                    # if (newx2-newx1)>MINISCALE and (newy2-newy1)>MINISCALE:
                    if (newy2 - newy1) > MINISCALE:
                        f_test.write('	<object>\n')
                        f_test.write('		<name>' + label + '</name>\n')
                        f_test.write('		<bndbox>\n')
                        f_test.write('			<xmin>' + str(newx1) + '</xmin>\n')
                        f_test.write('			<ymin>' + str(IMAGE_SIZE + newy1) + '</ymin>\n')
                        f_test.write('			<xmax>' + str(newx2) + '</xmax>\n')
                        f_test.write('			<ymax>' + str(IMAGE_SIZE + newy2) + '</ymax>\n')
                        f_test.write('		</bndbox>\n')
                        f_test.write('	</object>\n')
                    else:
                        continue

        elif i == 3:
            img = Image.open(allimgreadpath + image_names[i])
            width, height = img.size
            scalewidth = IMAGE_SIZE / width
            scaleheight = IMAGE_SIZE / height

            text = open(allxmlreadpath + image_names[i].split('.')[-2] + '.xml').read()
            text = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u"", text)
            root = ET.fromstring(text)

            if root.findall('object') == []:
                print("no object filename:", image_names[i])
            else:
                for object in root.findall('object'):
                    label = object.findtext('name')
                    x1 = object.findtext('bndbox/xmin')
                    y1 = object.findtext('bndbox/ymin')
                    x2 = object.findtext('bndbox/xmax')
                    y2 = object.findtext('bndbox/ymax')

                    newx1 = int(int(x1) * scalewidth)
                    newy1 = int(int(y1) * scaleheight)
                    newx2 = int(int(x2) * scalewidth)
                    newy2 = int(int(y2) * scaleheight)

                    # if (newx2-newx1)>MINISCALE and (newy2-newy1)>MINISCALE:
                    if (newy2 - newy1) > MINISCALE:
                        f_test.write('	<object>\n')
                        f_test.write('		<name>' + label + '</name>\n')
                        f_test.write('		<bndbox>\n')
                        f_test.write('			<xmin>' + str(IMAGE_SIZE + newx1) + '</xmin>\n')
                        f_test.write('			<ymin>' + str(IMAGE_SIZE + newy1) + '</ymin>\n')
                        f_test.write('			<xmax>' + str(IMAGE_SIZE + newx2) + '</xmax>\n')
                        f_test.write('			<ymax>' + str(IMAGE_SIZE + newy2) + '</ymax>\n')
                        f_test.write('		</bndbox>\n')
                        f_test.write('	</object>\n')
                    else:
                        continue
    f_test.write('</annotation>\n')
    f_test.close()
def read_train_valid():
    file=[]
    with open('trainval.txt', 'r') as f:
        data = f.readlines()
        for item in data:
            file.append(item.strip())
    return file
    
if __name__ == '__main__':
    allimgreadpath = 'image/'         # 原始jpg图片+左右翻转后的jpg图片合并在一起的路径
    ximgwritepath = 'ximg/'            # Mosaic数据增强后的图片路径（每四张图片拼接成一张新的图片）
    allxmlreadpath = 'voc_annotation/'         # 原始xml+左右翻转后的xml合并在一起的路径(对应于allimg)
    xxmlwritepath = 'xxml/'            # Mosaic数据增强后的xml路径（对应于Mosaic数据增强后的图片ximg）
    file = read_train_valid()
    allimgnames_ = os.listdir(allimgreadpath)
    allimgnames=[i for i in allimgnames_ if i[:-4] in file]
    random.shuffle(allimgnames)

    print(allimgnames)
    NUM = 0
    IMAGE_ROW = 2
    IMAGE_COLUMN = 2
    IMAGE_SIZE = 416
    MINISCALE = 1
    for image_names in [allimgnames[i:i + 4] for i in range(0, len(allimgnames), 4)]:
        NUM += 1
        xxmlname = img4to1(image_names)
        print(xxmlname)
        xml4to1(image_names, xxmlname)
