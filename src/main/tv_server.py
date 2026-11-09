"""
Usage:  python tv_server.py [port]      (default port: 1238)
"""
import socket
import sys
import threading

from tv_logic import SmartTV

DEFAULT_PORT = 1238
NUM_CHANNELS = 5  # C >= 3, you choose


class TVServer:
  def __init__(self, tv, port=DEFAULT_PORT):
    self.tv = tv
    self.port = port
    self._lock = threading.Lock()   # guards the TV and _remotes
    self._remotes = set()           # one file object per connected remote

  def serve_forever(self):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", self.port))
    server.listen()
    print(f"Smart TV listening on port {self.port} "
          f"({self.tv.num_channels} channels)")
    try:
      while True:
        conn, addr = server.accept()
        threading.Thread(target=self._serve_client,
                         args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
      print("\nShutting down")
    finally:
      server.close()

  def _serve_client(self, conn, addr):
    try:
      with conn, conn.makefile("rw", encoding="utf-8", newline="\n") as f:
        with self._lock:
          self._remotes.add(f)
          count = len(self._remotes)
        print(f"Remote connected from {addr} ({count} connected)")
        try:
          for line in f:
            with self._lock:
              before = (self.tv.is_on, self.tv.channel)
              reply = self.tv.handle_command(line)
              after = (self.tv.is_on, self.tv.channel)
              f.write(reply + "\n")
              f.flush()
              self._notify_others(f, before, after)
            print(f"  {addr}: {line.strip()!r} -> {reply!r}")
        finally:
          with self._lock:
            self._remotes.discard(f)
    except (ConnectionResetError, BrokenPipeError):
      pass
    print(f"Remote {addr} disconnected")

  def _notify_others(self, sender, before, after):
    events = []
    if before[0] != after[0]:
      events.append("EVENT POWER " + ("ON" if after[0] else "OFF"))
    if before[1] != after[1]:
      events.append(f"EVENT CHANNEL {after[1]}")
    if not events:
      return

    others = [r for r in self._remotes if r is not sender]
    print(f"  change {before} -> {after}: "
          f"notifying {len(others)} other remote(s)")
    for event in events:
      for remote in others:
        try:
          remote.write(event + "\n")
          remote.flush()
        except (OSError, ValueError) as e:
          print(f"  notify failed: {e!r}")


def main():
  port = DEFAULT_PORT
  if len(sys.argv) > 1:
    try:
      port = int(sys.argv[1])
    except ValueError:
      sys.exit("Port must be a number")
    if not 1 <= port <= 65535:
      sys.exit("Port must be between 1 and 65535")
  try:
    TVServer(SmartTV(NUM_CHANNELS), port).serve_forever()
  except OSError as e:
    sys.exit(f"Could not start server on port {port}: {e}")


if __name__ == "__main__":
  main()