from PIL import Image
import numpy as np
import glob as gb
import copy
import cv2
import os


LENGTH_THRESHOLD, THICKNESS = 15, 5
NUM_SIZE = 14
min_contour_area = 0.05 * NUM_SIZE * NUM_SIZE
max_contour_area = 4 * NUM_SIZE * NUM_SIZE
min_width, max_width = NUM_SIZE - 4, NUM_SIZE * 8
min_height, max_height = NUM_SIZE - 4, NUM_SIZE * 8

# Set path
LOAD_PATH = './result/principal_2_rotated_images_to_cut'
SAVE_PATH = './result/principal_3_cut_images_to_resize'


"""#---------Target Cut----------"""


def front_zero_remove(list_input, remove_num):
    '''
    Remove all zeros at the beginning of a list
    Return the new list and number of zeros be removed
    @author IMT-Atlantique,03/2020
    '''
    if len(list_input) > 0 and list_input[0] <= 3:
        list_input.pop(0)
        remove_num += 1
        return front_zero_remove(list_input, remove_num)
    else:
        return list_input, remove_num


def end_zero_remove(list_input):
    '''
    Remove all small numbers(0-3) at the ending of a list
    Return the new list
    @author IMT-Atlantique,03/2020
    '''
    if len(list_input) > 0 and list_input[-1] <= 3:
        list_input.pop()
        return end_zero_remove(list_input)
    else:
        return list_input


def cut_image(datalist_input, digtal_width, target_to_cutout):
    '''
    Cut images according to digtal_width and target_to_cutout
    Input：
    datalist_input - list, number of black pixels of each column.
    digtal_width - int, width of targets.
    target_to_cutout - int, number of target it should find.
    Output:
    list, the location where suohld make a cut.
    @author IMT-Atlantique,03/2020
    '''

    try_times = 10
    curr_locate = 0
    last_locate = 0
    cut_locate = []
    jump = 0
    dot_flag = False

    data_list_org = copy.deepcopy(datalist_input)
    new_data_list = end_zero_remove(datalist_input)

    while target_to_cutout > 1 and try_times > 0:
        this_remove_num = 0
        new_data_list, this_remove_num = front_zero_remove(new_data_list, this_remove_num)

        if len(new_data_list) > 10:
            new_data_list = new_data_list[2:]

        if len(new_data_list) > 0:
            cut_curr = new_data_list.index(min(new_data_list[0:digtal_width]))
            curr_locate = curr_locate + this_remove_num + cut_curr
        else:
            break

        if len(new_data_list) > 10:
            curr_locate += 2

        if cut_curr >= 3:
            cut_locate.append(curr_locate + 1)
            new_data_list = data_list_org[curr_locate:]
            target_to_cutout -= 1
            # print(data_list_org[last_locate:curr_locate],new_data_list)
            last_locate = curr_locate
            if jump == 1 and this_remove_num <= 10 and target_to_cutout == 1:
                dot_flag = True
        else:
            jump += 1
            new_data_list = data_list_org[curr_locate:]

        try_times -= 1

    return cut_locate, dot_flag


def target_num_count(img_input):
    tmp_img = cv2.cvtColor(np.array(img_input.convert('RGB')), cv2.COLOR_RGB2BGR)
    h, w = tmp_img.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    dot_flag = False
    color = 1
    numm = 0

    for x in range(w - 1):
        for y in range(h - 1):  #
            if (tmp_img[y, x] == 0).all():
                cv2.floodFill(tmp_img, mask, (x, y), (0, 0, color), cv2.FLOODFILL_MASK_ONLY)  #
                color = color + 50

    color_count = {}

    for x in range(w - 1):
        for y in range(h - 1):
            if (tmp_img[y, x] != 255).any():
                if (tmp_img[y, x][2]) in color_count:
                    color_count[tmp_img[y, x][2]] += 1
                else:
                    color_count[tmp_img[y, x][2]] = 1
                    numm = numm + 1

    # print('Inter-connect area count: ',numm)
    # print(color_count)

    target_num = 0
    for value in color_count.values():
        if 12 <= value <= 27:
            dot_flag = True
            # print('This is like a dot, dot_flag = True')
        elif 30 < value < 500:
            target_num += 1
            # print('This is likely a target!')
        else:
            continue
            # print('This is too large or too small')

    return tmp_img, target_num, dot_flag


def cut_batch():
    # set path
    img_path = gb.glob(SAVE_PATH + '/*.png')
    for img_file in img_path:
        os.remove(img_file)
    if not os.path.exists(SAVE_PATH):
        os.mkdir(SAVE_PATH)
    img_path = gb.glob(LOAD_PATH + '/*.png')
    print(len(img_path))

    '''
    #img_path.sort()
    img_path.sort(key=lambda x: int(x.replace("frame","").split('.')[0]))
    
    img_path[0:10]
    '''

    # Cut all .png in the file
    dot_exist = []
    for id_num in range(len(img_path)):  # enumerate(img_path):
        img_file = LOAD_PATH + '/_' + str(id_num) + '.png'
        # Load the image to be cut
        img_bin3 = cv2.imread(img_file, 0)

        # 连通域计数
        target_width = NUM_SIZE + 2
        img_cut_1 = Image.fromarray(img_bin3)
        tmp_img, target_num_1, dot_flag_1 = target_num_count(img_cut_1)

        # counting non-zero value by column, on Y axis
        # 可以得到字符宽的边界，波形的波谷即间隔
        col_nz = []
        for col in img_bin3.T.tolist():
            col_nz.append(len(col) - col.count(255))

        black_pixel = [x for x in col_nz if x <= 2]
        # target_num_2 = int(round(len(black_pixel)/target_width))
        '''
        #Set the target number
        if target_num_1 == target_num_2:
        target_num_final = target_num_2
        elif target_num_1 > target_num_2:
        target_num_final = target_num_2
        else:
        target_num_final = target_num_2
        '''
        # Cut image by using cut_image function
        list_ToBeCut = copy.deepcopy(col_nz)
        column_boundary_list, dot_flag_2 = cut_image(list_ToBeCut, target_width,
                                                      10)  # Try to cut 10 times for all images!!!

        # Save dot_existence information
        if dot_flag_1 and dot_flag_2:
            dot_exist.append(str(id_num) + '-True')
        else:
            dot_exist.append(str(id_num) + '-False')

        # Prepare to show cuted images
        imgCut_list = []
        column_boundary_list.insert(0, 0)
        column_boundary_list.insert(len(column_boundary_list), len(col_nz))
        xl = [column_boundary_list[i:i + 2] for i in range(0, len(column_boundary_list) - 1, 1)]
        for x in xl:
            imgCut_list.append(img_bin3[:, x[0]:x[1]])

        # del invalid image
        # 删去宽度不大于target_width * 0.6像素的错误图片
        imgCut_list = [x for x in imgCut_list if x.shape[1] > 3]

        # Save cut images
        Save_Flag = False
        for j, img in enumerate(imgCut_list):
            nom = SAVE_PATH + '/' + str(id_num) + '_' + str(j + 1) + '_A.png'
            cv2.imwrite(nom, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            Save_Flag = True

        if Save_Flag:
            print('Image %d done, cut to %d images!' % (id_num, j + 1) + ' dot flag is ' + str(dot_flag_1 or dot_flag_2))
        else:
            print('Image %d done, not be cut!!' % id_num + ' dot flag is ' + str(dot_flag_1 or dot_flag_2))

    # Save the bounding_box_list
    b = np.array(dot_exist)
    np.save(SAVE_PATH + '/../dot_existence_infolist.npy', b)


def cut(image, name):
    '''
    #img_path.sort()
    img_path.sort(key=lambda x: int(x.replace("frame","").split('.')[0]))

    img_path[0:10]
    '''

    # Cut all .png in the file
    dot_exist = []
    id_num = name
    img_bin3 = image

    # connected component count
    target_width = NUM_SIZE + 2
    img_cut_1 = Image.fromarray(img_bin3)
    tmp_img, target_num_1, dot_flag_1 = target_num_count(img_cut_1)

    # counting non-zero value by column, on Y axis
    #can get the width of digit, the valley of the waveform can help us split the digits
    col_nz = []
    for col in img_bin3.T.tolist():
        col_nz.append(len(col) - col.count(255))

    black_pixel = [x for x in col_nz if x <= 2]
    # target_num_2 = int(round(len(black_pixel)/target_width))
    '''
    #Set the target number
    if target_num_1 == target_num_2:
    target_num_final = target_num_2
    elif target_num_1 > target_num_2:
    target_num_final = target_num_2
    else:
    target_num_final = target_num_2
    '''
    # Cut image by using cut_image function
    list_ToBeCut = copy.deepcopy(col_nz)
    column_boundary_list, dot_flag_2 = cut_image(list_ToBeCut, target_width,
                                                  10)  # Try to cut 10 times for all images!!!

    # Save dot_existence information
    if dot_flag_1 and dot_flag_2:
        dot_exist.append(str(id_num) + '-True')
    else:
        dot_exist.append(str(id_num) + '-False')

    # Prepare to show cuted images
    imgCut_list = []
    column_boundary_list.insert(0, 0)
    column_boundary_list.insert(len(column_boundary_list), len(col_nz))
    xl = [column_boundary_list[i:i + 2] for i in range(0, len(column_boundary_list) - 1, 1)]
    for x in xl:
        imgCut_list.append(img_bin3[:, x[0]:x[1]])

    # del invalid image
    # delete the images which the width is less than target_width * 0.6
   
    imgCut_list = [x for x in imgCut_list if x.shape[1] > 6]

    return imgCut_list, dot_flag_2
