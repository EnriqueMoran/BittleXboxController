"""This program allow to control Bittle using Xbox controller.
"""

import os
import pyBittle
import pygame
import sys
import time


__author__ = "EnriqueMoran"

__version__ = "v1.0"


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
        self.gait = pyBittle.Command.WALK

        self.bittle = None
        self.connect_wifi = connect_wifi
        self.connect_bluetooth = connect_bluetooth
        self.ip_addr = ip_addr
        self.device_name = device_name
        self.bt_port = bt_port
        self.gait = pyBittle.Command.WALK
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
        for i in range(self.n_axes):
            axis = self.joystick.get_axis(i)
            if i == 0:  # vertical
                if axis > 0 and abs(axis) > 0.7:  # Right
                    new_direction = pyBittle.Command.RIGHT
                    break
                elif axis < 0 and abs(axis) > 0.7:  # Left
                    new_direction = pyBittle.Command.LEFT
                    break
                else:
                    new_direction = pyBittle.Command.BALANCE
            elif i == 1:  # horizontal
                if axis > 0 and abs(axis) > 0.7:  # Backward
                    new_direction = pyBittle.Command.BACKWARD
                    break
                elif axis < 0 and abs(axis) > 0.7:  # Forward
                    new_direction = pyBittle.Command.FORWARD
                    break
                else:  # Stop
                    new_direction = pyBittle.Command.BALANCE

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
            if hat == (-1, 0):  # left
                gait = pyBittle.Command.CRAWL
            elif hat == (1, 0):  # right
                gait = pyBittle.Command.TROT
            elif hat == (0, -1):  # down
                gait = pyBittle.Command.WALK
            elif hat == (0, 1):  # up
                gait = pyBittle.Command.RUN
            if gait:
                self.gait = gait
                print(f"New gait selected: {self.gait}")

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
        time.sleep(1)  # let Bittle rest to prevent damage
        return True

    def send_direction(self, command):
        direction = self.bittle._commands[self.gait] +\
                    self.bittle._commands[command]
        direction = 'kbk' if command == pyBittle.Command.BACKWARD \
                    else direction
        if self.connect_wifi:
            if self.bittle.has_wifi_connection():
                if command == pyBittle.Command.BALANCE:
                    self.bittle.send_command_wifi(command)
                else:
                    self.bittle.send_msg_wifi(direction)
        elif self.connect_bluetooth:
            if command == pyBittle.Command.BALANCE:
                self.bittle.send_command_bluetooth(command)
            else:
                self.bittle.send_msg_bluetooth(direction)
        print(f"Direction: {command} sent")
        # Let Bittle rest to prevent damage, modify this under your own risk
        time.sleep(0.5)
        return True


if __name__ == '__main__':
    connect_wifi = False  # Set to True to connect through WiFi
    connect_bluetooth = False  # Set to True to connect through Bluetooth
    ip_addr = '192.168.1.138'  # Here goes your Bittle's IP address
    controller = Controller(connect_wifi=connect_wifi,
                            connect_bluetooth=connect_bluetooth,
                            ip_addr=ip_addr)
    if not connect_wifi and not connect_bluetooth:
        print("No connection method selected.")
        sys.exit()
    try:
        controller.run()
    except KeyboardInterrupt:
        if controller.connect_bluetooth:
            print("Closing Bluetooth connection with Bittle")
            try:
                controller.bittle.send_command_bluetooth(pyBittle.Command.REST)
                controller.bittle.disconnect_bluetooth()
            except:
                pass
        sys.exit()
