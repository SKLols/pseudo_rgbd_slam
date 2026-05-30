from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():

    node_b = Node(
        package='pseudo_rgbd_slam',
        executable='node_b_depth_estimator',
        name='node_b_depth_estimator',
        output='screen'
    )

    node_c = TimerAction(period=25.0, actions=[
        Node(
            package='pseudo_rgbd_slam_cpp',
            executable='node_c_slam',
            name='node_c_slam',
            output='screen'
        )
    ])

    node_a = TimerAction(period=50.0, actions=[
        Node(
            package='pseudo_rgbd_slam',
            executable='node_a_broadcaster',
            name='node_a_broadcaster',
            output='screen'
        )
    ])

    return LaunchDescription([node_b, node_c, node_a])