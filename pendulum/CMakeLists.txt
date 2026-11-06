cmake_minimum_required(VERSION 3.8)
project(pendulum)


find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf launch config world rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
