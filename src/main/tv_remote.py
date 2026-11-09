"""
Usage:  python tv_remote.py <server host/IP> <port>
Example: python tv_remote.py 192.168.67.12 1238
"""
import socket
import sys

class RemoteControl:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self._sock = None
    self._file = None

  def connect(self):
    self._sock = socket.create_connection((self.host, self.port), timeout=5)
    self._sock.settimeout(None)
    self._file = self._sock.makefile("rw", encoding="utf-8", newline="\n")

  def send(self, command):
    """Send one command and return the reply, or None if the
    connection was lost."""
    try:
      self._file.write(command + "\n")
      self._file.flush()
      reply = self._file.readline()
    except (ConnectionResetError, BrokenPipeError):
      return None
    return reply.strip() if reply else None

  def close(self):
    if self._file:
      self._file.close()
    if self._sock:
      self._sock.close()

  def run(self):
    print(f"Connected to TV at {self.host}:{self.port}. Type QUIT to exit.")
    while True:
      try:
        cmd = input("remote> ").strip()
      except (EOFError, KeyboardInterrupt):
        print()
        break
      if not cmd:
        continue
      if cmd.upper() in ("QUIT", "EXIT"):
        break
      reply = self.send(cmd)
      if reply is None:
        print("Lost connection to the TV.")
        break
      print(reply)


def main():
  if len(sys.argv) != 3:
    sys.exit("Usage: python tv_remote.py <host> <port>")
  try:
    port = int(sys.argv[2])
  except ValueError:
    sys.exit("Port must be a number")

  remote = RemoteControl(sys.argv[1], port)
  try:
    remote.connect()
  except OSError as e:
    sys.exit(f"Could not connect to {sys.argv[1]}:{port}: {e}")
  try:
    remote.run()
  finally:
    remote.close()


if __name__ == "__main__":
  main()