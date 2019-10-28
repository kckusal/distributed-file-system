'''
    Name-server maintains a JSON object structure of our DFS.
        dfs = {
            "root": {
                "dir1": {
                    "myfile.pdf": {
                        "__locations": [server1_ip, server2_ip]
                    }
                },
                "dir2": {}
            }
        }
'''

import json
from functools import reduce
from operator import getitem
import rpyc

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
        

    def exposed_save(self):
        with open("ken_dir_mapper.txt", "w") as output_file:
            json.dump(self.data, output_file)


if __name__=="__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(NameServerService(), port=18861)
    t.start()
    