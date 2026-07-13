#include <memory>
#include "geometry_msgs/msg/transform_stamped.hpp" // 提供消息接口
#include "rclcpp/rclcpp.hpp"
#include "tf2/LinearMath/Quaternion.h"             // 提供tf2::Quaternion类
#include "tf2/utils.h"                             // 提供tf2::getEulerYPR函数
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp" // 提供消息类型转换函数
#include "tf2_ros/buffer.h"                        // 提供TF缓冲类Buffer
#include "tf2_ros/transform_listener.h"            // 提供坐标监听器类
#include <chrono>                                  // 引入时间相关头文件

using namespace std::chrono_literals;

class TFListener : public rclcpp::Node
{
private:
      std::shared_ptr<tf2_ros::Buffer> buffer_;
      std::shared_ptr<tf2_ros::TransformListener> listener_;
      rclcpp::TimerBase::SharedPtr timer_;

public:
      TFListener() : Node("tf_listener")
      {
            buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
            listener_ = std::make_shared<tf2_ros::TransformListener>(*buffer_, this);
            timer_ = this->create_wall_timer(5s, std::bind(&TFListener::getTransfrom, this));
      }

      void getTransform()
      {
            try
            {
                  const auto transform = buffer_->lookupTransform(
                      "base_link", "target_point", this->get_clock()->now(),
                      rclcpp::Duration::from_seconds(1.0f));

                  const auto &translation = transform.transform.translation;
                  const auto &rotation = transform.transform.rotation;
                  double yaw, pitch, roll;
                  tf2::getEulerYPR(rotation, yaw, pitch, roll); // 四元数转欧拉角
            }
            catch (tf2::TransformException &ex)
            {
                  RCLCPP_WARN(get_logger(), "Exception: %s", ex.what());
            }
      }
};

int main(int argc, char **argv)
{
      rclcpp::init(argc, argv);
      auto node = std::make_shared<TFListener>();
      rclcpp::spin(node);
      rclcpp::shutdown();
      return 0;
}