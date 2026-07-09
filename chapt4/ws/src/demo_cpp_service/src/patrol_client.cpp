#include <cstdlib>
#include <ctime>
#include "rclcpp/rclcpp.hpp"
#include "chapt4_interfaces/srv/patrol.hpp"
#include <chrono>

using namespace std::chrono_literals;
using Patrol = chapt4_interfaces::srv::Patrol;

class PatrolClient : public rclcpp::Node
{
public:
      PatrolClient() : Node("patrol_client")
      {
            patrol_client_ = this->create_client<Patrol>("patrol");
            timer_ = this->create_wall_timer(10s, std::bind(&PatrolClient::timer_callback, this));
            srand(time(NULL)); // 初始化随机数种子，使用当前时间作为种子
      }
      void timer_callback()
      {
            while (!patrol_client_->wait_for_service(1s))
            {
                  if (!rclcpp::ok())
                  {
                        RCLCPP_ERROR(this->get_logger(), "Interrupted while waiting for the service. Exiting.");
                        return;
                  }
                  RCLCPP_INFO(this->get_logger(), "Service not available, waiting again...");
            }

            auto request = std::make_shared<Patrol::Request>();
            request->target_x = rand() % 15;
            request->target_y = rand() % 15;
            RCLCPP_INFO(this->get_logger(), "Sending request: target_x=%.2f, target_y=%.2f", request->target_x, request->target_y);

            patrol_client_->async_send_request(request, [&](rclcpp::Client<Patrol>::SharedFuture result_future) -> void
                                               {
                  auto response = result_future.get();
                  if (response->result == Patrol::Response::SUCCESS){
                        RCLCPP_INFO(this->get_logger(), "Patrol successful!");
                  } else {
                        RCLCPP_ERROR(this->get_logger(), "Patrol failed!");
                  } });
      }

private:
      rclcpp::Client<Patrol>::SharedPtr patrol_client_;
      rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv)
{
      rclcpp::init(argc, argv);
      auto node = std::make_shared<PatrolClient>();
      rclcpp::spin(node);
      rclcpp::shutdown();
      return 0;
}