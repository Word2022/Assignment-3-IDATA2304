"""Remote control (TCP client) that also shows updates from other remotes.

Usage:  python tv_remote.py <server host/IP> <port>
"""
import queue
import socket
import sys
import threading


class RemoteControl:
  def __init__(self, host, port, on_event=None):
    self.host = host
    self.port = port
    self.on_event = on_event or (lambda message: None)
    self._sock = None
    self._reader = None
    self._writer = None
    self._replies = queue.Queue()

  def connect(self):
    self._sock = socket.create_connection((self.host, self.port), timeout=5)
    self._sock.settimeout(None)
    # Separate read and write files, because two threads use them
    self._reader = self._sock.makefile("r", encoding="utf-8", newline="\n")
    self._writer = self._sock.makefile("w", encoding="utf-8", newline="\n")
    threading.Thread(target=self._read_loop, daemon=True).start()

  def _read_loop(self):
    try:
      for line in self._reader:
        line = line.strip()
        if line.startswith("EVENT "):
          try:
            self.on_event(line[len("EVENT "):])
          except Exception as e:
            print(f"Event handler error: {e!r}")
        else:
          self._replies.put(line)
    except (OSError, ValueError):
      pass
    self._replies.put(None)  # signals "connection closed"

  def send(self, command, timeout=5):
    try:
      self._writer.write(command + "\n")
      self._writer.flush()
    except (OSError, ValueError):
      return None
    try:
      return self._replies.get(timeout=timeout)
    except queue.Empty:
      return "ERROR no reply from server"

  def close(self):
    try:
      self._sock.shutdown(socket.SHUT_RDWR)  # wakes the reader thread
    except (OSError, AttributeError):
      pass
    for item in (self._writer, self._reader, self._sock):
      if item:
        try:
          item.close()
        except OSError:
          pass

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


def show_event(message):
  print(f"\n[TV update] {message}")
  print("remote> ", end="", flush=True)  # redraw the prompt


def main():
  if len(sys.argv) != 3:
    sys.exit("Usage: python tv_remote.py <host> <port>")
  try:
    port = int(sys.argv[2])
  except ValueError:
    sys.exit("Port must be a number")

  remote = RemoteControl(sys.argv[1], port, on_event=show_event)
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