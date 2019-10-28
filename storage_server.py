import rpyc

REPILCATION_FACTOR = 2
SERVERS = {
    "name": ['127.0.0.1:18861'],
    "storage": ['127.0.0.1:18862']
}

class StorageServerService(rpyc.Service):
    def on_connect(self, conn):
        # runs when a connection is made to this service
        print('Incoming connection from host: ')

    def on_disconnect(self, conn):
        # run just before disconnecting
        print('Disconnected from host: ')

    def exposed_get_answer(self): # this is an exposed method
        return 42

    exposed_the_real_answer_though = 43     # an exposed attribute

    def get_question(self):  # while this method is not exposed
        return "what is the airspeed velocity of an unladen swallow?"


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    # Expose my service to the world through this port
    t = ThreadedServer(StorageServerService, port=18861)
    t.start()