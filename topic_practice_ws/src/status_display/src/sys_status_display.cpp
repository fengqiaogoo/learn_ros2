#include <QApplication>
#include <QLabel>
#include <QString>
#include <memory>
#include <sstream>
#include "rclcpp/rclcpp.hpp"
#include "status_interface/msg/system_status.hpp"

using SystemStatus = status_interface::msg::SystemStatus;

class SysStatusDisplay : public rclcpp::Node
{
      public:
          SysStatusDisplay() : Node("sys_status_display"){
            label_ = new QLabel(get_qstr_from_msg(std::make_shared<SystemStatus>()));
            label_->show();
            subscription_ = this->create_subscription<SystemStatus>(
                  "system_status", 10, [&](const SystemStatus::SharedPtr msg) -> void {
                        label_->setText(get_qstr_from_msg(msg));
                  });
          }
          QString get_qstr_from_msg(const SystemStatus::SharedPtr msg){
            std::stringstream show_str;
            show_str
            << "==========系统状态可视化显示工具==========\n"
            << "data time: \t" << msg->stamp.sec << "\ts\n"
            << "user name: \t" << msg->host_name << "\t\n"
            << "cpu usage: \t" << msg->cpu_percent << "\t%\n"
            << "mem usage: \t" << msg->memory_percent << "\t%\n"
            << "men total: \t" << msg->memory_total << "\tMB\n"
            << "mem free: \t" << msg->memory_available << "\tMB\n"
            << "net sent: \t" << msg->net_sent << "\tMB\n"
            << "net recv: \t" << msg->net_recv << "\tMB\n"
            << "=======================================";
            return QString::fromStdString(show_str.str());
          }
      private:
          rclcpp::Subscription<SystemStatus>::SharedPtr subscription_;
          QLabel *label_;
};

int main(int argc, char* argv[])
{     rclcpp::init(argc, argv);
      QApplication app(argc, argv);
      auto node = std::make_shared<SysStatusDisplay>();
      std::thread spin_thread([&]() -> void {
          rclcpp::spin(node);
      });
      spin_thread.detach();
      app.exec();
      rclcpp::shutdown();
      return 0;
}
