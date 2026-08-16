import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math


class TurtleSquare(Node):

    def __init__(self):
        super().__init__('turtle_square')

        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_subscriber = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )
        self.timer = self.create_timer(0.01, self.timer_callback)

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.pose_received = False

        self.start_x = None
        self.start_y = None
        self.target_theta = None

        self.state = 0

        self.side_length = 3.0     # طول ضلع المربع
        self.linear_speed = 0.8    # سرعة المشي (أبطأ = أدق)
        self.angular_speed = 0.5   # سرعة الدوران (أبطأ = أدق)
        self.angle_tolerance = 0.01

    def pose_callback(self, pose):
        self.x = pose.x
        self.y = pose.y
        self.theta = pose.theta
        self.pose_received = True

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def timer_callback(self):

        if not self.pose_received:
            return

        msg = Twist()

        if self.start_x is None:
            self.start_x = self.x
            self.start_y = self.y

        if self.state == 0:
            distance = math.sqrt(
                (self.x - self.start_x) ** 2 +
                (self.y - self.start_y) ** 2
            )

            if distance < self.side_length:
                msg.linear.x = self.linear_speed
                msg.angular.z = 0.0
            else:
                msg.linear.x = 0.0
                msg.angular.z = 0.0
                self.target_theta = self.normalize_angle(self.theta + math.pi / 2)
                self.state = 1

        elif self.state == 1:
            angle_diff = self.normalize_angle(self.target_theta - self.theta)

            if abs(angle_diff) > self.angle_tolerance:
                msg.linear.x = 0.0
                msg.angular.z = self.angular_speed if angle_diff > 0 else -self.angular_speed
            else:
                msg.linear.x = 0.0
                msg.angular.z = 0.0
                self.start_x = self.x
                self.start_y = self.y
                self.state = 0

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleSquare()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()