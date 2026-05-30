cmake_minimum_required(VERSION 3.8)
project(pseudo_rgbd_slam_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(message_filters REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(node_c_slam src/node_c_slam.cpp)
ament_target_dependencies(node_c_slam rclcpp message_filters sensor_msgs cv_bridge OpenCV nav_msgs geometry_msgs)

install(TARGETS node_c_slam
  DESTINATION lib/${PROJECT_NAME})

ament_package()
