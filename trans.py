# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
import re
from shutil import copyfile

root_path="\\"
srcTxt_path=r"xxml\\"
srcPic_path=r"ximg\\"
output_root_path=r"voc\\"

def prettyXml(element, indent, newline, level = 0): # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
    if element:  # 判断element是否有子元素
        if element.text == None or element.text.isspace(): # 如果element的text没有内容
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
    #else:  # 此处两行如果把注释去掉，Element的text也会另起一行
        #element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
    temp = list(element) # 将elemnt转成list
    for subelement in temp:
        if temp.index(subelement) < (len(temp) - 1): # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
            subelement.tail = newline + indent * (level + 1)
        else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个
            subelement.tail = newline + indent * level
        prettyXml(subelement, indent, newline, level = level + 1) # 对子元素进行递归操作

def PASCAL2VOC():
    if not os.path.exists(output_root_path + srcTxt_path.replace(root_path, '')):
        print("Create a xml dir: " + output_root_path + srcTxt_path.replace(root_path, ''))
        os.makedirs(output_root_path + srcTxt_path.replace(root_path, ''))
    if not os.path.exists(output_root_path + srcPic_path.replace(root_path, '')):
        print("Create a pic dir: " + output_root_path + srcPic_path.replace(root_path, ''))
        os.makedirs(output_root_path + srcPic_path.replace(root_path, ''))

    
    for txt_filename in os.listdir(srcTxt_path):
        if txt_filename.split(".")[-1]=="txt":
            # 创建一个root element<annotation>
            annotation = ET.Element("annotation")
            # 直接通过SubElement类为<annotation>添加多个子元素<folder><filename><path><source><size><segmented><object>
            folder = ET.SubElement(annotation, "folder")
            folder.text = 'Tarin_picture'
            filename = ET.SubElement(annotation, "filename")
            path = ET.SubElement(annotation, "path")
            source = ET.SubElement(annotation, "source")
            database = ET.SubElement(source, "database")
            size = ET.SubElement(annotation, "size")
            width = ET.SubElement(size, "width")
            height = ET.SubElement(size, "height")
            depth = ET.SubElement(size, "depth")
            segmented = ET.SubElement(annotation, "segmented")
            segmented.text = "0"

            with open(srcTxt_path + txt_filename, "r") as file:
                for line in file.readlines():
                    picNameRegex = re.compile(r'Image filename : "(.*)"')
                    mo1 = picNameRegex.search(line)
                    if (mo1 != None):
                        database.text = mo1.group(1).split('/')[0]
                        filename.text = mo1.group(1).split('/')[-1]
                        path.text = srcPic_path + filename.text
                        filename.text = database.text + '_' + filename.text
                    picSizeRegex = re.compile(r'Image size (.*) : (.*) x (.*) x (.*)')
                    mo2 = picSizeRegex.search(line)
                    if (mo2 != None):
                        width.text = mo2.group(2)
                        height.text = mo2.group(3)
                        depth.text = mo2.group(4)
                    if database.text == 'Caltech' or 'VOC2005_1':
                        motorbikeRegex = re.compile(
                            r'Bounding box for object (\d)+ "(PASmotorbikeSide)"(.*) : (.*) - (.*)')
                    if database.text == 'VOC2005_2':
                        motorbikeRegex = re.compile(
                            r'Bounding box for object (\d)+ "(PASmotorbike|PASmotorbikeSide)"(.*) : (.*) - (.*)')
                    if database.text == 'VOC2006':
                        motorbikeRegex = re.compile(
                            r'Bounding box for object (\d)+ "(PASmotorbike|PASmotorbikeLeft|PASmotorbikeRight|PASmotorbikeDifficult|PASmotorbikeTrunc|PASmotorbikeTruncDifficult|PASmotorbikeRear|PASmotorbikeFrontal)"(.*) : (.*) - (.*)')
                    mo3 = motorbikeRegex.findall(line)
                    if (mo3 != None):
                        for obj_in_pic in mo3:
                            object = ET.SubElement(annotation, "object")
                            name = ET.SubElement(object, "name")
                            name.text = obj_in_pic[1]
                            pose = ET.SubElement(object, "pose")
                            pose.text = "Unspecified"
                            struncated = ET.SubElement(object, "struncated")
                            struncated.text = "0"
                            difficult = ET.SubElement(object, "difficult")

                            if ('Difficult' in obj_in_pic[1]):
                                difficult.text = "1"
                            else:
                                difficult.text = "0"
                            bndbox = ET.SubElement(object, "bndbox")
                            xmin = ET.SubElement(bndbox, "xmin")
                            xmin.text = obj_in_pic[3].split('(')[-1].split(',')[0]
                            ymin = ET.SubElement(bndbox, "ymin")
                            ymin.text = obj_in_pic[3].split(' ')[-1].split(')')[0]
                            xmax = ET.SubElement(bndbox, "xmax")
                            xmax.text = obj_in_pic[4].split('(')[-1].split(',')[0]
                            ymax = ET.SubElement(bndbox, "ymax")
                            ymax.text = obj_in_pic[4].split(' ')[-1].split(')')[0]
            prettyXml(annotation, '\t', '\n')
            annotationTree = ET.ElementTree(element=annotation)
            annotationTree.write(output_root_path+ srcTxt_path.replace(root_path, '') + filename.text.split('.')[0]+ ".xml",encoding="utf-8")
            copyfile(path.text, output_root_path + srcPic_path.replace(root_path, '') + filename.text)
if __name__ == "__main__":
    PASCAL2VOC()
