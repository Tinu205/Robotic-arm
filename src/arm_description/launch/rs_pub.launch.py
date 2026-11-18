import os 

from ament_index_python.packages import get_package_share_directory 
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node

import xacro 

def generate_launch_description():
    use_sim_time=LaunchConfiguration('use_sim_time')
    pkg_path = os.path.join(get_package_share_directory('arm_description'))
    xacro_file = os.path.join(pkg_path,'urdf','robot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)

    #rviz_config_path = os.path.join(get_package_share_directory('arm_description'),'rviz','config.rviz')

    params = {'robot_description':robot_description_config.toxml(),'use_sim_time':use_sim_time}
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # Launch!
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),

        robot_state_publisher_node,
        joint_state_publisher_node,
        #rviz_node
    ])
