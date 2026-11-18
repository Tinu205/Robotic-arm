import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'arm_description'
    rjr = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name),'launch','rjr.launch.py'
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
            launch_arguments={'gz_args':['-r -v4',world],'on_exit_shutdown':'true'}.items()
    )

    spawn_entity = Node(package='ros_gz_sim',executable='create',arguments=['-topic','robot_description','-name','my_bot','-z','0.1'],output='screen')

    return LaunchDescription([
        rjr,
        world_arg,
        gazebo,
        spawn_entity,
    ])
