''' NOTE: This was preliminary, so updates were made to this interface.
------------CLIENT Interface-----------

ken connect         Connect to the nameserver, loads repl with current = root.
ken(.):$ exit     Shuts down the interactive dfs repl.
ken(.):$ ls         List directories and files
ken(.):$ cd dir     Change current directory to the 'dir' given if valid, else no valid directory     
ken(.):$ initialize     Removes all existing files in root and returns available size.
ken(.):$ create -f . file.ext              Create a new file in the existing directory
ken(.):$ create -f "root/abc" file.ext     First cd's into given directory (create if missing), then create new file there.
ken(.):$ create -d . dir_name                New directory created in current directory
ken(.):$ create -d "root/abc" dir_name   First cd's into given directory (create if missing), then create new dir there.
ken(.):$ remove  file_dir_name           Removes given dir/file
ken(.):$ refresh                        Refreshes nameserver info
ken(.):$ info .             Information of current directory (How many files? Total Dir size? Recursively dir size of all files present in it.)
ken(.):$ info "root/abc"            info of given dir or file
ken(.):$ put src_file_path dest_path          Uploads file in given path in host's machine to dfs.
ken(.):$ get src_file_path dest_path          Downloads a file in dfs to host's machine.
ken(.):$ copy src_path dest_path
ken(.):$ move src_path dest_path

'''

from __future__ import unicode_literals, print_function
from prompt_toolkit import print_formatted_text as print, HTML
from prompt_toolkit.styles import Style

import os, sys
if sys.version_info < (3, 5):
  print('> Please use Python version 3.5 or above!')
  sys.exit(0)

import math
import time
import random
from uuid import uuid4
import json


style = Style.from_dict({
  'orange': '#ff7e0b',
  'red': '#e74c3c',
  'green': '#22b66c',
  'blue': '#0a84ff',
  'i': 'italic',
  'b': 'bold',
})

try:
  import rpyc
except ModuleNotFoundError:
  print(HTML('> <red>Install <orange>rpyc</orange> module first.</red>'))
  sys.exit(0)

try:
  from tqdm import tqdm
except ModuleNotFoundError:
  print(HTML('> <red>Install <orange>tqdm</orange> module first.</red>\n > sudo pip3 install tqdm\n'))
  sys.exit(0)


CONN = None
NS_IP = None
NS_PORT = None

def connect_to_ns(count_retry=1, max_retry=3):
  global CONN
  print(HTML('<orange>Connecting to nameserver...</orange>'))
  try:
    CONN = rpyc.connect(NS_IP, NS_PORT)
  except ConnectionError:
    CONN = None
  
  time.sleep(1)

  if CONN is None:
    print(HTML("<red>Connection couldn't be established.\n</red>"))
    time.sleep(1)
    if count_retry<=max_retry:
      print("Attempts so far = {}. Let's retry!".format(count_retry))
      return connect_to_ns(count_retry+1, max_retry)
    else:
      print("Maximum allowed attempts made. Closing the application now!\n")
      return False
  else:
    print(HTML("<green>Connected!</green>"))
    time.sleep(1)
    return True

def ns_is_responding():
  global CONN
  try:
    temp = CONN.root.refresh()
    return True
  except EOFError:
    CONN = None
    print(HTML("<red>Error</red>: Connection to nameserver lost!"))
    time.sleep(0.7)
    print(HTML("<green>Retrying</green> in 5 seconds..."))
    time.sleep(5)
    
    return True if connect_to_ns() else False


# put in storage server
def put_in_ss(ss, remote_path, block_name, block_data):
  ss = ss.split(":")
  try:
    conn = rpyc.connect(ss[1], ss[2])
    target_path = os.path.join(remote_path, block_name)
    conn.root.put(target_path, block_data)
  except ConnectionRefusedError:
    print('Connection refused by {} while trying to put block {}'.format(ss, block_name))
  return None

# get from storage server
def get_from_ss(ss, remote_path):
  ss = ss.split(":")
  try:
    conn = rpyc.connect(ss[1], ss[2])
    return conn.root.get(remote_path)
  except ConnectionRefusedError:
    print('Connection refused by {} while trying to get {}'.format(ss, remote_path))

def parse_size_from_bytes(num):
  num = float(num)
  # this function will convert bytes to MB.... GB... etc
  for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
    if num < 1024.0:
      return "%3.2f %s" % (num, x)
    num /= 1024.0

def prettyDictionary(t,s):
  for key in sorted(t.keys()):
    if "blocks" in t[key]:
      print(HTML("   "*(s) + '|- ' + str(key)))
    else:
      key_str = "root" if key=="ken" else key
      if key_str=="root":
        print(HTML(" <b>ROOT</b>"))
      else:
        print(HTML("   "*s + '|- <b><green>' + str(key_str) + "</green></b>"))
    
      if not isinstance(t[key],list):
        prettyDictionary(t[key],s+1)
              
from cmd import Cmd

class MyPrompt(Cmd):
  global CONN
  ABSOLUTE_ROOT = "/ken"
  CURRENT_DIR = '/ken'
  prompt = "[KEN-DFS] (.) >> "
  intro = "Welcome to KEN Distributed File System.\n > Type '?' or 'help' to see available commands.\n > The root volume is /ken/ \n"

  def preloop(self):
    print(HTML('\n------------- <green>Session Started</green> -------------\n'))

  def parse_args(self, cmd_name, args, min_required=0, max_required=float('inf')):
    args = args.strip()
    args = args.split(" ") if len(args)>0 else args
    N = len(args)

    if N<min_required or N>max_required:
      if min_required == max_required:
        required = min_required
      else:
        required = "{} ".format(min_required)
        if math.isinf(max_required):
          required += "or more"
        else:
          required += "to {}".format(max_required)

      print(HTML('<red>Error</red>: <b>{}</b> expected <orange>{}</orange> args, got <orange>{}</orange>.'.format(cmd_name, required, N)))
      print(HTML("<green><b>TIP</b></green>: Try <b>help {}</b> for correct usage.\n".format(cmd_name)))
      return None
    return args

  def print_help(self, form, result):
    form = form.split(" ")
    form[0] = "<orange>{}</orange>".format(form[0])
    form = " ".join(form)
    print(HTML("Usage Format: {} \nResult: {}\n".format(form, result)))

  def print_response(self, response):
    output = "<green>Success</green>:" if response["status"]==1 else "<red>Failed</red>:"
    output += " {}".format(response["message"])
    print(HTML(output))
  
  def print_dictionary(self, d):
    print('')
    print(HTML('<orange>File System</orange>:'))
    prettyDictionary(d, 0)
    print("")

  def do_quit(self, inp):
    print(HTML("\n-------------- <red>Session Ended</red> -------------- \n"))
    return True
  
  def help_quit(self):
    self.print_help('[exit] [x] [q] [Ctrl-D]', '<red>Quit</red> the application.')

  def change_current_directory(self, dir):
    self.CURRENT_DIR = dir
    dir = '.' + dir[4:] if dir[:4]==self.ABSOLUTE_ROOT else dir
    self.prompt = "[KEN-DFS] (" + dir + ") >> "
  
  def do_show(self, args):
    args = args.strip().split(" ", 1)
    
    cmd = None
    myargs = ""
    if len(args)==1:
      cmd = args[0]
    elif len(args)>1:
      cmd, myargs = args
    
    if cmd and cmd!="show":
      my_cmd = "do_" + cmd
      try:
        method_to_call = getattr(self, my_cmd)
        method_to_call(myargs)
      except AttributeError:
        print(HTML('No such command <red>{}</red>'.format(cmd)))
    if ns_is_responding:
      result = json.loads(CONN.root.get("/ken"))["dfs"]
      self.print_dictionary(result)    
    

  def help_show(self):
    self.print_help('show [any_other_command]', 'Shows file system after performing any_other_command given.')

  def do_init(self, args):
    args = self.parse_args('init', args, 0, 1)
    
    if not ns_is_responding():  self.do_quit()

    result = {}
    if self.parse_path(self.CURRENT_DIR) != self.ABSOLUTE_ROOT:
      result["status"]=0
      result["message"] = "Can only initialize from root directory."
    else:
      if len(args)>0 and args[0]=="-force":
        result = json.loads(CONN.root.initialize(forced=True))
      else:
        result = json.loads(CONN.root.initialize())
        
    if result["status"]==1:
      result["message"] += "\n Available size: " + parse_size_from_bytes(1024*1024*1024*len(CONN.root.get_alive_servers()))
    self.print_response(result)

  def help_init(self):
    self.print_help('init [-force]', 'Initialize the file system. Use <red>-force</red> to delete everything and restart.')

  def parse_path(self, arg):
    if arg==".":
      return self.CURRENT_DIR
    elif arg == "..":
      arg = self.CURRENT_DIR.rsplit("/", 1)[0]
      return self.ABSOLUTE_ROOT if arg=="" else arg
    elif arg[:4]==self.ABSOLUTE_ROOT:
      # return absolute path, remove '/' at the end if there is.
      return arg[:-1] if arg[-1]=="/" else arg
    else:
      # parse relative path
      return os.path.join(self.CURRENT_DIR, arg)

  def do_cd(self, dir):
    args = self.parse_args('cd', dir, 1, 1)

    if not ns_is_responding():  self.do_quit()

    if args:
      arg = self.parse_path(args[0])
      print(HTML('Changing dir to: <green>{}</green>'.format(arg)))
      result = json.loads(CONN.root.get(arg))
      if result["status"]==1:
        try:
          blocks = result["data"]["blocks"]
          result["status"] = 0
          result["message"] = "Can't <b>cd</b> to a file."
          self.print_response(result)
        except:
          self.change_current_directory(arg)
      else:
        self.print_response(result)

  def help_cd(self):
    self.print_help('cd target_directory', 'Change current directory.')

  def do_ls(self, dir="."):
    args = self.parse_args('ls', dir, 0, 1)
    if args is None: return
    try:
      arg = self.parse_path(args[0])
    except IndexError:
      arg = self.parse_path(args)
    
    if not ns_is_responding():  self.do_quit()
    result = json.loads(CONN.root.get(arg))

    if result["status"]==1:
      try:
        blocks = result["data"]["blocks"]
        result["status"] = 0
        result["message"] = "Can't <b>ls</b> to a file."
        self.print_response(result)
      except:
        items = result["data"].keys()
        out = []
        for x in items:
          if x[:2]!="__":
            try:
              blocks = result["data"][x]["blocks"]
              out.append("<b>{}</b>".format(x))
            except:
              out.append("<b><green>{}</green></b>".format(x))
        if len(items)==0: out.append("<b>Empty directory!</b>")
        print(HTML("\t".join(out)))
    else:
      self.print_response(result)
      
  
  def help_ls(self):
    self.print_help('ls [target_directory]', 'List directory contents.')


  def do_mkdir(self, dir):
    args = self.parse_args('mkdir', dir, 1, 1)
    if not ns_is_responding():  self.do_quit()
    if args:
      arg = self.parse_path(args[0])
      print(arg)
      temp = json.loads(CONN.root.get(arg))
      if (temp["status"]==1):
        result = {
          "status": 0,
          "message": "Directory already exists!",
          "data": {}
        }
      else:
        result = json.loads(CONN.root.mkdir(arg))
      self.print_response(result)
      
  def help_mkdir(self):
    self.print_help('mkdir dir_name', 'Create new folder with given <orange>dir_name</orange>')

  def do_mkfiles(self, files):
    args = self.parse_args('mkfiles', files, 1)
    if not ns_is_responding():  self.do_quit()
    if args:
      for arg in tqdm(args):
        path = self.parse_path(arg)
        if path[-1]=="/": path = path[:-1]
        
        name = path.rsplit("/", 1)
        file = name[1].rsplit(".", 1)
        
        #print('Creating new file {} with extension {} at {}'.format(file[0], file[1], path))
        
        result = {}
        if len(file)!=2:
          result["status"]=0
          result["message"] = "Make sure file name is given with correct extension."
        else:
          result = json.loads(CONN.root.get(name[0]))
          if result["status"]==0:
            pass
          else:
            result = json.loads(CONN.root.new_file(path, []))
            if result["status"]==1:
              result["message"] = "New file created at {}".format(arg)      
        self.print_response(result)

  def help_mkfiles(self):
    self.print_help('mkfiles file1 [file2..]', 'Create new files with given names and extension.')
  
  def do_delete(self, files):
    args = self.parse_args('delete', files, 1)
    if args:
      if args[0] == "-force":
        force = True
        args = args[1:]
      else:
        force = False
      
      if not ns_is_responding():  self.do_quit()

      for arg in args:
        path = self.parse_path(arg)
        result = json.loads(CONN.root.delete(path, force_delete=force))
        
        if result["status"]==1:
          if path == self.parse_path(self.CURRENT_DIR):
            self.change_current_directory(self.ABSOLUTE_ROOT)

        self.print_response(result)

  def help_delete(self):
    self.print_help('delete [-force] file1 ... fileN', 'Delete files with given pathnames.\nUse <red>-force</red> to delete a file or directory with files inside.')

  def do_info(self, path):
    args = self.parse_args('info', path, 0, 1)
    arg = '.' if len(args)==0 else args[0]
    arg = self.parse_path(arg)

    if not ns_is_responding():  self.do_quit()

    res = json.loads(CONN.root.get(arg))
    if res["status"]==1:
      is_file = True if "blocks" in res["data"].keys() else False
      if is_file:
        blocks = res["data"]["blocks"]
        size_bytes = (len(blocks)-1) * int(res["nsconfig"]["block_size"]) if len(res["data"]["blocks"])>0 else 0
        target_ss = CONN.root.get_ss_having_this_block(blocks[-1])
        last_byte_size = None
        target_remote_path = self.parse_path(arg).rsplit("/", 1)[0]
        for ss in target_ss:
          try:
            block_path = os.path.join(target_remote_path, blocks[-1])
            data = get_from_ss(ss, block_path)
            last_byte_size = sys.getsizeof(data)
            break
          except:
            pass
        
        if last_byte_size is None:
          last_byte_size = int(res["nsconfig"]["block_size"])
        
        res["message"] = "This is a file. \nLocation: {}\nSize: {}".format(arg, parse_size_from_bytes(size_bytes + last_byte_size))
      else:
        keys = res["data"].keys()
        file_count = 0
        dir_count = 0
        for key in keys:
          if "blocks" in res["data"][key].keys():
            file_count += 1
          else:
            dir_count += 1
        #files_inside = CONN.root.files_in_directory(arg.split("/")[-1], res["data"])
        #res["message"] = "This is a directory.\n<green>Direct Subdirectories count</green>: {} \n<green>Direct files count</green>: {}\n<green>Total files inside</green>: {}".format(dir_count, file_count, None)
    self.print_response(res)

  def help_info(self):
    self.print_help('info [file_or_dir_path]', 'Output information of file/dir in given path.')


  def do_copy(self, args):
    args = self.parse_args('copy', args, 2, 2)
    if args:
      src = self.parse_path(args[0])
      dest = self.parse_path(args[1])

      if not ns_is_responding():  self.do_quit()

      result = json.loads(CONN.root.copy(src, dest))
      self.print_response(result)

  def help_copy(self):
    self.print_help('copy file_path target_dir', 'Copy a file to target directory.')

  def do_move(self, args):
    args = self.parse_args('move', args, 2, 2)
    if args:
      src = self.parse_path(args[0])
      dest = self.parse_path(args[1])

      if not ns_is_responding():  self.do_quit()

      result = json.loads(CONN.root.move(src, dest))
      if src == self.parse_path(self.CURRENT_DIR):
        self.change_current_directory(dest)
      self.print_response(result)

  def help_move(self):
    self.print_help('move source_path target_path', "Move file/contents from source_path to target_path.")


  def do_upload(self, args):
    args = self.parse_args('upload', args, 2, 2)
    if args:
      local_path = args[0]  #its local computer path
      remote_path = self.parse_path(args[1])
      
      if not ns_is_responding():  self.do_quit()
      res = json.loads(CONN.root.get(remote_path))
      
      result = {
        "status": 1
      }
      msg = []

      if not os.path.exists(local_path):
        result["status"]=0
        msg.append('No such resoure in local path!')
      
      if res["status"]==0:
        result["status"]=0
        msg.append('No such target remote directory!')
      
      if result["status"]==0:
        result["message"] = "\n".join(msg)
        self.print_response(result)
        return
      
      # get configurations
      replication_factor =  int(res["nsconfig"].get('replication_factor'))
      block_size = int(res["nsconfig"].get('block_size'))
      estimated_servers_need = os.path.getsize(local_path)/replication_factor

      if not ns_is_responding():  self.do_quit()
      storage_servers = CONN.root.get_alive_servers(estimated_servers_need + 4)

      ss_block_map = []
      total_size = os.path.getsize(local_path)
      blocks_len = math.ceil(total_size/block_size)
      print(HTML('File splitted into <green>{}</green> blocks.'.format(blocks_len)))
      done_size = 0
      with open(local_path, 'rb') as lf:
        buff = lf.read(block_size)
        i = 0
        while buff:
          i += 1
          print('Uploading block', i)
          block_name = str(uuid4())
          target_ss = random.sample(storage_servers, replication_factor) if len(storage_servers)>replication_factor else storage_servers
          
          for ss in tqdm(target_ss):
            put_in_ss(ss, remote_path, block_name, buff)
            done_size += block_size
            ss_block_map.append([ss, block_name])
          
          buff = lf.read(block_size)

      # send this block map to nameserver for storing
      if not ns_is_responding():  self.do_quit()
      local_path = local_path[:-1] if local_path[-1]=="/" else local_path
      try:
        file_name = local_path.rsplit("/", 1)[1]
      except IndexError:
        file_name = local_path
      
      file_name = os.path.join(remote_path, file_name)
      result = json.loads(CONN.root.new_file(file_name, ss_block_map))
      self.print_response(result)


  def help_upload(self):
    self.print_help("upload file_local_path target_dfs_directory", "Upload file from local file system to DFS.")

  def do_download(self, args):
    args = self.parse_args('download', args, 2, 2)
  
    if args:
      remote = self.parse_path(args[0])
      local = args[1]

      if not ns_is_responding():  self.do_quit()
      #print(remote)
      res = json.loads(CONN.root.get(remote))
      
      result = {
        "status": 1
      }
      msg = []

      if not os.path.exists(local):
        result["status"]=0
        msg.append('No such target local directory!')
      
      blocks = []
      if res["status"]==0:
        result["status"]=0
        msg.append('No such resource in remote path!')
      else:
        blocks = res["data"]["blocks"]
      
      if not blocks or len(blocks)==0:
        result["status"]=0
        msg.append('No file/empty file in given remote directory.')
      
      if result["status"]==0:
        result["message"] = "\n".join(msg)
        self.print_response(result)
        return
      
      out_fname = remote.rsplit("/", 1)[1]
      response = {
        "status": 1, "message": ""
      }
      target_out_file = os.path.join(local, out_fname)
      target_remote_path = remote.rsplit("/", 1)[0]
      print(HTML('<green>{}</green> blocks need to be fetched.'.format(len(blocks))))
      with open(target_out_file, "wb") as lf:
        i = 0
        for block_id in tqdm(blocks):
          i += 1
          target_ss = CONN.root.get_ss_having_this_block(block_id)
          data = None
          problematic_ss = []
          for ss in target_ss:
            try:
              block_path = os.path.join(target_remote_path, block_id)
              data = get_from_ss(ss, block_path)
              lf.write(data)
              #print(HTML('Block <b>{}</b> fetched.'.format(i)))
              break
            except:
              data = None
              problematic_ss.append(ss)
          
          if len(problematic_ss)>0 and data is None:
            print('Problematic storage servers were', problematic_ss)
          
          if not data:
            response["status"]=0
            response["message"]="At least 1 block missing! Can't retrieve the file."
            self.print_response(response)
            return

      response["message"] = "File saved to {}".format(local)
      self.print_response(response)
      

  def help_download(self):
    args = self.print_help('download file_dfs_path target_local_directory', "Download files from DFS to local system.")

  def do_refresh(self, args):
    args = self.parse_args('refresh', args, 0, 0)
    if args is not None:
      if not ns_is_responding():  self.do_quit()
      res = json.loads(CONN.root.refresh())
      self.print_response(res)

  def help_refresh(self):
    self.print_help("refresh", "Refresh DFS.")

  def default(self, inp):
    if inp=='x' or inp=='q':
      return self.do_quit(inp)
    else:
      print(HTML('"{}" is NOT a valid command! \n > Try <green>help</green> to see available commands.\n'.format(inp)))
  
  def emptyline(self):
    pass

  
def main(ns):
  global CONN
  global NS_IP, NS_PORT
  NS_IP = ns[0]
  NS_PORT = ns[1]

  if connect_to_ns():
    MyPrompt().cmdloop()
  

if __name__=='__main__':
  aws = ['3.134.8.132', 18861]
  local = ['localhost', 18860]
  main(aws)
