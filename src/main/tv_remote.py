"""
Usage:  python tv_remote.py <server host/IP> <port>
Example: python tv_remote.py 192.168.67.12 1238
"""
import socket
import sys
import threading
import queue

class RemoteControl:
  def __init__(self, host, port, on_event=None):
    self.host = host
    self.port = port
    self.on_event = on_event or (lambda message : None)
    self._reader
    self._sock = None
    self._file = None
    self.replies = queue.Queue()

  def connect(self):
    self._sock = socket.create_connection((self.host, self.port), timeout=5)
    self._sock.settimeout(None)
    self._file = self._sock.makefile("rw", encoding="utf-8", newline="\n")
    self._reader = self._sock.makefile("rw", encoding="utf-8", newline="\n")
    threading.Thread(target=self._read_loop, daemon=True).start()

  def read_loop(self):
    try:
      for line in self._reader:
        line = line.strip()
        if line.startswith("EVENT "):
          self.on_event(line[len("EVENT "):])
        else:
          self.replies.put(line)
    except(OSError,ValueError):
      pass
    self._replies.put(None)

  def send(self, command):
    """Send one command and return the reply, or None if the
    connection was lost."""
    try:
      self._file.write(command + "\n")
      self._file.flush()
      reply = self._file.readline()
    except (OSError,ValueError):
      return None
    return self._replies.get()

  def close(self):
    try:
      self._sock.shutdown(socket.SHUT_RDWR)   # wakes the reader thread
    except (OSError, AttributeError):
      pass
    for item in (self._writer, self._reader, self._sock):
      if item:
        item.close()

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