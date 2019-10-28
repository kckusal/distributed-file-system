'''
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

'''

import sys
import rpyc

class ClientService:
    def __init__(self):
        pass
    
    def connect_ns(self):
        # connect to the nameserver and return the connection, return None on exception
        try:
            return rpyc.connect('127.0.0.1', port=18861)
        except:
            return None

        pass

    def query(self, name):
        pass

    def send(self, name):
        pass

    def get(self, name):
        pass


def main():
    args = sys.argv[1:]

    print('\nConnecting to the nameserver...')
    client = ClientService()
    
    try:
        ns = client.connect_ns().root
        print('\nSuccessfully connected to the nameserver!')
    except:
        print('\nFailed to connect to the nameserver! Try again!\n')
        sys.exit(0)
    
    
    if len(args)==2 and args[0]=='ken' and args[1]=='connect':
        current = "root"
        while True:
            args = raw_input("\n>>> ken: ({}) $  ".format(current))
            args = args.strip().split(" ")
            args = [ current if x=="." else x for x in args ]   # change . arguments with current directory reference.
            #print(args)

            if len(args)==1:
                arg = args[0]

                if arg=="exit":
                    break
                elif arg=="refresh":
                    ns.refresh()
                    main()
                    break
                elif arg=="initialize":
                    ns.initialize()    # initialize dfs here
                elif arg=="ls":
                    #conn.get(current)      get all attributes in current directory
                    print(ns.ls(current))
                else:
                    print("Invalid command. Try 'help' command to learn usage.")

            elif len(args)==2:
                if args[0]=="cd":
                    # get current dir from structure, if curr exists then make current = args[1], else print error
                    if ns.get(args[1]) is None:
                        print('Invalid path name: some dirs do not exist in given path.')
                    else:
                        current = args[1]

                elif args[0]=="info":
                    # get info of dir args[1]
                    pass

                elif args[0]=="remove":
                    # remove dir args[1]
                    pass

                else:
                    print("Invalid command. Try 'help' command to learn usage.")

            elif len(args)==3:
                if args[0]=="put":
                    # do upload task here
                    pass
                elif args[0]=="get":
                    # do download task here
                    pass
                else:
                    print("Invalid command. Try 'help' command to learn usage.")
                
            elif len(args)==4:
                if args[0]=="create":
                    
                    if args[1]=="-f" or args[1]=="-d":
                        is_file = True if args[1]=="-f" else False

                        # create file/dir inside of dir given by arg[2], arg[3] is the name of file/dir
                        # cd to arg[2] after done.

                    else:
                        print("Invalid command. Try 'help' command to learn usage.")

                else:
                    print("Invalid command. Try 'help' command to learn usage.")

            else:
                print("Invalid command. Try 'help' command to learn usage.")
            
        
    else:
        print('Try command "ken connect" to start using your Distributed File System.')


if __name__ == "__main__":
    main()