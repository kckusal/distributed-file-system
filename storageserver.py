import os, sys
import rpyc
from subprocess import run
import socket
import random
import json
from functools import reduce
from operator import getitem

class StorageServerService(rpyc.Service):
  ROOT = "/ken"

  def __init__(self):
    print('Storage Server started..')

  def on_connect(self, conn):
    sock = conn._channel.stream.sock
    print('New connection:', sock.getpeername())
  
  def on_disconnect(self, conn):
    sock = conn._channel.stream.sock
    print('Connection terminated:', sock.getpeername())

  def parse_path(self, path):
    if path[:4]!=self.ROOT: path = os.path.join(self.ROOT, path)
    return path

  def exposed_put(self, block_path, data):
    # put given file to this path
    path = self.parse_path(block_path)
    #block_path += ".ken"
    # it's guaranteed that there will be no conflicts as file name is uuid4
    self.exposed_run_shell_cmd('sudo echo "">{}'.format(block_path))
    with open(block_path, 'wb') as f:
      f.write(data)
    print('Putting block "{}" here.'.format(block_path))

  def exposed_get(self, block_path):
    if not os.path.isfile(block_path): return None
    with open(block_path, 'rb') as file:
      data = file.read()
    return data
    print('Block "{}" requested.'.format(block_path.rsplit("/", 1)[1]))

  def exposed_send_my_block(self, origin_block_path, destination, destination_block_path):
    dest = destination.split(":")
    try:
      conn = rpyc.connect(dest[0], dest[2])
      with open(origin_block_path, "rb") as lf:
        data = lf.read()
        conn.root.put(destination_block_path, data)
    except ConnectionRefusedError:
      print('Connection to {} refused while sending block'.format(dest))

  # block_received is automatically done by ns, only worry about block sent here
  def inform_ns_block_sent(self, block_id, ss_id):
    ns = "ns:3.134.8.132:18861"
    ns = ns.split(":")
    try:
      # here we need to connect to Name Server, IP, Port of NS needed.
      conn = rpyc.connect(ns[0], ns[2])
      conn.root.mark_new_block(block_id, ss_id)
      print('Block sent informed to NS.')
    except ConnectionRefusedError:
      print("Connection refused when trying to connect to NS to inform of blocks sent.")

  def exposed_forward_my_blocks(self, blocks, dests):
    for root, dirs, files in os.walk('/ken'):
      for name in files:
        if name in blocks:
          target = random.choice(dests)
          target_path = os.path.join(root, name)
          self.exposed_send_my_block(target_path, target, target_path)
          self.inform_ns_block_sent(name, target)
          print('My block {} forwarded to {}'.format(name, target))
  
  def maintain_subdirectories(self, root, to_add, to_remove):
    for x in to_add:
      cmd = "sudo mkdir {}".format(os.path.join(root, x))
      self.exposed_run_shell_cmd(cmd)
      self.exposed_run_shell_cmd("sudo chmod -R -v 777 {}".format(os.path.join(root, x)))
    
    for y in to_remove:
      cmd = "sudo rm -rf {}".format(os.path.join(root, y))
      self.exposed_run_shell_cmd(cmd)


  # Modify my directory structure to fit given structure
  def exposed_adapt_this_directory_structure(self, struct):
    struct = json.loads(struct)

    for root, dirs, files in os.walk('/ken/'):

      keys = root.replace("/", " ").strip().split(" ")
      data = reduce(getitem, keys, struct)
      
      source = [x for x in list(data.keys()) if "blocks" not in data[x]]
      existing = dirs

      to_add = list(set(source) - set(existing))
      to_remove = list(set(existing) - set(source))

      self.maintain_subdirectories(root, to_add, to_remove)


  # use subprocess to run shell command on Unix system
  def exposed_run_shell_cmd(self, formatted_cmd_str):
    from subprocess import run
    run("sudo chmod -R -v 777 /ken/", shell=True, check=True)
    run(formatted_cmd_str, shell=True, check=True)


def main(port=18861):
  from rpyc.utils.server import ThreadedServer
  t = ThreadedServer(StorageServerService(),port=port)
  print('Server details: ({}, {})'.format(t.host, port))
  t.start()
  

if __name__=="__main__":
  args = sys.argv[1:]
  if len(args)>1:
    print('Wrong usage: You can only specify [port] as argument.')
    sys.exit(0)
  elif len(args)==0:
    port = 18861
  else:
    port = int(args[0])
  main(port)
