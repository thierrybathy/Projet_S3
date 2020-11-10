import principal_1_position
import principal_2_rotate
import principal_3_cut
import principal_4_resize
import cnn_predict
import cv2
import glob as gb
import os
import numpy as np

# the input(the original map) path
LOAD_PATH = "./source/part2_Mr_clair.tif"
if __name__ == '__main__':
    # location
    save_detected_path = './result/principal_1_detected_images_to_rotate'
    save_cut_path = './result/principal_3_cut_images_to_resize'
    # get the position information of the numbers, save the postion into the bounding_box_list
    bounding_box_list, image = principal_1_position.location(LOAD_PATH)

    # Delete all existing .png files
    img_path = gb.glob(save_detected_path + '/*.png')
    for img_file in img_path:
        os.remove(img_file)
    if not os.path.exists(save_detected_path):
        os.mkdir(save_detected_path)
    print("save images, there are ", len(bounding_box_list), "images in total.")
    # Save all detected targets as .png file
    res = []
    # process the single digit
    for i, bounding_box in enumerate(bounding_box_list):
        [intX, intY, intW, intH] = bounding_box
        # img_bin #image #blur #img_bino
        nom = save_detected_path + '/_' + str(i) + '.png'
        top = intY - 2 if (intY - 2) > 0 else intY
        bottom = intY + intH + 2 if (intY + intH + 2) < image.shape[0] else intY + intH
        left = intX - 2 if (intX - 2) > 0 else intX
        right = intX + intW + 2 if (intX + intW + 2) < image.shape[1] else intX + intW
        img_data = image[top: bottom, left: right]
        # save the postion information as a tuple
        position = (top, bottom, left, right)
        cv2.imwrite(nom, img_data, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        print("save ", i, " image")

        img_detected = cv2.cvtColor(img_data, cv2.COLOR_GRAY2BGR)
        name = str(i)
        # rotate the cropped image
        img_rotated = principal_2_rotate.rotate_number_string(img_detected, '_' + name)
        # segment number, store the single digit to imgCut_list and recognize if there is the dicimal point
      
        imgCut_list, dot_flag = principal_3_cut.cut(img_rotated, name)
        # Save cut images
        label = ""
        # the initial confidence is 1, confidence_total = confidence[1]*confidence[2].....
        初始置信度设置为1，总置信度 = 各个数字置信度的乘积
        confidence_total = 1
        for j, img in enumerate(imgCut_list):
            nom = save_cut_path + '/' + str(name) + '_' + str(j + 1) + '_A.png'
            cv2.imwrite(nom, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            img_cut = img
            # resize the cropped images
            img_resized = principal_4_resize.resize_digits(img_cut, name)
            # input the CNN network to get the predict_value and the confidence
            current_label, confidence = cnn_predict.recognize(img_resized)
            confidence_total = confidence_total * confidence
            if current_label == 'A':
                label = 'A'
                break
            label = label + current_label
        if label != 'A' and dot_flag:
            label = int(label) / 10.0
        res.append((position, label, confidence_total))
        
        # check the resule, the image has prediction_value and its confidence
    
        cv2.namedWindow(str(label) + " confidence: " + str(confidence), 0)
        cv2.resizeWindow(str(label) + " confidence: " + str(confidence), 500, 500)
        cv2.imshow(str(label) + " confidence: " + str(confidence), img_data)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # save all information
    res = np.array(res)
    print(res)
    np.save("./result/final.npy", res)


