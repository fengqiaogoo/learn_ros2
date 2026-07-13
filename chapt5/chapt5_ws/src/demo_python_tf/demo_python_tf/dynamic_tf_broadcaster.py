import math

# Workaround: patch deprecated np.float for older transforms3d compatibility
import numpy as np

if not hasattr(np, "float"):
    np.float = np.float64

from cv2 import transform
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
from tf_transformations import quaternion_from_euler


class TFBroadcaster(Node):
    def __init__(self):
        super().__init__("tf_broadcaster")
        self.broadcaster_ = TransformBroadcaster(self)
        self.timer_ = self.create_timer(0.01, self.publish_tf)

    def publish_tf(self):
        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = "camera_link"
        transform.child_frame_id = "bottle_link"
        transform.transform.translation.x = 0.2
        transform.transform.translation.y = 0.3
        transform.transform.translation.z = 0.5

        # Convert Euler angles to quaternion
        rotation_quat = quaternion_from_euler(0, 0, 0)
        transform.transform.rotation.x = rotation_quat[0]
        transform.transform.rotation.y = rotation_quat[1]
        transform.transform.rotation.z = rotation_quat[2]
        transform.transform.rotation.w = rotation_quat[3]

        # 发布静态坐标变换
        self.broadcaster_.sendTransform(transform)
        self.get_logger().info(f"TF:{transform}")


def main():
    rclpy.init()
    static_tf_broadcaster = TFBroadcaster()
    rclpy.spin(static_tf_broadcaster)
    rclpy.shutdown()
