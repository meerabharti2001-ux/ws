from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_this = FindPackageShare("diffdrive")
    urdf_file = PathJoinSubstitution([pkg_this, "urdf", "diff_drive.xacro.urdf"])
    robot_description = Command([FindExecutable(name='xacro'), " ", urdf_file, " ", "namespace:=r1"])

    config_file = PathJoinSubstitution([pkg_this, "config", "diff_drive_controller.yaml"])
    
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='r1',
        output='screen',
        parameters=[{"robot_description":robot_description}]
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        namespace='r1',
        output='screen',
        arguments=['-topic', 'robot_description', '-name',
                   'diff_drive', '-allow_renaming', 'true'],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '-c', '/r1/controller_manager'
            ],
    )
    diff_drive_base_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_drive_base_controller',
            '--param-file',
            config_file,
            '-c', '/r1/controller_manager'
            ],
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    gz_launch_node = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [PathJoinSubstitution([FindPackageShare('ros_gz_sim'),
                                           'launch',
                                           'gz_sim.launch.py'])]),
                launch_arguments=[('gz_args', [' -r -v 1 empty.sdf'])])

    return LaunchDescription([gz_launch_node, bridge, node_robot_state_publisher, gz_spawn_entity, joint_state_broadcaster_spawner, diff_drive_base_controller_spawner])
