import os
import xml.etree.ElementTree as ET
from xml.dom.minidom import Document
import cv2


class YOLO_VOCConvert:
    '''
    为了方便数据集格式的处理,所以实现了数据格式转换，主要有YOLO->VOC和VOC->YOLO
    '''
    def __init__(self, txts_path, xmls_path, imgs_path):
        self.txts_path = txts_path   
        self.xmls_path = xmls_path   
        self.imgs_path = imgs_path   
        self.classes = ['Unripe','Ripe']


    def _search_all_classes(self, writer=False):
        all_names = set()
        txts = os.listdir(self.txts_path)
        txts = [txt for txt in txts if txt.split('.')[-1] == 'txt']
        print(len(txts), txts)
        for txt in txts:
            txt_file = os.path.join(self.txts_path, txt)
            with open(txt_file, 'r') as f:
                objects = f.readlines()
                for object in objects:
                    object = object.strip().split(' ')
                    print(object)
                    all_names.add(int(object[0]))

        print("All labels", all_names, "numofdata:%d" % len(txts))

        return list(all_names)
    
    
    def voc2yolo(self):
        '''
        这个的实现比较简单，主要是归一化处理
        '''
        print('************************Transfer*************************')
        dirpath=self.xmls_path
        newdir=self.txts_path
        dict_info = {}
        for i in len(self.classes):
            dict_info[self.classes[i]]=i
            
        for fp in os.listdir(dirpath):
            if fp.endswith('.xml'):
                root = ET.parse(os.path.join(dirpath, fp)).getroot()

                xmin, ymin, xmax, ymax = 0, 0, 0, 0
                sz = root.find('size')
                width = float(sz[0].text)
                height = float(sz[1].text)
                filename = root.find('filename').text
                for child in root.findall('object'):

                    sub = child.find('bndbox') 
                    label = child.find('name').text
                    label_ = dict_info.get(label)
                    if label_:
                        label_ = label_
                    else:
                        label_ = 0
                    xmin = float(sub[0].text)
                    ymin = float(sub[1].text)
                    xmax = float(sub[2].text)
                    ymax = float(sub[3].text)
                    try:
                        x_center = (xmin + xmax) / (2 * width)
                        x_center = '%.6f' % x_center
                        y_center = (ymin + ymax) / (2 * height)
                        y_center = '%.6f' % y_center
                        w = (xmax - xmin) / width
                        w = '%.6f' % w
                        h = (ymax - ymin) / height
                        h = '%.6f' % h
                    except ZeroDivisionError:
                        print(filename, '的 width有问题')
                    with open(os.path.join(newdir, fp.split('.xml')[0] + '.txt'), 'a+') as f:
                        f.write(' '.join([str(label_), str(x_center), str(y_center), str(w), str(h) + '\n']))
        print('************************Transfer Done!*************************')
        
        
        
        
    def yolo2voc(self):
        '''
        这里比较复杂，主要是需要理解xml数据格式的组织方式
        '''
        print('************************Transfer*************************')
        if not os.path.exists(self.xmls_path):
            os.mkdir(self.xmls_path)
 
        _imgs = os.listdir(self.imgs_path)
        txts = os.listdir(self.txts_path)
        txts = [txt for txt in txts if not txt.split('.')[0] == "classes"]
        

        imgs=[i for i in _imgs if i[:-3]+'txt' in txts]
        if len(imgs) == len(txts):  
            map_imgs_txts = [(img, txt) for img, txt in zip(imgs, txts)]
            txts = [txt for txt in txts if txt.split('.')[-1] == 'txt']
            print(len(txts), txts)
            for img_name, txt_name in map_imgs_txts:
                print("-->Reading img:", img_name)
                img = cv2.imread(os.path.join(self.imgs_path, img_name))
                height_img, width_img, depth_img = img.shape
                print("-->Image shape:", height_img, width_img, depth_img)

        
                all_objects = []
                txt_file = os.path.join(self.txts_path, txt_name)
                with open(txt_file, 'r') as f:
                    objects = f.readlines()
                    for object in objects:
                        object = object.strip().split(' ')
                        all_objects.append(object)
                        print(object) 

                # 创建xml标签文件中的标签
                xmlBuilder = Document()
                # 创建annotation标签，也是根标签
                annotation = xmlBuilder.createElement("annotation")

                # 给标签annotation添加一个子标签
                xmlBuilder.appendChild(annotation)

                # 创建子标签folder
                folder = xmlBuilder.createElement("folder")
                # 给子标签folder中存入内容，folder标签中的内容是存放图片的文件夹，例如：JPEGImages
                folderContent = xmlBuilder.createTextNode(self.imgs_path.split('/')[-1])  # 标签内存
                folder.appendChild(folderContent)  # 把内容存入标签
                annotation.appendChild(folder)   # 把存好内容的folder标签放到 annotation根标签下

                # 创建子标签filename
                filename = xmlBuilder.createElement("filename")
                # 给子标签filename中存入内容，filename标签中的内容是图片的名字，例如：000250.jpg
                filenameContent = xmlBuilder.createTextNode(txt_name.split('.')[0] + '.jpg')  # 标签内容
                filename.appendChild(filenameContent)
                annotation.appendChild(filename)

                # 把图片的shape存入xml标签中
                size = xmlBuilder.createElement("size")
                # 给size标签创建子标签width
                width = xmlBuilder.createElement("width")  # size子标签width
                widthContent = xmlBuilder.createTextNode(str(width_img))
                width.appendChild(widthContent)
                size.appendChild(width)   # 把width添加为size的子标签
                # 给size标签创建子标签height
                height = xmlBuilder.createElement("height")  # size子标签height
                heightContent = xmlBuilder.createTextNode(str(height_img))  # xml标签中存入的内容都是字符串
                height.appendChild(heightContent)
                size.appendChild(height)  # 把width添加为size的子标签
                # 给size标签创建子标签depth
                depth = xmlBuilder.createElement("depth")  # size子标签width
                depthContent = xmlBuilder.createTextNode(str(depth_img))
                depth.appendChild(depthContent)
                size.appendChild(depth)  # 把width添加为size的子标签
                annotation.appendChild(size)   # 把size添加为annotation的子标签

                # 每一个object中存储的都是['0', '0.506667', '0.553333', '0.490667', '0.658667']一个标注目标
                for object_info in all_objects:
                    # 开始创建标注目标的label信息的标签
                    object = xmlBuilder.createElement("object")  # 创建object标签
                    # 创建label类别标签
                    # 创建name标签
                    imgName = xmlBuilder.createElement("name")  # 创建name标签
                    imgNameContent = xmlBuilder.createTextNode(self.classes[int(object_info[0])])
                    imgName.appendChild(imgNameContent)
                    object.appendChild(imgName)  # 把name添加为object的子标签

                    # 创建pose标签
                    pose = xmlBuilder.createElement("pose")
                    poseContent = xmlBuilder.createTextNode("Unspecified")
                    pose.appendChild(poseContent)
                    object.appendChild(pose)  # 把pose添加为object的标签

                    # 创建truncated标签
                    truncated = xmlBuilder.createElement("truncated")
                    truncatedContent = xmlBuilder.createTextNode("0")
                    truncated.appendChild(truncatedContent)
                    object.appendChild(truncated)

                    # 创建difficult标签
                    difficult = xmlBuilder.createElement("difficult")
                    difficultContent = xmlBuilder.createTextNode("0")
                    difficult.appendChild(difficultContent)
                    object.appendChild(difficult)

                    # 先转换一下坐标
                    # (objx_center, objy_center, obj_width, obj_height)->(xmin，ymin, xmax,ymax)
                    x_center = float(object_info[1])*width_img + 1
                    y_center = float(object_info[2])*height_img + 1
                    xminVal = int(x_center - 0.5*float(object_info[3])*width_img)   # object_info列表中的元素都是字符串类型
                    yminVal = int(y_center - 0.5*float(object_info[4])*height_img)
                    xmaxVal = int(x_center + 0.5*float(object_info[3])*width_img)
                    ymaxVal = int(y_center + 0.5*float(object_info[4])*height_img)

                    # 创建bndbox标签(三级标签)
                    bndbox = xmlBuilder.createElement("bndbox")
                    # 在bndbox标签下再创建四个子标签(xmin，ymin, xmax,ymax) 即标注物体的坐标和宽高信息
                    # 在voc格式中，标注信息：左上角坐标(xmin, ymin) (xmax, ymax)右下角坐标
                    # 1、创建xmin标签
                    xmin = xmlBuilder.createElement("xmin")  # 创建xmin标签（四级标签）
                    xminContent = xmlBuilder.createTextNode(str(xminVal))
                    xmin.appendChild(xminContent)
                    bndbox.appendChild(xmin)
                    # 2、创建ymin标签
                    ymin = xmlBuilder.createElement("ymin")  # 创建ymin标签（四级标签）
                    yminContent = xmlBuilder.createTextNode(str(yminVal))
                    ymin.appendChild(yminContent)
                    bndbox.appendChild(ymin)
                    # 3、创建xmax标签
                    xmax = xmlBuilder.createElement("xmax")  # 创建xmax标签（四级标签）
                    xmaxContent = xmlBuilder.createTextNode(str(xmaxVal))
                    xmax.appendChild(xmaxContent)
                    bndbox.appendChild(xmax)
                    # 4、创建ymax标签
                    ymax = xmlBuilder.createElement("ymax")  # 创建ymax标签（四级标签）
                    ymaxContent = xmlBuilder.createTextNode(str(ymaxVal))
                    ymax.appendChild(ymaxContent)
                    bndbox.appendChild(ymax)

                    object.appendChild(bndbox)
                    annotation.appendChild(object)  # 把object添加为annotation的子标签
                f = open(os.path.join(self.xmls_path, txt_name.split('.')[0]+'.xml'), 'w')
                xmlBuilder.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')
                f.close()
        print('************************Transfer Done!*************************')




if __name__ == '__main__':
    txts_path1 = './labels/'
    xmls_path1 = './xml/'
    imgs_path1 = './images/'

    yolo2voc_obj1 = YOLO_VOCConvert(txts_path1, xmls_path1, imgs_path1)
    yolo2voc_obj1.yolo2voc()
