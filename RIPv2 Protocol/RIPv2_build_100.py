#####################################
###  Ahmad Alsaleh (ID: 14749959) ###
###  Chadol Han (ID: 79364948)    ###
###  COSC364 Assignment 1         ###
###  Routing Demon RIPv2          ###
#####################################

#Importing modules
import os
import socket
import select
import sys
import queue
import time
import random

my_id = -1      #Global variable for router ID
output_p = {}   #Dictionary for output ports, k = port number, v = peer router
input_p = []    #Input ports list

def show_table(table):
    '''Function to print the table in the terminal in a visible format'''
    
    router_ids = sorted(table.keys())
    table_length = len(table)
    
    ##########################    TABLE FORMATTING    ##########################
    print("\n\nRouter ID: {0}".format(my_id))
    print("│ ID │ Next Hop │ Cost │Time Out │")
  
    for i in range(0, table_length):
        info = table[router_ids[i]]
        print("│ {:>2} │".format(router_ids[i]), end='')
        print(" {:>6}   │ {:>2}   │ {:<8.4f}│"\
              .format(info[0], info[1], float(str(info[3][0])[:8])))
    print("\n") 
    #Don't need to show input ports, too messy and dont need to see
    #print("Input ports currently active for router: {0}".format(my_id))
    #print(input_p)
    print("\n")
    print("Output ports | Peer router")
    for k, v in output_p.items():
        print("   ", k, "    |     ", v)
    print("\n")
    ##########################    TABLE FORMATTING    ##########################
        
def state_firsthop(f_router, table):
    '''Function that returns the routers in which the routes in the routing
    table use the input f_router as first hop'''
    
    routers = []
    router_ids = sorted(table.keys())
    for router in router_ids:
        if table[router][0] == f_router:
            routers.append(router)
    return routers

def rtable_build(filename):
    '''Function that reads the config text files (which contain the ports,
    metrics) and creates the routing table from the information inside'''
    
    global my_id
    total = []
    table = {}
    
    ##########################   READING CONFIG FILE  ##########################
    config = open(filename, 'r')
    for i in config.readlines():
        i = i.split(', ')
        total.append(i)
    ##########################   READING CONFIG FILE  ##########################
    
    my_id = int(total[0][1])
        
    for i in range(1, len(total[1])):
        input_p.append(int(total[1][i]))

    for i in range(1,len(total[2])):
        temp = total[2][i]
        temp = temp.split('-')
        router_id = int(temp[-1])
        port_num = int(temp[0])
        output_p[port_num] = router_id
        f_router = router_id
        cost = int(temp[-2])
        flag = False
        timers = [0, 0]
        table[router_id] = [f_router, cost, flag, timers]
    return table

def check_key_routerid(table):
    '''Returns the routerid's in a list from the routing table by reading the
    keys from the dictionary of the routing table'''
    
    routerid_keys = []
    t = table
    empty = None
    
    if t != empty:
        
        for y in t.keys():
            routerid_keys.append(y)
        #print(routerid_keys)
        return routerid_keys
    
    else:
        #print(routerid_keys)
        return routerid_keys


def listenlist(): 
    '''Function that binds the ports from the config file to sockets to which
    we need to listen'''
    llist = []
    input_port_length = len(input_p)
    ##########################     BINDING PORTS      ##########################
    
    for i in range(0, input_port_length):
        #Create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #Bind to port
        sock.bind(('localhost', int(input_p[i]) ))        
        llist.append(sock)
    return llist
    
    ##########################     BINDING PORTS      ##########################

        
def id_checker(routerid_check, table):
    '''Function that takes the routerid as an input and checks whether it 
    matches/exists in the routing table'''
    key = check_key_routerid(table)
    
    if routerid_check in key:
        return True 
    else:
        return False


def receiver(r_table, timeout):
    '''Function that checks if messages have been received on the sockets'''
    
    socket_list = listenlist() 
    table_key = []
    table = r_table
    a,b,c = select.select(socket_list,[],[], timeout)
    
    if a != []:
        s = a[0]
        s.settimeout(7)
        #Receive the data
        data, addr = s.recvfrom(1024) #Buffer size is 1024 bytes
        data = str(data)
        data = data.replace("b","").replace("'","")
        data = data.split(',')
        src = int(data[2])
        #print("Data received from router ID: {}".format(src))
        start = 3
        print(data)
        while start < len(data):
            routerid_check = int(data[start]) 
            router_id = int(data[start])
            
            try:
                if src in table:
                    cost = min(int(data[start + 1]) + table[src][1], 16)
                else:
                    print("ERROR")
                    cost = 16
            except:
                print("ERROR: ERROR WITH COSTS")
            
            if cost not in range(0,17):
                print("Packet is invalid: Cost not in range 0-16")
                while 1:
                    continue
    
            #CONTINUE FROM HERE
            if router_id not in output_p.values() and router_id != my_id:
                if not id_checker(routerid_check, table):
                    #If the route is not registered to our routing table
                    #and IS reachable, add it to the routing table
                    table[router_id] = [src, cost, False, [0,0]]
            
                if (cost < table[router_id][1]):
                    #Better route is found
                    table[router_id][1] = cost 
                    table[router_id][0] = src
            
                if (src == table[router_id][0]):
                    #Submitting to the info the router gives us if they 
                    #are the first hop to the destination
                    table[router_id][1] = cost 
                    table[router_id][0] = src
                    table[router_id][-1][0] = 0
                    table[router_id][-1][1] = 0
                    table[router_id][2] = False
            
            start += 2

            
        if src in table:
            table[src][-1][0] = 0       #Resets timer
            table[src][-1][1] = 0
            table[src][2] = False        #Sets flag to false
    return table

def create_message(table, port):
    '''Function that creates a message that contains a dictionary representing
    the routing table and where it is being sent (port number)'''

    t = table
    command = "2"
    version = "2"
    source = my_id
    key = check_key_routerid(t)
    head = command + ',' + version + ','+ str(source)
    final = head
   
    for v in key:
        value = t[v]
        final += ',' + str(v) + ','
        cost = str(value[1]) if v not in t.values() else 16
        final += cost
    #print(final)
    return final

def send_msg(table):
    '''Function to send message with updates to all neighbours'''
    
    #Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
    
    for port in output_p:  
        msg = create_message(table, port)
        msg = msg.encode('utf-8')
        #Sending the data
        sock.sendto(msg, ("localhost", port))
        #print(msg)


def timer_update(table, time):
    '''Function to add time to routing table entry timers'''
    
    timeout_error = 15 #Timeout duration till it cuts off
    garbage_collection_timeout = 10
    for key in sorted(table.keys()):
        if table[key][2]:
            table[key][-1][1] += time
            if table[key][-1][1] > garbage_collection_timeout:
                del table[key]
        else:
            table[key][-1][0] += time
            if table[key][-1][0] > timeout_error:
                table[key][1] = 16
                table[key][2] = True
                for router in state_firsthop(key, table):
                    table[router][1] = 16
        #print(key)
        #print(table)
        #print(time) ERRORRRRR
        

