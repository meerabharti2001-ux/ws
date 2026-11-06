cmake_minimum_required(VERSION 3.8)
project(cart)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf launch config world rviz
  DESTINATION share/${PROJECT_NAME}
)

#beginplugin
#this should be same in${PROJECT_NAME}.xml in library path
find_package(rclcpp REQUIRED)
find_package(pluginlib REQUIRED)
find_package(hardware_interface REQUIRED)

add_library(${PROJECT_NAME} SHARED
  hardware/gz_custom_system.cpp
)

ament_target_dependencies(${PROJECT_NAME}
  hardware_interface
	pluginlib
	rclcpp
)

target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/hardware/include>
	$<INSTALL_INTERFACE:include>
)
	
pluginlib_export_plugin_description_file(
  hardware_interface
	gz_custom_hardware_plugins.xml
)

install(
  DIRECTORY include/
  DESTINATION include
)

install(
  TARGETS ${PROJECT_NAME}
  DESTINATION lib
)
#endplugin


ament_package()
