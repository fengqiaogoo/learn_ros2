import rclpy
from rclpy.node import Node
from chapt4_interfaces.srv import FaceDetector
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
import cv2
import face_recognition
import time


class FaceDetectNode(Node):
    def __init__(self):
        super().__init__("face_detect_node")
        self.bridge = CvBridge()
        self.service = self.create_service(
            FaceDetector, "/face_detect", self.detect_face_callback
        )
        self.image_path = (
            get_package_share_directory("demo_python_service") + "/resource/images.jpeg"
        )

    def detect_face_callback(self, request, response):
        if request.image.data:
            cv_image = self.bridge.imgmsg_to_cv2(request.image)
        else:
            cv_image = cv2.imread(self.image_path)
        start_time = time.time()
        self.get_logger().info("Detecting faces...")
        face_locations = face_recognition.face_locations(cv_image)
        end_time = time.time()
        self.get_logger().info(
            f"Face detection took {end_time - start_time:.2f} seconds."
        )
        response.number = len(face_locations)
        response.use_time = end_time - start_time
        for i, (top, right, bottom, left) in enumerate(face_locations):
            response.top.append(top)
            response.right.append(right)
            response.bottom.append(bottom)
            response.left.append(left)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = FaceDetectNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
