# BittleXboxController
Control your Bittle using Xbox One controller.

Connect to Bittle through WiFi (Linux & Windows) or Bluetooth (Linux) and start controlling your Bittle with a Xbox controller.

![alt tag](/readme_images/gif1.gif)

Dependencies: [pyBittle](https://github.com/EnriqueMoran/pyBittle)


##How it works
The controller and Bittle are connected to your computer. This tool receives the inputted data from the controller, translates it into Bittle understandable commands and sends them to it through Bluetooth or WiFi connection using pyBittle library.

## How to use
1. Connect the Xbox controller to your computer.
2. Turn on your Bittle and connect it to your computer (only in case you will control it through Bluetooth).
3. Run this tool.
4. Control your Bittle using the Xbox controller.
5. To exit, press ctrl + c.


## Buttons
* **A:** BALANCE
* **B:** REST
* **X:** GREETING
* **Y:** SIT
* **LB:** STEP
* **LR:** GYRO
* **Left pad:** CRAWL
* **Right pad:** TROT
* **Down pad:** WALK
* **Up pad:** RUN


## Known issues
* Gyro command not working.
* Sometimes command is not recognized, to fix this, send another one (e.g, BALANCE).