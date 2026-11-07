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
    pkg_this = FindPackageShare("cart")
    urdf_file = PathJoinSubstitution([pkg_this, "urdf", "test_cart_velocity.xacro.urdf"])
    robot_description = Command([FindExecutable(name='xacro')," ", urdf_file])
    config_file = PathJoinSubstitution([pkg_this, "config", "cart_controller_velocity.yaml"])
    world_file = PathJoinSubstitution([pkg_this, "world", "empty_imu.sdf"])
    rviz_file = PathJoinSubstitution([pkg_this, "rviz", "cart_velocity.rviz"])

    
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
                   '-name', 'cart', 
                   '-allow_renaming', 'true'],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )
    joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_trajectory_controller',
            '--param-file',
            config_file,
            ],
    )
    imu_sensor_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'imu_sensor_broadcaster',
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

    world_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource([PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])]),
                launch_arguments=[('gz_args', [gz_args, ' -r -v 1 ', world_file])])

    return LaunchDescription([
    world_launch,
    node_robot_state_publisher,
    gz_spawn_entity,
    joint_state_broadcaster_spawner,
    joint_trajectory_controller_spawner,
    imu_sensor_broadcaster_spawner,
    bridge,
])
