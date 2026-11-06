from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch Arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)
    gz_args = LaunchConfiguration('gz_args', default='')

    pkg_this = FindPackageShare("gripper")
    urdf_file = PathJoinSubstitution([pkg_this, "urdf", "test_gripper_mimic_joint_position.xacro.urdf"])
    robot_description = Command([FindExecutable(name="xacro"), " ", urdf_file])
    config_file = PathJoinSubstitution([pkg_this, "config", "gripper_controller_position.yaml"])
    world_file = PathJoinSubstitution([pkg_this, "world", "empty_imu.sdf"])
    rviz_file = PathJoinSubstitution([pkg_this, "rviz", "gripper_position.rviz"])



    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{"robot_description": robot_description, "use_sim_time": True}]
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d",rviz_file]
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', 
                   '-name', 'gripper', 
                   '-allow_renaming', 'true'],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'gripper_controller',
            '--param-file',
            config_file,
            ],
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    world_file = IncludeLaunchDescription(PythonLaunchDescriptionSource([PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])]),
                launch_arguments=[('gz_args', [gz_args, " -r -v 1 ", world_file])])

    return LaunchDescription([
        gz_spawn_entity,
        world_file,
        joint_state_broadcaster_spawner,
        gripper_controller_spawner,
        rviz_node,
        bridge,
        node_robot_state_publisher,
    ])
