
import sys
import unittest
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tv_logic import (SmartTV)


class TestSmartTV(unittest.TestCase):
  def setUp(self):
    self.tv = SmartTV(num_channels=5)

  def test_starts_on_channel_1(self):
    self.assertEqual(self.tv.channel, 1)

  def test_commands_rejected_while_off(self):
    for cmd in ("UP", "DOWN", "GET", "CHANNELS"):
      self.assertEqual(self.tv.handle_command(cmd), "ERROR TV is off")
    self.assertEqual(self.tv.handle_command("STATUS"), "OFF")

  def test_up_wraps_around(self):
    self.tv.power_on()
    self.tv.set_channel(5)
    self.assertEqual(self.tv.handle_command("UP"), "Switched to channel 1")

  def test_down_wraps_around(self):
    self.tv.power_on()
    self.assertEqual(self.tv.handle_command("DOWN"), "Switched to channel 5")

  def test_channel_remembered_after_power_cycle(self):
    self.tv.handle_command("POWER ON")
    self.tv.handle_command("UP")
    self.tv.handle_command("POWER OFF")
    self.tv.handle_command("POWER ON")
    self.assertEqual(self.tv.handle_command("GET"), "The TV is on channel 2")

  def test_invalid_input_is_handled(self):
    self.tv.power_on()
    for cmd in ("SET 99", "SET 0", "SET abc", "SET", "SET -1",
                "POWER", "POWER blegh", "wowiezowie", ""):
      self.assertTrue(self.tv.handle_command(cmd).startswith("ERROR"), cmd)


if __name__ == "__main__":
  unittest.main()