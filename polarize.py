import cv2

def polarize(imagePath='F:/codes/python/NumberRecognition/erdianba.png'):
    image = cv2.imread(imagePath)
    if image.all() != None:
        image = cv2.resize(image, (28, 28))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        cv2.threshold(image, 140, 255, 0, image)
        cv2.imwrite("F:/codes/python/NumberRecognition/afternumerdianba.png",image)
        return image
    else:
        return None
    # 打开窗口显示
    # cv2.namedWindow("Image")
    # cv2.imshow("Image", image)
    # cv2.waitKey(0)

if __name__ == "__main__":
    polarize()
