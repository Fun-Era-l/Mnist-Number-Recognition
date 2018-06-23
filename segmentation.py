import cv2
import numpy as np
import converse

def segment(imPath=r'F:\codes\python\NumberRecognition\erdianwu.png'):
    img = cv2.imread(imPath, 0)


    # 自定义灰度方法
    # grayimg = np.zeros(img.shape,dtype=np.float32)
    # for i,r in enumerate(img):
    #     for j,c in enumerate(r):
    #         grayimg[i, j] = min(img[i, j][0], img[i, j][1], img[i, j][2])
    # cv2.imshow('srcImage', img)
    # # cv2.imshow('grayImage', grayimg)
    # cv2.waitKey(0)
    # for r in img:
    #     print(r)
    #     print('\n')
    # 灰度极化
    # cv2.imshow("contours", img)
    # cv2.waitKey(0)
    # basic = [0,70,144,200]
    # cv2.threshold(img,70,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU,img)

    # converse 将黑白颜色反转
    cv2.imshow('srcImage', img)
    # cv2.imshow('grayImage', grayimg)
    cv2.waitKey(0)

    img = converse.converse(img)

    cv2.imshow('srcImage', img)
    # cv2.imshow('grayImage', grayimg)
    cv2.waitKey(0)
    # 区域分割,提取字符到contours中
    image, contours, hier = cv2.findContours(img, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
    cv2.imshow("contours", img)
    cv2.waitKey(0)
    d=0
    for index,ctr in enumerate(contours):
        # if(index != 1  and index<3):
        # Get bounding box
        x, y, w, h = cv2.boundingRect(ctr)
            # Getting ROI
        roi = image[y:y+h, x:x+w]
        cv2.imshow('character: %d'%d,roi)
        print(type(roi))
        cv2.imwrite('character_%d.png'%d, roi)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        d+=1

if __name__ == '__main__':
        segment()