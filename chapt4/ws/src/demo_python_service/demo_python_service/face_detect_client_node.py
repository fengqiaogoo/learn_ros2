import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from chapt4_interfaces.srv import FaceDetector
from ament_index_python.packages import get_package_share_directory
import cv2

from cv_bridge import CvBridge


class FaceDetectorClient(Node):
    def __init__(self):
        super().__init__("face_detect_client")
        self.client = self.create_client(FaceDetector, "/face_detect")
        self.bridge = CvBridge()
        self.image_path = (
            get_package_share_directory("demo_python_service") + "/resource/test1.jpg"
        )
        self.image = cv2.imread(self.image_path)

    def send_request(self):
        # 判断服务是否上线
        while self.client.wait_for_service(timeout_sec=1.0) is False:
            self.get_logger().info("service not available, waiting again...")
        request = FaceDetector.Request()
        request.image = self.bridge.cv2_to_imgmsg(self.image)
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        response = future.result()
        self.get_logger().info(
            "Received response: number of faces detected: %d" % response.number
        )
        self.show_face_locations(response)

    def show_face_locations(self, response):
        for i in range(response.number):
            top = response.top[i]
            right = response.right[i]
            bottom = response.bottom[i]
            left = response.left[i]
            cv2.rectangle(self.image, (left, top), (right, bottom), (0, 255, 0), 2)
        output_path = (
            get_package_share_directory("demo_python_service") + "/resource/result.jpg"
        )
        cv2.imwrite(output_path, self.image)
        self.get_logger().info(f"Result saved to: {output_path}")


def main(args=None):
    rclpy.init(args=args)
    face_detect_client = FaceDetectorClient()
    face_detect_client.send_request()
    rclpy.shutdown()
