'''
    Name-server maintains a JSON object structure of our DFS.
        {
            "root": {
                "dir1": {
                    "myfile.pdf": {
                        "created": "date_time of creating",
                        "modified": "date_time of last modified",
                        "size": 258000,
                        "blocks": [
                            { uuid: "dfjkfsxkjlsdjf239", "__locations": [server1_ip, server2_ip] },
                            { uuid: "dfjkfsxkjlsdjf239", "__locations": [server1_ip, server2_ip] }
                        ]
                    }
                },
                "dir2": {}
            }
        }

    Use nested lookup: https://pypi.org/project/nested-lookup/
    Argument parser

    Assumptions:
      - Storage in storage servers is unlimited. Try put in nameservers one by one, if fail in all, then fail putting.

    Name-server will only act as a structure and a pointer, nothing more.
    
      - Client wants to get a file: contact nameserver, the ns will return the blocks mapping where they're located.
      Client will fetch those blocks and build the file on its own.

      - client wants to put a file: contacts nameserver asking list of alive storage servers and possibly the
    replication factor; client will directly put the files in those storage servers with replication too.
      
      - client wants to remove a file: Contacts nameserver asking for a list of storage servers with blocks; client
      deletes those blocks in all storage servers.

      - client wants to delete a dir: contacts nameserver; nameserver returns list of storage servers with all blocks FOR ALL FILES inside of it.
      client deletes those blocks all.

      - client wants to rename file/dir: contacts nameserver; nameserver simply renames in appropriate position in the structure


    Nameserver can interact with the storage servers in following ways:
      - ping periodically to see if they're alive.
      - ask the remaining storage capacity.
      - always return a json to client: { 'status': '1', data: { ..data here } }    # status 0 if some error and data contains error message, else data contains JSON.

    Client:
      - give commands
      - make PUT, GET, REMOVE requests to storage server, .
      - create empty file means just initialize with 0 blocks.
      - info query retrieves all blocks and sums up sizes for file_size.
      - return { 'status':1, data: { ..data } } to others on request

    Nameserver:
      - indexing of servers = dict({
          "192.168.0.0": { isAlive: True, capacity: 30000 },
          "192.168.0.1": { isAlive: False, capacity: 30000 },
          "192.168.0.2": { isAlive: True, capacity: 30000 }
      })    # save in storage_servers.txt
      - dfs structure with block --> server mapping     # save in dfs_structure.txt for convenience
      - just dump these files using pickle

      - check aliveness of a server every 10s, if one is down, copy its content to some other server.
      - return { 'status':1, action:'replicate', data: { ..data } } to client on request

    
    Storage servers:
      - contain folder with our dfs name in root directory:    root/ken
      - inside ken, just stores bin. blocks with name:   some_uuid.bin
      - return { 'status':1, data: { ..data } } to client on request

'''

import json
from functools import reduce
from operator import getitem
import rpyc

import uuid

REPILCATION_FACTOR = 2
SERVERS = {
    "name": ['127.0.0.1:18861'],
    "storage": ['127.0.0.1:18862']
}

class NameServerService(rpyc.Service):
    def on_connect(self, conn):
        # runs when a rpyc connection created to run the service
        print('Incoming connection from host: ')

    def on_disconnect(self, conn):
        # runs just before a rpyc connection is closed
        print('Disconnected from host: ')

    data = {}
    SPLIT_THRESHOLD = 1200000   # split if file size larger than this
    SPLIT_BLOCK_SIZE = 500000   # Each block will have a maximum size of this bytes

    def exposed_copy(self, src_path, dest_path):
        # if dir, just copy object structure, if files, copy that shit too. (if copy in same dir, add with _copy1)
        pass
        self.exposed_save()

    def exposed_move(self, src_path, dest_path):
        # just modify the obj
        pass
        self.exposed_save()

    def exposed_upload(self, path, file):
        # add an entry by calling add_file in the structure
        # chose servers based on R, put file there and ask it to pass it to next.
        pass

    def exposed_download(self, path):
        # download file in given path from one of the available servers.
        pass

    def __init__(self):
        self.exposed_refresh()
        print('Name server started...')
    
    def exposed_initialize(self):
        self.data = {
            "root": {}
        }
        self.exposed_save()
        return 'DFS initialized.'

    def exposed_refresh(self):
        with open("ken_dir_mapper.txt", 'r') as input_file:
            self.data = json.load(input_file)

    def url2list(self, url_name):
        names = url_name.strip().split("/")
        return names[:-1] if names[-1]=="" else names

    def exposed_show(self):
        return json.dumps(self.data, indent=4, sort_keys=True)

    # 'name' should include path + file/dir name
    def add(self, names, is_file=False, serv_addrs=None):
        names = self.url2list(names)

        data = self.data
        for n in names:
            try:
                data = data[n]
            except:
                data[n] = {}
                data = data[n]
        
        if is_file:
            # if file already contains, just append server address list to include new ones
            try:
                s = data['__locations']
                data['__locations'] = s + list(set(serv_addrs) - set(s))
            except:
                data['__locations'] = serv_addrs
            
            # now call server(s) to create the file
        
        self.exposed_save()
            

    def exposed_add_file(self, name, serv_addrs):
        self.add(name, True, serv_addrs)

    def exposed_add_dir(self, name):
        self.add(name, False)

    def exposed_rename(self, old_path_name, new_name):
        paths = self.url2list(old_path_name)
        parent = reduce(getitem, paths[:-1], self.data)
        parent[new_name] = parent.pop(paths[-1])

        self.exposed_save()


    def exposed_remove(self, name, serv_addrs=[]):
        paths = self.url2list(name)
        
        parent = reduce(getitem, paths[:-1], self.data)

        serv = parent[paths[-1]].get('__locations')
        if serv:
            serv = [item for item in serv if item not in serv_addrs]
            # if 0 associated servers after removing given list of servers, remove file/dir entirely from mapping
            if len(serv)==0:
                del parent[paths[-1]]
            else:
                parent[paths[-1]]['__locations'] = serv         
        else:
            # if it's a directory
            del parent[paths[-1]]
        
        self.exposed_save()


    # return list of servers if name is a file, empty list if its a dir, None if error
    def exposed_get(self, names):
        names = self.url2list(names)

        try:
            result = reduce(getitem, names, self.data)
        except (KeyError,TypeError):
            print('Requested resource not found! Invalid path name or file does not exist in given path.')
            return None
        
        try:
            return result["__locations"]
        except:
            return []

        # if 'usr/abc' is not in server1, then 'user/abc/a.txt' or anything 'usr/abc/*' is not in server1

    def exposed_ls(self, path):
        names = self.url2list(path)

        try:
            inst = reduce(getitem, names, self.data)
            return "\t".join(x for x in inst.keys())
        except (KeyError,TypeError):
            return 'Invalid path name: some dirs do not exist in given path.'
    
    # Split given file and returns the block object with ID and data
    def split_file(self, f):
        blocks = []
        with open(f, 'rb') as file:
            bytes = f.read(self.SPLIT_BLOCK_SIZE)
            while bytes:
                blocks.append({
                    'id': uuid.uuid1(),
                    'data': bytes
                })
                bytes = f.read(self.SPLIT_BLOCK_SIZE)
        return blocks


    def exposed_save(self):
        with open("ken_dir_mapper.txt", "w") as output_file:
            json.dump(self.data, output_file)


if __name__=="__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(NameServerService(), port=18861)
    t.start()
    