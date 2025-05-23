import time
import signal
from gpiozero import PWMOutputDevice

from pifan.fan_control.get_controller import get_controller
from pifan.fan_control.base_controller import ControllerOptions

from pifan.config import config_loader

class Daemon:

    def __init__(self):
        self.temp_sensor_path = "/sys/class/thermal/thermal_zone0/temp"
        self.fan_speed = 0.0

    def _log_message(self, message: str):
        print(f"[daemon] {message}")

    def get_temp(self) -> float:
        """
        Reads the temperature from the provided TEMP_SENSOR_PATH
        """
        with open(self.temp_sensor_path, "r") as sensor:
            temp_str = sensor.read()
        return int(temp_str) / 1000
    
    def get_status(self) -> dict[str]:
        """
        Daemon status as dictionary
        """
        return {
            "system_temperature": self.get_temp(),
            "fan_speed": self.fan_speed,
            "controller": self.controller.get_name()
        }
    
    def get_config(self) -> dict[str]:
        """
        Daemon configuration as dictionary
        """
        return {
            "temp_high": self.config["fan"]["temp_high"],
            "temp_low": self.config["fan"]["temp_low"],
            "gpio_pin": self.config["fan"]["gpio_pin"],
            "controller": self.controller.get_name(),
            "frequency": self.config["fan"]["frequency"]
        }

    def set_controller(self, controller_name: str) -> bool:
        controller = get_controller(controller_name, self.controller_options)
        if controller:
            self.controller = controller
            return True
        return False

    def _handle_sigterm(self, _signum, _frame):
        self._keep_running = False
        self._exit()

    def _exit(self):
        self._log_message("stopping daemon...")
        self.fan.value = 0.0

    def run(self):
        self.config = config_loader.load_config()
        self.controller_options = ControllerOptions(self.config["fan"]["temp_high"],
                                               self.config["fan"]["temp_low"])
        self.controller = get_controller(self.config["fan"]["controller"], self.controller_options)
        if not self.controller:
            self._log_message(f"error: invalid controller {self.config['fan']['controller']}, defaulting to max_speed")
            self.controller = get_controller("max_speed", self.controller_options)
        self.fan = PWMOutputDevice(pin=self.config["fan"]["gpio_pin"], 
                                   frequency=self.config["fan"]["frequency"])
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        self._keep_running = True
        self._log_message("fan daemon started")
        while self._keep_running:
            try:
                temp = self.get_temp()
                self.fan_speed = round(self.controller.get_speed(temp), 2)
                self.fan.value = self.fan_speed
                time.sleep(self.config["daemon"]["update_interval"])
            except KeyboardInterrupt:
                self._exit()
                break
