from OSC import OSCServer
import sys
from time import sleep

server = OSCServer( ("localhost", 7110) )
server.timeout = 0
run = True

def user_callback(path, tags, args, source):
    # which user will be determined by path:
    # we just throw away all slashes and join together what's left
    user = ''.join(path.split("/"))
    # tags will contain 'fff'
    # args is a OSCMessage with data
    # source is where the message came from (in case you need to reply)
    print user, args, source 
    
for i in range(2):
    for c in range(1,5):
        server.addMsgHandler( "/EEG_%d/channel_%d/notch_50/lpf_75"%(i,c), user_callback )
    server.addMsgHandler( "/markers" , user_callback )    
server.serve_forever()