from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_this = FindPackageShare("diffdrive")

    urdf_file = PathJoinSubstitution([pkg_this, "urdf", "diff_drive.xacro.urdf"])

    robot_description = Command([FindExecutable(name="xacro"), " ", urdf_file])

    config_file = PathJoinSubstitution([pkg_this, "config", "diff_drive_controller.yaml"])

    world_file = PathJoinSubstitution([pkg_this, "world", "empty_imu.sdf"])

    rviz_file = PathJoinSubstitution([pkg_this, "rviz", "diffdrive.rviz"])

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True
            }
        ]
    )

    # Gazebo
    gz_sim_launch_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            ])
        ]),
        launch_arguments=[
            ("gz_args", [" -r -v 3 ", world_file])
        ]
    )

    # Spawn robot in Gazebo
    gz_spawn_entity_node = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-name", "diff_drive",
            "-allow_renaming", "true"
        ]
    )

    # Diff Drive Controller
    diff_drive_base_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_base_controller",
            "--param-file",
            config_file
        ]
    )

    # Joint State Broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster"
        ]
    )

    # Gazebo-ROS Bridge
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
        ],
        output="both"
    )

    # RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_file],
        parameters=[
            {"use_sim_time": True}
        ]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        rviz_node,
        gz_sim_launch_node,
        gz_spawn_entity_node,
        diff_drive_base_controller_spawner,
        joint_state_broadcaster_spawner,
        bridge
    ])