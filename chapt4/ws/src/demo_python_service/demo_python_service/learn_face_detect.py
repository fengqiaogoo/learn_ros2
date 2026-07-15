import face_recognition
import cv2
from ament_index_python.packages import get_package_share_directory


def main():
    image_path = (
        get_package_share_directory("demo_python_service") + "/resource/images.jpeg"
    )
    image = cv2.imread(image_path)

    # 查找图像中所有人脸
    face_locations = face_recognition.face_locations(image)

    # 绘制每个人脸的边界框
    for top, right, bottom, left in face_locations:
        cv2.rectangle(image, (left, top), (right, bottom), (255, 0, 0), 4)

    # 显示图像
    cv2.imshow("Detected Faces", image)
    cv2.waitKey(0)
