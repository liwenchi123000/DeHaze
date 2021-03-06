import numpy as np
import json
import cv2 as cv


def imgShow(img):
    cv.namedWindow('img', cv.WINDOW_AUTOSIZE)
    cv.imshow('img', img)
    cv.waitKey(0)


def calculate_J(ori_img, airlight, Rough_T):
    (x, y) = Rough_T.shape
    temp_ori_img = ori_img.astype(np.int16)
    for i in range(3):
        temp_ori_img[:, :, i] = ((temp_ori_img[:,:,i] - airlight[i]) / Rough_T) + airlight[i]
    temp_ori_img[temp_ori_img < 0] = 0
    temp_ori_img[temp_ori_img > 255] = 255
    return temp_ori_img.astype(np.uint8)


def getRough_T(J_D, omg=0.98):
    Rough_T = np.zeros(J_D.shape, np.float32)
    Rough_T = J_D / 255
    Rough_T = (1 - Rough_T)*omg
    Rough_T[Rough_T<0.05] = 0.05
    return Rough_T


def getAirlight(J_D, ori_img):
    (x, y) = J_D.shape
    num = x*y // 1000
    # arr = [[-1,-1,-1]]
    arr = []
    for i in range(x):
        for j in range(y):
            arr.append([i,j,J_D[i][j]])
    arr = sorted(arr, key=lambda x:x[2], reverse=True)
    arr = arr[0:num]
    # heapsort.topKMaxValue(arr, num)
    sum_b = 0
    sum_g = 0
    sum_r = 0
    for i in arr:
        if i[0] != -1:
            sum_b += ori_img[i[0]][i[1]][0]
            sum_g += ori_img[i[0]][i[1]][1]
            sum_r += ori_img[i[0]][i[1]][2]
    return (sum_b//num, sum_g//num, sum_r//num)


def getDarkChannelImage(ori_img, windowsize=3):
    return cv.erode(np.min(ori_img, 2), cv.getStructuringElement(cv.MORPH_RECT, (windowsize, windowsize)))


def dehaze(ori_img):
    J_D = getDarkChannelImage(ori_img)
    imgShow(J_D)
    airlight = getAirlight(J_D, ori_img)
    # print(airlight)
    Rough_T = getRough_T(J_D)
    # imgShow(Rough_T)
    res = calculate_J(ori_img, airlight, Rough_T)
    # imgShow(res)
    return res


if __name__ == '__main__':
    original_image = cv.imread('./assert/im8.jpg')
    # print(original_image)
    res = dehaze(original_image)
    cv.imwrite('./ans3.jpg', res)