# AU423_Project
Robot with an arm in a environment 

# AU423_IPSA

## Create a ROSject

Connect to [RDS](https://app.theconstructsim.com/#/) and enter your username and password if needed.

On the left panel, click on **My Rosjects** ,then create a new one:

* ROS Distro: **ROS Noetic**
* Name: *AU423_Project* (for instance)
* Description: *This is my project for AU423* (for instance)

Then click on **Create** and run the ROSject.



## Cloning the Github repository

Open a terminal (Web shell) and follow the instructions **ONE AFTER THE OTHER**:

```bash
cd ~/catkin_ws/src && git clone https://github.com/maximilianmorlion/AU423_Project.git
cd ~/catkin_ws && catkin_make && source ~/catkin_ws/devel/setup.bash
```

Then you can launch the robot and the environment with : 
```bash
roslaunch description_robot_ipsa simu.launch
```
Enjoy ! All the commands to control the robot are written in the console !
