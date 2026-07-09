#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "turtlesim/msg/pose.hpp"
#include "chapt4_interfaces/srv/patrol.hpp"
using Patrol = chapt4_interfaces::srv::Patrol;

class TurtleController : public rclcpp::Node
{
private:
      rclcpp::Service<Patrol>::SharedPtr patrol_service_;
      rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_subscription_;
      rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr velocity_publisher_;
      double target_x_{1.0};
      double target_y_{1.0};
      double k_{1.0};
      double max_speed_{3.0};

public:
      TurtleController() : Node("turtle_controller")
      {
            patrol_service_ = this->create_service<Patrol>("patrol", [&](const Patrol::Request::SharedPtr request, Patrol::Response::SharedPtr response) -> void
                                                           {
                  if(
                        (0<request->target_x && request->target_x<12.0f) &&
                        (0<request->target_y && request->target_y<12.0f)
                  ){
                     this->target_x_ = request->target_x;
                  this->target_y_ = request->target_y;
                  response->result = Patrol::Response::SUCCESS;
                  }else{

                     response->result = Patrol::Response::FAIL;
                  } });
            pose_subscription_ = this->create_subscription<turtlesim::msg::Pose>("turtle1/pose", 10, std::bind(&TurtleController::on_pose_received_, this, std::placeholders::_1));
            velocity_publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);
      }

private:
      void on_pose_received_(const turtlesim::msg::Pose::SharedPtr pose)
      {
            // TODO: 收到位置计算误差，发布速度指令
            auto current_x = pose->x;
            auto current_y = pose->y;
            RCLCPP_INFO(get_logger(), "current x:%f,y:%f", current_x, current_y);

            auto distance = std::sqrt((target_x_ - current_x) * (target_x_ - current_x) + (target_y_ - current_y) * (target_y_ - current_y));
            auto angle = std::atan2((target_y_ - current_y), (target_x_ - current_x)) - pose->theta;
            auto msg = geometry_msgs::msg::Twist();
            if (distance > 0.1)
            {
                  if (fabs(angle) > 0.2)
                  {
                        msg.angular.z = fabs(angle);
                  }
                  else
                  {
                        msg.linear.x = k_ * distance;
                  }
            }

            if (msg.linear.x > max_speed_)
            {
                  msg.linear.x = max_speed_;
            }
            velocity_publisher_->publish(msg);
      }
};

int main(int argc, char **argv)
{
      rclcpp::init(argc, argv);
      auto node = std::make_shared<TurtleController>();
      rclcpp::spin(node);
      rclcpp::shutdown();
      return 0;
}