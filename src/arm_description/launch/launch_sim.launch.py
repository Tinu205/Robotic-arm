import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'arm_description'
    rs_pub = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name),'launch','rs_pub.launch.py'
        )]),launch_arguments={'use_sim_time':'true'}.items()
    )

    world = LaunchConfiguration('world')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='world to load'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'),'launch','gz_sim.launch.py')]),
            launch_arguments={'gz_args':['-r -v4 ',world],'on_exit_shutdown':'true'}.items()
    )

    spawn_entity = Node(package='ros_gz_sim',executable='create',arguments=['-topic','robot_description','-name','my_bot','-z','0.1'],output='screen')

    # Gazebo and ROS 2 use different middleware. Bridge the sim clock one way, Gazebo -> ROS ('[').
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    # The controller manager lives inside Gazebo (gz_ros2_control plugin), so it only
    # exists after the robot is spawned. Chain: spawn -> broadcaster -> trajectory controller.
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen'
    )

    start_broadcaster_after_spawn = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner]
        )
    )

    start_jtc_after_broadcaster = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[joint_trajectory_controller_spawner]
        )
    )

    return LaunchDescription([
        world_arg,
        rs_pub,
        gazebo,
        clock_bridge,
        spawn_entity,
        start_broadcaster_after_spawn,
        start_jtc_after_broadcaster,
    ])
