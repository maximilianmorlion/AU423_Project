# AU423_IPSA

## Create a ROSject

Connect to [RDS](https://app.theconstructsim.com/#/) and enter your username and password if needed.

On the left panel, click on **My Rosjects** ,then create a new one:

* ROS Distro: **ROS Melodic**
* Name: *AU423_IPSA* (for instance)
* Description: *This is my project for AU423* (for instance)

Then click on **Create** and run the ROSject.



## Cloning the Github repository

Open a terminal (Web shell) and follow the instructions **ONE AFTER THE OTHER**:

```bash
cd ~/catkin_ws/src && git clone https://github.com/JohvanyROB/AU423_IPSA.git
cd ~/catkin_ws && catkin_make && source ~/catkin_ws/devel/setup.bash
```

You can now come back to the slides.
