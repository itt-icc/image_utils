# Author:Youchao Zhang
# Email:matthews@qq.com
# Date:08/1/2021

#  VGG Image Annotator (up to version 1.6) saves each image in the form:
'''
{'filename': '28503151_5b5b7ec140_b.jpg',
 'size': 100202
 'regions': [
     {
         "shape_attributes": {
             "name": "polygon",
             "all_points_x": [],
             "all_points_y":[]
         },
         "region_attributes":{
             "type": "lettuce"
         }

     }, ...
 ],
 "file_attributes": {}
 }
'''

# Labelme
'''
{
    "version": "",
    "flags": {},
    "shapes": [
        {
        "label": "lettuce",
         "points": [[x, y], ...],
         "group_id":null,
         "shape_type":"polygon",
         "flags":{}
         },
        {
        }
        ...
    ],
    "imagePath":"filename.jpg",
    "imageData":"data",
    "imageHeight":480,
    "imageWidth":640
}
'''


import os
import json
def labelme2vir(filename):
    '''
    One labelme dict to one vir dict
    @params:filename:the name of labelme json data
    return :vir : a dict that we need
    NOTE:the size information will loss
    '''
    vir = dict()
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_name=data["imagePath"].split('\\')
        vir["filename"] = data_name[-1]
        vir['size'] = 0
        regions_vir = list()
        regions_lm = data["shapes"]
        regions_lm=sorted(regions_lm,key=lambda x:len(x['points']),reverse=True)
        number_shape_lm = len(regions_lm)
        for item_regions_lm in regions_lm:
            points = item_regions_lm["points"]
            all_points_x = [int(xy[0]) for xy in points]
            all_points_y = [int(xy[1]) for xy in points]
            item_regions_vir = {
                "shape_attributes": {"name": "polygon", "all_points_x": all_points_x, "all_points_y": all_points_y},
                "region_attributes": {"type": "lettuce"}
            }
            regions_vir.append(item_regions_vir)
        vir['regions'] = regions_vir
        vir['file_attributes'] = {}
    return vir

def get_name(name):
    """
    from labelme data name to project name
    """
    item = name.split("-")
    new_name = item[0]+'-'+item[1]+'-'+item[4]+'-'+item[6]
    return new_name

def transfer(path, outputpath):
    '''
    transfer labelme to vir
    '''
    names = os.listdir(path)
    names.sort()
    project_name = list()
    for i in names:
        pro_name = get_name(i)
        if pro_name not in project_name:
            project_name.append(pro_name)

    Project = list()
    for _proname in project_name:
        _project = list()
        for item in names:
            if get_name(item) == _proname:
                _project.append(item)
        Project.append(_project)

    print("All json file:")
    print(*names, sep="\n")
    print("END\n")
    print("All project_name:")
    print(*project_name, sep="_json.json\n", end="_json.json\n")
    print("END\n")
    print("All project list:")
    print(*Project, sep="\n")
    print("END\n")

    print("**************************start to transfer!!**************************")
    for pro, proname in zip(Project, project_name):
        cur_pro = {}
        for item in pro:
            cur_item = labelme2vir(path+'\\'+item)
            cur_pro[item] = cur_item
        with open(outputpath+'\\'+proname+'_json.json', 'w', encoding='utf-8') as f:
            json.dump(cur_pro, f)
            print(proname+'_json.json done!')
    print("**************************  transfer done !!**************************")


if __name__ == '__main__':
    inputpath = r'.\input'
    outputpath = r'.\output2'
    transfer(inputpath, outputpath)
