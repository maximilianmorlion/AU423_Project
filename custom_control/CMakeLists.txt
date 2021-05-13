cmake_minimum_required(VERSION 2.8.3)
project(custom_control)

find_package(catkin REQUIRED)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES control_robot_ipsa
#  CATKIN_DEPENDS controller_manager joint_state_controller robot_state_publisher
#  DEPENDS system_lib
)

## Mark executable scripts (Python etc.) for installation
## in contrast to setup.py, you can choose the destination
catkin_install_python(PROGRAMS
   teleop_twist_keyboard.py
   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

