'''
Created on Oct 2, 2015

@author: Sjors.Ruijgrok
'''

import bluetooth


class Bluetooth(object):
    '''
    Class for setting up a Bluetooth connection.
    For now only RFCOMM client connection is supported.
    
    NOTE: It's not allowed to use "bluetooth.py" as module-name because the pybluez-lib already
          got a python-module with this name.
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self._server_sock = None
        self._client_sock = None
    
    
    def findDevices(self, get_names = False):
        print "Searching for bluetooth devices ..."
        nearby_devices = bluetooth.discover_devices(lookup_names = get_names)

        print "Found %d Bluetooth-devices" % len(nearby_devices)
        if get_names:
            for addr, name in nearby_devices:
                print '  %s - %s' % (addr, name)
        else:
            for addr in nearby_devices:
                print '  %s' % addr
            
        
        return nearby_devices
    
    
    def findServices(self, addr):
        print "\rGetting services from %s ..." % addr
        services = bluetooth.find_service(address = addr)
        
        if len(services) > 0:
            print "Found %d service(s)" % len(services)
        else:
            print "No services found"
        
        for svc in services:
            print "  Name:        %s" % svc["name"]
            print "  Host:        %s" % svc["host"]
            print "  Description: %s" % svc["description"]
            print "  Provided By: %s" % svc["provider"]
            print "  Protocol:    %s" % svc["protocol"]
            print "  channel/PSM: %s" % svc["port"]
            print "  svc classes: %s" % svc["service-classes"]
            print "  profiles:    %s" % svc["profiles"]
            print "  service id:  %s" % svc["service-id"]
        
        return services
    
    
    def connectClient_RFCOMM(self, services):
        if len(services) <= 0:
            print "\rCan't make connection - no services specified"
            return None
        
        # NOTE: Here it's assumed that the first (and probably the only) service in list is the Serial Port Protocol.
        first_match = services[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]
        
        print "\rConnecting to \"%s\" on %s" % (name, host)
        
        # Create the client socket
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((host, port))
        
        print "Connected!"
        print "\r"
        
        return socket
    
    
    def sendClient(self, socket = None, data = []):
        if len(data) > 0 and socket != None:
            print data
            socket.send(data)
    
    
    def receiveClient(self, socket = None, size = 0):
        data = []
        if socket != None and size > 0:
            # TODO: Implement timeout
            try:
                for _ in xrange(size):
                    # TODO: Get all data at once and parse as string (?)
                    new_data = socket.recv(1)
                    if new_data != None:
                        data.append(new_data)
                        print new_data.encode('hex'), '-', new_data
                if len(data) != size:
                    print 'Data-size mismatch (requested: %d, received: %d)' % (size, len(data))
            except Exception as e:
                print e
        
        return data
    
    
    def connectServer_RFCOMM(self):
        '''
        This is just an example from: https://github.com/karulis/pybluez
        It's not tested yet.
        '''
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", bluetooth.PORT_ANY))
        server_sock.listen(1)
        
        port = server_sock.getsockname()[1]
        
        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        
        bluetooth.advertise_service( server_sock, "SampleServer",
                           service_id = uuid,
                           service_classes = [ uuid, bluetooth.SERIAL_PORT_CLASS ],
                           profiles = [ bluetooth.SERIAL_PORT_PROFILE ], 
        #                   protocols = [ OBEX_UUID ] 
                            )
        
        print "Waiting for connection on RFCOMM channel %d" % port
        
        client_sock, client_info = server_sock.accept()
        print "Accepted connection from ", client_info
        
        try:
            while True:
                data = client_sock.recv(1024)
                if len(data) == 0: break
                print "received [%s]" % data
        except IOError:
            pass
        
        print "disconnected"
        
        client_sock.close()
        server_sock.close()
        print "all done"
