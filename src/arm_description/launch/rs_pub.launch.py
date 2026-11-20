import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    effort_mode = LaunchConfiguration('effort_mode')

    pkg_path = os.path.join(get_package_share_directory('arm_description'))
    xacro_file = os.path.join(pkg_path,'urdf','robot.urdf.xacro')

    # xacro runs when the launch actually starts (Command substitution), so it can
    # see launch argument values. Calling xacro.process_file() directly here would
    # run before arguments are resolved and always use the xacro defaults.
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' effort_mode:=', effort_mode]),
        value_type=str
    )

    rviz_config_path = os.path.join(get_package_share_directory('arm_description'),'rviz','config.rviz')

    params = {'robot_description':robot_description,'use_sim_time':use_sim_time}
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # No joint_state_publisher_gui here: in simulation the joint_state_broadcaster
    # publishes /joint_states. Two publishers on that topic make the robot flicker.
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d',rviz_config_path],
        parameters=[{'use_sim_time':use_sim_time}]
    )


    # Launch!
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use sim time if true'),

        DeclareLaunchArgument(
            'effort_mode',
            default_value='false',
            description='true: effort command interfaces, false: position'),

        robot_state_publisher_node,
        rviz_node
    ])
