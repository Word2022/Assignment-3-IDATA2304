
import socket
import sys
import threading

from tv_logic import SmartTV

DEFAULT_PORT = 1238
NUM_CHANNELS = 5


class TVServer:
  def __init__(self, tv, port=DEFAULT_PORT):
    self.tv = tv
    self.port = port
    self.lock = threading.Lock()
    self.remotes = set()

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
        threading.Thread(
          target=self._serve_client, args=(conn, addr), daemon=True,
        ).start()
    except KeyboardInterrupt:
      print("Shutting down")
    finally:
      server.close()

  def notify_others(self, sender, before, after):
    events = []
    if before[0] != after[0]:
      events.append("EVENT POWER " + ("ON" if after[0] else "OFF"))
    if before[1] != after[1]:
      events.append(f"EVENT CHANNEL {after[1]}")

    for event in events:
      for remote in list(self.remotes):
        if remote is sender:
          continue
        try:
          remote.write(event + "\n")
          remote.flush()
        except (OSError, ValueError):
          pass   # that remote is gone; its own thread cleans up

  def _serve_client(self, conn, addr):
    print(f"Remote connected from {addr}")
    try:
      with conn, conn.makefile("rw", encoding="utf-8", newline="\n") as f:
        with self.lock:
          self.remotes.add(f)           # register this remote
        try:
          for line in f:
            with self.lock:
              before = (self.tv.is_on, self.tv.channel)
              reply = self.tv.handle_command(line)
              after = (self.tv.is_on, self.tv.channel)
              f.write(reply + "\n")
              f.flush()
              self.notify_others(f, before, after)
            print(f"  {addr}: {line.strip()!r} -> {reply!r}")
        finally:
          with self.lock:
            self.remotes.discard(f)   # unregister on disconnect
    except (ConnectionResetError, BrokenPipeError):
      pass

    print(f"Remote {addr} disconnected")


def show_event(message):
  print(f"\n[TV update] {message}")
  print("remote> ", end="", flush=True)

def main():
  port = DEFAULT_PORT
  if len(sys.argv) > 1:
    try:
      port = int(sys.argv[1])
    except ValueError:
      sys.exit("Port must be a number")

  TVServer(SmartTV(NUM_CHANNELS), port).serve_forever()


if __name__ == "__main__":
  main()