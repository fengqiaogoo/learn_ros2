# 导入 ROS2 客户端库 (rclpy)，提供 ROS2 Python 接口的核心功能
import rclpy

# 从 rclpy.node 模块导入 Node 基类，所有 ROS2 节点必须继承它
from rclpy.node import Node

# 从 example_interfaces 包导入 String 消息类型，用于收发标准字符串消息
from example_interfaces.msg import String

# 导入 threading 模块，用于创建独立线程执行语音朗读任务
import threading

# 从 queue 模块导入 Queue（线程安全队列），用于在生产者和消费者线程之间传递数据
from queue import Queue

# 导入 time 模块，用于线程休眠（sleep）
import time

# 导入 espeakng 库，用于中文文本到语音（TTS）的合成与朗读
import espeakng


# 定义 NovelSubNode 类，继承自 rclpy.node.Node，创建一个 ROS2 订阅节点
class NovelSubNode(Node):
    # 构造函数：node_name 参数指定该 ROS2 节点的名称
    def __init__(self, node_name):
        # 调用父类（Node）的构造函数，初始化 ROS2 节点
        super().__init__(node_name)
        # 创建一个线程安全的队列 Queue 实例，用于缓存待朗读的小说文本
        self.novels_queue_ = Queue()
        # 创建一个 ROS2 订阅者（Subscription）：
        #   - 消息类型为 String
        #   - 订阅的主题名为 "novel"
        #   - 收到消息时的回调函数为 self.novel_callback
        #   - QoS 队列深度为 10（最多缓存 10 条未处理消息）
        self.novels_subscriber_ = self.create_subscription(
            String, "novel", self.novel_callback, 10
        )
        # 创建一个后台线程，target=self.speak_thread 指定线程要运行的函数
        self.speech_thread_ = threading.Thread(target=self.speak_thread)
        # 启动后台线程，开始执行 self.speak_thread 函数
        self.speech_thread_.start()

    # 订阅者的回调函数：每当收到 "novel" 主题上的消息时由 ROS2 框架自动调用
    def novel_callback(self, msg):
        # 将消息的文本数据（msg.data）放入队列，等待语音线程消费朗读
        self.novels_queue_.put(msg.data)

    # 语音朗读线程的主函数：循环等待队列中的文本并朗读
    def speak_thread(self):
        # 创建 espeakng.Speaker 实例，用于执行文本转语音
        speaker = espeakng.Speaker()
        # 设置语音为中文（"zh"），使朗读使用中文发音
        speaker.voice = "zh"
        # 循环检查 ROS2 上下文是否仍然有效（节点未被关闭）
        while rclpy.ok():
            # 检查队列中是否有待朗读的文本（队列大小 > 0）
            if self.novels_queue_.qsize() > 0:
                # 从队列中取出一条文本（FIFO 先进先出）
                text = self.novels_queue_.get()
                # 通过 ROS2 日志系统打印当前正在朗读的内容
                self.get_logger().info(f"正在朗读 {text}")
                # 调用 espeakng 的 say 方法开始朗读文本
                speaker.say(text)
                # 调用 wait 方法阻塞等待当前朗读完成后再继续
                speaker.wait()
            # 如果队列为空，没有文本需要朗读
            else:
                # 休眠 1 秒，避免空转忙等待消耗 CPU
                time.sleep(1)


# 程序的入口函数（main），接受可选的命令行参数 args
def main(args=None):
    # 初始化 rclpy 客户端库，必须在创建任何 ROS2 节点之前调用
    rclpy.init(args=args)
    # 创建 NovelSubNode 节点实例，节点名称为 "novel_read"
    node = NovelSubNode("novel_read")
    # 进入 ROS2 事件循环（spin），阻塞等待消息到达并调用回调函数
    rclpy.spin(node)
    # 节点退出后，关闭 rclpy 客户端库，释放资源
    rclpy.shutdown()
