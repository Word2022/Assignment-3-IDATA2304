
import socket
import sys


from tv_logic import SmartTV

DEFAULT_PORT = 1238
NUM_CHANNELS = 5


class TVServer:
  def __init__(self, tv, port=DEFAULT_PORT):
    self.tv = tv
    self.port = port

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
        self._serve_client(conn, addr)  # one remote at a time
    except KeyboardInterrupt:
      print("Shutting down")
    finally:
      server.close()

  def _serve_client(self, conn, addr):
    print(f"Remote connected from {addr}")
    try:
      with conn, conn.makefile("rw", encoding="utf-8", newline="\n") as f:
        for line in f:  # loop ends when the client disconnects
          reply = self.tv.handle_command(line)
          print(f"  {line.strip()!r} -> {reply!r}")
          f.write(reply + "\n")
          f.flush()
    except (ConnectionResetError, BrokenPipeError):
      pass
    print("Remote disconnected")


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