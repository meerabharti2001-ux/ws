from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    
    pkg_this = FindPackageShare("ackermann")
    urdf_file = PathJoinSubstitution([pkg_this, "urdf", "test_ackermann_drive.xacro.urdf"])
    robot_description = Command([FindExecutable(name="xacro"), " ", urdf_file])
    config_file = PathJoinSubstitution([pkg_this, "config", "ackermann_drive_controller.yaml"])
    world_file = PathJoinSubstitution([pkg_this, "world", "empty_imu.sdf"])
    rviz_file = PathJoinSubstitution([pkg_this, "rviz", "ackermann.rviz"])

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output='screen',
        arguments=["-d", rviz_file]
    )

    node_robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
            }]
    )

    gz_world_node = IncludeLaunchDescription(PythonLaunchDescriptionSource([PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])]),
            launch_arguments=[('gz_args', [' -r -v 1 ', world_file])])
    
    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', 'robot_description', 
            '-name', 'ackermann', 
            '-allow_renaming', 'true'],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    
    ackermann_steering_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['ackermann_steering_controller','--param-file', config_file,
                   '--controller-ros-args', '-r /ackermann_steering_controller/tf_odometry:=/tf',
                   ],
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    return LaunchDescription([node_robot_state_publisher, rviz_node, bridge, gz_world_node, gz_spawn_entity, joint_state_broadcaster_spawner,
                              ackermann_steering_controller_spawner])
