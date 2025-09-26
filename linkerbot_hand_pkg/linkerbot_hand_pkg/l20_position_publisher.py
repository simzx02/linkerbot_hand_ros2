#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script creates a ROS2 node to publish joint positions for the Linker Hand L20.
It repeatedly sends a command to the '/cb_left_hand_control_cmd' topic,
causing the hand to move to and hold a predefined position.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class L20PositionPublisher(Node):
    """
    A ROS2 node that publishes JointState messages to control the L20 hand.
    """
    def __init__(self):
        # Initialize the node with the name 'l20_position_publisher'
        super().__init__('l20_position_publisher')

        # Define the topic name and message type
        topic_name = '/cb_left_hand_control_cmd'
        
        # Create a publisher
        self.publisher_ = self.create_publisher(JointState, topic_name, 10)

        # Set the publishing rate (in seconds)
        timer_period = 1.0  # 1 message per second (1 Hz)
        
        # Create a timer to call the publish_command method periodically
        self.timer = self.create_timer(timer_period, self.publish_command)

        # Define the target joint positions for the L20 hand
        # This is an array of 20 float values, same as the one-line command.
        self.target_position = [100.0,10.0, 10.0, 10.0, 10.0, #base thumb, 1234 #min 10 (safe close) ,max 250 safe open [0,255]
        255.0, 127.5, 127.5, 127.5, 127.5, #abduction thumb (circle joint), 1234 finger left-right movement: CAREFULL!! Collision happens here easily.
        0.0, 0.0, 0.0, 0.0, 0.0, #thumb opposition(move to center) + reserved
        200.0, 0.0, 50.0, 50.0, 50.0] #tip thumb 1234
        
        '''
        L20: ["Thumb base", "Index base", "Middle base", "Ring base", "Little base", 
        "Thumb abduction", "Index abduction", "Middle abduction", "Ring abduction", "Little abduction", 
        "Thumb opposition",  "Reserved", "Reserved", "Reserved", "Reserved", 
        "Thumb tip", "Index tip", "Middle tip", "Ring tip", "Little tip"]
        
        '''

        self.get_logger().info(f"Publishing to '{topic_name}' every {timer_period} seconds...")

    def publish_command(self):
        """
        Constructs and publishes the JointState message.
        """
        # Create a new JointState message
        msg = JointState()

        # Set the timestamp for the message header
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # Assign the predefined target positions
        # The list must contain exactly 20 elements for the L20 model.
        msg.position = self.target_position

        # Velocity and effort are not required for simple position control,
        # but the fields exist in the message. We can leave them empty.
        msg.velocity = [50.0]*5
        msg.effort = []

        # Publish the message
        self.publisher_.publish(msg)
        
        # Log the published data to the console for verification
        self.get_logger().info(f'Publishing position command: {msg.position}')


def main(args=None):
    """
    The main entry point for the script.
    """
    # Initialize the ROS2 client library
    rclpy.init(args=args)

    try:
        # Create an instance of the publisher node
        position_publisher = L20PositionPublisher()

        # Keep the node running so it can continue publishing
        rclpy.spin(position_publisher)

    except KeyboardInterrupt:
        # This block will be executed when you press Ctrl+C
        pass
    finally:
        # Cleanly destroy the node and shut down rclpy
        position_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

### How to Run the Script
'''
1.  **Save the File:** Save the code above into a file named `l20_position_publisher.py` inside your ROS2 package's scripts directory (e.g., `your_ros2_ws/src/your_package/your_package/`).

2.  **Make it Executable:** Open a terminal, navigate to the directory where you saved the file, and run:
    ```bash
    chmod +x l20_position_publisher.py
    ```

3.  **Build Your Workspace (if needed):** If you added this script to a new package or just created the package, build your workspace from the root (`your_ros2_ws/`).
    ```bash
    colcon build
    ```

4.  **Run the Hand SDK:** In one terminal, make sure your main `linker_hand_sdk` node is running for the L20 hand.
    ```bash
    # From your workspace root
    source install/setup.bash
    ros2 run linker_hand_ros2_sdk linker_hand_sdk --ros-args -p hand_type:=left -p hand_joint:=L20
    ```

5.  **Run the Publisher Script:** In a **new terminal**, source your workspace and run your new script.
    ```bash
    # From your workspace root
    source install/setup.bash
    ros2 run your_package_name l20_position_publisher.py
    
    L20: ["Thumb base", "Index base", "Middle base", "Ring base", "Little base", "Thumb abduction", "Index abduction", 
    "Middle abduction", "Ring abduction", "Little abduction", "Thumb opposition",  "Reserved", "Reserved", "Reserved", "Reserved", 
    "Thumb tip", "Index tip", "Middle tip", "Ring tip", "Little tip"]
    
    '''