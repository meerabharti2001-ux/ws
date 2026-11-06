from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_this = FindPackageShare("mecanum")
    urdf_file = PathJoinSubstitution([pkg_this, "urdf", "test_mecanum_drive.xacro.urdf"])
    robot_description = Command([FindExecutable(name="xacro")," ", urdf_file])
    config_file = PathJoinSubstitution([pkg_this, "config", "mecanum_drive_controller.yaml"])
    rviz_file = PathJoinSubstitution([pkg_this, "rviz", "mecanum.rviz"])
    world_file = PathJoinSubstitution([pkg_this, "world", "empty_imu.sdf"])
    
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{"robot_description": robot_description, "use_sim_time": True}]
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description',
                   '-name', 'mecanum_vehicle', 
                   '-allow_renaming', 'true'],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    mecanum_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'mecanum_drive_controller',
            '--param-file',
            config_file,
            '--controller-ros-args',
            '-r /mecanum_drive_controller/tf_odometry:=/tf',
            ],
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )
    
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_file]
    )

    gz_launch_node =    IncludeLaunchDescription(PythonLaunchDescriptionSource([PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])]),
                launch_arguments=[('gz_args', [' -r -v 1 ', world_file])])

    return LaunchDescription([
        rviz_node,
        gz_spawn_entity,
        gz_launch_node, 
        joint_state_broadcaster_spawner,
        mecanum_drive_controller_spawner,
        bridge,
        node_robot_state_publisher,
    ])
