"""This program allow to control Bittle using Xbox controller.
"""

import math
import os
import pyBittle
import pygame
import sys
import time


__author__ = "EnriqueMoran"

__version__ = "v1.1"


BUTTONS_MAP = {
    0: pyBittle.Command.BALANCE,   # A
    1: pyBittle.Command.REST,      # B
    2: pyBittle.Command.GREETING,  # X
    3: pyBittle.Command.SIT,       # Y
    4: pyBittle.Command.STEP,      # LB
    5: pyBittle.Command.GYRO       # RB
}


class Controller():

    def __init__(self, window_size=(1, 1),
                 connect_wifi=False, connect_bluetooth=False,
                 ip_addr=None, device_name=None, bt_port=None):
        self.window_size = window_size
        self.window = None
        self.joystick = None
        self.n_axes = 0
        self.n_buttons = 0
        self.n_hats = 0

        self.bittle = None
        self.connect_wifi = connect_wifi
        self.connect_bluetooth = connect_bluetooth
        self.ip_addr = ip_addr
        self.device_name = device_name
        self.bt_port = bt_port
        self.direction = pyBittle.Command.BALANCE

    def initialize(self):
        os.environ["DISPLAY"] = ":0"
        os.environ["SDL_VIDEODRIVER"] = "dummy"  # Hide window
        controller_found = False
        self.window = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Bittle controller")
        pygame.init()
        pygame.time.Clock().tick(30)

        self.bittle = pyBittle.Bittle()
        if self.connect_wifi:
            self.bittle.wifiManager.ip = self.ip_addr
        elif self.connect_bluetooth:
            self.bittle.connect_bluetooth()
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.n_axes = self.joystick.get_numaxes()
            self.n_buttons = self.joystick.get_numbuttons()
            self.n_hats = self.joystick.get_numhats()
            print(f"Joystick found: {self.joystick.get_name()}")
            controller_found = True
        except:
            print("No controller found!")
        return controller_found

    def read_inputs(self):
        new_direction = self.direction
        x_axis_value = 0
        y_axis_value = 0
        for i in range(self.n_axes):
            axis_value = self.joystick.get_axis(i)
            if i == 0:  # Horizontal
                x_axis_value = axis_value
            elif i == 1:  # Vertical
                y_axis_value = -axis_value  # Set FORWARD as positive value

        if abs(x_axis_value) > 0.8 or abs(y_axis_value) > 0.8:
            angle = self.get_angle(x_axis_value, y_axis_value)
            if angle >= 337.5 or angle < 22.5:
                new_direction = pyBittle.Direction.FORWARD
            elif angle >= 22.5 and angle < 67.5:
                new_direction = pyBittle.Direction.FORWARDRIGHT
            elif angle >= 67.5 and angle < 112.5:
                new_direction = pyBittle.Direction.FORWARDRIGHT
            elif angle >= 112.5 and angle < 157.5:
                new_direction = pyBittle.Direction.BACKWARDRIGHT
            elif angle >= 157.5 and angle < 202.5:
                new_direction = pyBittle.Direction.BACKWARD
            elif angle >= 202.5 and angle < 247.5:
                new_direction = pyBittle.Direction.BACKWARDLEFT
            elif angle >= 247.5 and angle < 292.5:
                new_direction = pyBittle.Direction.FORWARDLEFT
            elif angle >= 292.5 and angle < 337.5:
                new_direction = pyBittle.Direction.FORWARDLEFT
        elif abs(x_axis_value) < 0.2 or abs(y_axis_value) < 0.2:
            new_direction = pyBittle.Command.BALANCE  # Stop

        if self.direction != new_direction:
            self.direction = new_direction
            self.send_direction(self.direction)

        for i in range(self.n_buttons):
            button = self.joystick.get_button(i)
            if button:
                try:
                    command = BUTTONS_MAP[i]
                    self.send_command(command)
                except Exception as e:
                    print(e)

        for i in range(self.n_hats):
            gait = None
            hat = self.joystick.get_hat(i)
            if hat == (-1, 0):  # Left pad
                gait = pyBittle.Gait.CRAWL
            elif hat == (1, 0):  # Right pad
                gait = pyBittle.Gait.TROT
            elif hat == (0, -1):  # Down pad
                gait = pyBittle.Gait.WALK
            elif hat == (0, 1):  # Up pad
                gait = pyBittle.Gait.RUN
            if gait:
                self.bittle.gait = gait
                print(f"New gait selected: {gait}")
                time.sleep(0.2)

    def run(self):
        initialized = self.initialize()
        if initialized:
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                self.read_inputs()
        pygame.quit()

    def send_command(self, command):
        if self.connect_wifi:
            if self.bittle.has_wifi_connection():
                self.bittle.send_command_wifi(command)
        elif self.connect_bluetooth:
            self.bittle.send_command_bluetooth(command)
        print(f"Action: {command} sent")
        time.sleep(0.5)  # Let Bittle rest to prevent damage
        return True

    def send_direction(self, direction):
        if self.connect_wifi:
            if self.bittle.has_wifi_connection():
                if direction == pyBittle.Command.BALANCE:
                    self.bittle.send_command_wifi(direction)
                else:
                    self.bittle.send_movement_wifi(direction)
        elif self.connect_bluetooth:
            if direction == pyBittle.Command.BALANCE:
                self.bittle.send_command_bluetooth(direction)
            else:
                self.bittle.send_movement_bluetooth(direction)
        print(f"Direction: {direction} sent")
        # Let Bittle rest to prevent damage, modify this under your own risk
        time.sleep(0.5)
        return True

    def get_angle(self, xPercent, yPercent):
        """Returns joystick angle.
        """
        angle_deg = 0
        if xPercent > 0.9 and yPercent == 0:
            angle_deg = 90
        elif xPercent < -0.9 and yPercent == 0:
            angle_deg = 270
        elif xPercent == 0 and yPercent > 0.9:
            angle_deg = 1
        elif xPercent == 0 and yPercent < -0.9:
            angle_deg = 180
        elif (xPercent > 0 and yPercent > 0 and (xPercent > 0.2 or
              yPercent > 0.2)):
            angle_rad = math.atan2(xPercent, yPercent)
            angle_deg = angle_rad * 180 / math.pi
        elif (xPercent > 0 and yPercent < 0 and (xPercent > 0.2 or
              yPercent < -0.2)):
            angle_rad = math.atan2(xPercent, yPercent)
            angle_deg = angle_rad * 180 / math.pi
        elif (xPercent < 0 and yPercent < 0 and (xPercent < -0.2 or
              yPercent < -0.2)):
            angle_rad = math.atan2(xPercent, yPercent)
            angle_deg = angle_rad * 180 / math.pi
            angle_deg += 360
        elif (xPercent < 0 and yPercent > 0 and (xPercent < -0.2 or
              yPercent > 0.2)):
            angle_rad = math.atan2(xPercent, yPercent)
            angle_deg = angle_rad * 180 / math.pi
            angle_deg += 360
        return angle_deg


if __name__ == '__main__':
    connect_wifi = False  # Set to True to connect through WiFi
    connect_bluetooth = False  # Set to True to connect through Bluetooth
    ip_addr = '192.168.1.138'  # Here goes your Bittle's IP address
    controller = Controller(connect_wifi=connect_wifi,
                            connect_bluetooth=connect_bluetooth,
                            ip_addr=ip_addr)
    if not connect_wifi and not connect_bluetooth:
        print("No connection method selected.")
        input()
        sys.exit()
    try:
        controller.run()
    except KeyboardInterrupt:
        if controller.connect_bluetooth:
            print("Closing Bluetooth connection with Bittle")
            try:
                controller.bittle.send_command_bluetooth(pyBittle.Command.REST)
                controller.bittle.disconnect_bluetooth()
                print("Connection Closed")
            except:
                pass
        input()
        sys.exit()
