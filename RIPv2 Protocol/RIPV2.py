#####################################
###  Ahmad Alsaleh (ID: 14749959) ###
###  Chadol Han (ID: 79364948)    ###
###  COSC364 Assignment 1         ###
###  Routing Demon RIPv2          ###
#####################################

from RIPv2_build_100 import *
def main():
    try:
        r_table = rtable_build(sys.argv[1]) 
        #List index out of range. Still works
        #Attempt to fix by limiting arguments
        while True:
            max_time = 2 + random.randint(-2,2)
            timeout = max_time
            rec = time.time()
            elapsed = rec - time.time()
            timer_incr = 0
        
            while elapsed < max_time:
                r_table = receiver(r_table, timeout) 
                timer_incr = time.time() - rec
                rec = time.time()
                timer_update(r_table, timer_incr)
                elapsed += timer_incr
                timeout = max(max_time - elapsed, 0)
        
            show_table(r_table)
            send_msg(r_table)
    #If control-c pressed, stop the loop for 100 seconds
    except KeyboardInterrupt:
        time.sleep(100)
       
if __name__ == "__main__":
    main()
    
'''Final checks'''
#Check routing table 3, 5, 4, 7 Seems like 4 and 7 arent connecting
#Fixed connection between 4 and 7
#Address being used, socket error. Reset sockets?
#Changed ports > workaround to error
    