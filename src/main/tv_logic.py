

class SmartTV:
  def __init__(self, num_channels=5):
    self.num_channels = num_channels
    self.is_on = False
    self.channel = 1

  def power_on(self):
    self.is_on = True

  def power_off(self):
    self.is_on = False

  def get_channel(self):
    self._require_on()
    return self.channel

  def set_channel(self, number):
    self._require_on()
    if not 1 <= number <= self.num_channels:
      raise Exception(f"channel must be 1-{self.num_channels}")
    self.channel = number

  def channel_up(self):
    self._require_on()
    self.channel = self.channel % self.num_channels + 1

  def channel_down(self):
    self._require_on()
    self.channel = (self.channel - 2) % self.num_channels + 1

  def _require_on(self):
    if not self.is_on:
      raise Exception("TV is off")


  def handle_command(self, line):
    parts = line.strip().upper().split()
    if not parts:
      return "ERROR empty command"
    try:
      return self._execute(parts[0], parts[1:])
    except Exception as e:
      return f"ERROR {e}"

  def _execute(self, cmd, args):
    if cmd == "STATUS":
      return "ON" if self.is_on else "OFF"

    if cmd == "POWER":
      if len(args) != 1 or args[0] not in ("ON", "OFF"):
        raise Exception("usage: POWER ON|OFF")
      self.power_on() if args[0] == "ON" else self.power_off()
      return "TV is turned " + args[0]

    if cmd == "CHANNELS":
      self._require_on()
      return f"The TV has {self.num_channels} channels"

    if cmd == "GET":
      return f"The TV is on channel {self.get_channel()}"

    if cmd == "UP":
      self.channel_up()
      return f"Switched to channel {self.channel}"

    if cmd == "SET":
      self.set_channel(int(args[0]))
      return f"Set channel to channel number {self.channel}"

    if cmd == "DOWN":
      self.channel_down()
      return f"Switched to channel {self.channel}"

    raise Exception("unknown command")