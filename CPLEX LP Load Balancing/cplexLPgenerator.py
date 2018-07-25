################################################################################
#### COSC364 Assignment 2
#### The following is a program which creates an LP file to be read on cplex
#### Ahmad Alsaleh (ID: 14749959) | Chadol Han (ID: 
################################################################################
import codecs
import subprocess
import time
#GLOBALS
global X
global Y
global Z
#Creates LP file
f = open("LPfile.lp","w+")

#Used to check for input positive integers error
class Error(UserWarning):
    pass

#Indenting string recipe, taken from http://code.activestate.com/recipes/576867-indent-a-string/
def indent(txt, stops=1):
    return '\n'.join(" " * 4 * stops + line for line in  txt.splitlines())


def write_initial():
    """"Function that writes required text to LP file"""
    f.write("Minimize\n")
    f.write(indent('r'))
    f.write("\nSubject to\n")
    
def inputs():
    """"Function that asks the user for the amount of nodes required and 
    checks whether they are positive integers"""
    while 1:
        try:
            global X
            global Y
            global Z
            source_nodes = input("Enter amount of source nodes: ")
            transit_nodes = input("Enter amount of transit nodes: ")
            destination_nodes = input("Enter amount of destination nodes: ")            
            X = int(source_nodes)
            Y = int(transit_nodes)
            Z = int(destination_nodes)        
            if X <= 0:
                raise Error
            elif Y <= 0:
                raise Error            
            elif Z <= 0:
                raise Error
        except Error:
            print("Nodes only accept positive integers, please try again!")
            continue
        except ValueError:
            print("The inputs must be a number, try again!")
            continue
        else:
            break
 
def write_demand_volume(source, transit, destination):
    """writes the demand volume from i to j to the LP file"""
    for i in range(1,source+1):  
        string = ""
        for k in range(1,destination+1):
            string = ""
            for j in range(1,transit+1):
                string += "x" + str(i) + str(j) + str(k) + " + "
                h = i + k
            f.write(indent(string[:-2] + "= {}".format(h))+"\n")
                    

def write_utilsation_u(source, transit, destination):
    """writes utilisation constraints for the transit nodes to the LP file"""
    for i in range(1,source+1):  
        string = ""
        for k in range(1,destination+1):
            string = ""
            for j in range(1,transit+1):
                string += "u" + str(i) + str(j) + str(k) + " + "
                n_k = 3
            f.write(indent(string[:-2] + "= {}".format(n_k)) + "\n")


def write_demand_flow(source, transit, destination):   
    """writes demand flow from i to j to the LP file"""
    for i in range(1,source+1):
            string = ""
            for j in range(1,transit+1):
                string = ""
                for k in range(1,destination+1):
                    h = i + k
                    string += "3 x" + str(i) + str(j) + str(k) + " - " + str(h) + " u" + str(i) + str(j) + str(k) + " = 0"
                    f.write(indent(string) + "\n")
                    string = ""    


def write_source_constraint(source, transit, destination): 
    """writes capacity constraints from source to transit to the LP file"""
    for i in range(1,source+1):  
        string = ""
        for j in range(1,transit+1):
            string = ""
            for k in range(1,destination+1):
                string += "x" + str(i) + str(j) + str(k) + " + " 
            f.write(indent(string[:-2] + "- c" + str(i) + str(j) + " = 0") + "\n")  
    
    
def write_destination_constraint(source, transit, destination):  
    """writes capacity constraints from transit to destination to the LP file"""
    for k in range(1,destination+1):  
        string = ""
        for j in range(1,transit+1):
            string = ""
            for i in range(1,source+1):
                string += "x" + str(i) + str(j) + str(k) + " + " 
            f.write(indent(string[:-2] + "- d" + str(j) + str(k) + " = 0") + "\n")  
            
            
def write_transit_constraints(source, transit, destination):
    """writes transit constraints to the LP file"""
    for j in range(1,transit+1):  
        string = ""
        for i in range(1,source+1):
            for k in range(1,destination+1):
                string += "x" + str(i) + str(j) + str(k) + " + "
        f.write(indent(string[:-2] + "- r <= 0") + "\n")

def write_totalflow_S_to_T(source, transit, destination):
    """Amount of flow on a given link (source to transit)"""
    for i in range(1,source+1):  
        string = ""
        for j in range(1,transit+1):
            string = ""
            for k in range(1,destination+1):
                string += "x" + str(i) + str(j) + str(k) + " + " 
            f.write(indent(string[:-2] + "- y" + str(i) + str(j) + " = 0") + "\n")    
  
def write_totalflow_T_to_D(source, transit, destination):
    """Amount of flow on a given link (transit to destination)"""
    for k in range(1,destination+1):  
        string = ""
        for j in range(1,transit+1):
            string = ""
            for i in range(1,source+1):
                string += "x" + str(i) + str(j) + str(k) + " + " 
            f.write(indent(string[:-2] + "- y" + str(j) + str(k) + " = 0") + "\n")     

def write_totalflowconstraint_S_to_T(source, transit):
    """Flow on link (from source to transit) constraint"""
    for i in range(1,source+1):  
        string = ""
        for k in range(1,transit+1):
            string += "y" + str(i) + str(k) + " - " + "c" + str(i) + str(k)
            f.write(indent(string + " <= 0") +"\n")   
            string = ""
    
def write_totalflowconstraint_T_to_D(transit, destination):
    """Flow on link (from transit to destination) constraint"""
    for i in range(1,transit+1):  
        string = ""
        for k in range(1,destination+1):
            string += "y" + str(i) + str(k) + " - " + "d" + str(i) + str(k)
            f.write(indent(string + " <= 0") +"\n")   
            string = ""    

def write_totalflow_transit_constraint(source, transit):
    """ """
    for j in range(1,transit+1):  
        string = ""
        for i in range(1,source+1):
            string += "y" + str(i) + str(j) + " + "
        f.write(indent(string[:-2] + "- r <= 0") + "\n")
        
def write_path_flow_bounds(source, transit, destination):
    """writes bounds for the path flow (non-negativity)"""
    f.write("\nBounds\n")
    f.write(indent("r >=0") + "\n")    
    for i in range(1,source+1):  
        string = ""
        for j in range(1,transit+1):
            string = ""
            for k in range(1,destination+1):
                string += "x" + str(i) + str(j) + str(k) + " + "
                f.write(indent(string[:-2] + ">= 0") + "\n")    
                string = ""
          
def write_capacity_S_to_T(source, transit):
    """writes bounds for the capacity c from source to transit(non-negativity)"""
    for i in range(1,source+1):  
        string = ""
        for j in range(1,transit+1):
            string += "c" + str(i) + str(j) 
            f.write(indent(string + " >= 0") + "\n")
            string = ""
            
def write_capacity_T_to_D(transit, destination):
    """writes bounds for the capacity d from transit to dest(non-negativity)"""
    for j in range(1,transit+1):  
        string = ""
        for k in range(1,destination+1):
            string += "d" + str(j) + str(k) 
            f.write(indent(string + " >= 0") + "\n")
            string = ""  

def write_linkflow_bound_S_to_T(source, transit):
    """writes bounds for the linkflow from source to transit(non-negativity)"""
    for i in range(1,source+1):  
        string = ""
        for j in range(1,transit+1):
            string += "y" + str(i) + str(j) 
            f.write(indent(string + " >= 0") + "\n")
            string = ""
            
def write_linkflow_bound_T_to_D(transit, destination):
    """writes bounds for the linkflow from transit to destination(non-negativity)"""
    for j in range(1,transit+1):  
        string = ""
        for k in range(1,destination+1):
            string += "y" + str(j) + str(k) 
            f.write(indent(string + " >= 0") + "\n")
            string = "" 
            
def write_to_binary(source, transit, destination):
    """writes the binary values and adds an end so the LP file ends"""
    f.write("\n\nBinary\n")
    for i in range(1,source+1):  
        string = ""
        for j in range(1,transit+1):
            string = ""
            for k in range(1,destination+1):
                string += "u" + str(i) + str(j) + str(k)
                f.write(indent(string) + "\n")    
                string = ""    
    f.write("End")    
    
    
def run_in_cplex(file):
    """The following function runs the LP file created by this program
    into CPLEX, CPLEX then reads it and optimizes it"""
    #Add "display solution variables -" after optimize to show solutions
    #It was removed so the execution time could be properly calculated
    proc = subprocess.Popen(["./cplex"] + ["-c", "read", file, "optimize", "display solution variables -"], stdout=subprocess.PIPE)
    out,err = proc.communicate()
    result = out.decode("utf-8")
    return result

def main():
    write_initial()
    inputs()
    write_demand_volume(X,Y,Z)
    f.write("\n")    
    write_utilsation_u(X,Y,Z)
    f.write("\n")    
    write_demand_flow(X, Y, Z)
    f.write("\n")    
    write_source_constraint(X,Y,Z)
    f.write("\n")
    write_destination_constraint(X, Y, Z)
    f.write("\n")
    write_transit_constraints(X, Y, Z)
    f.write("\n")
    write_totalflow_S_to_T(X, Y, Z)
    f.write("\n")
    write_totalflow_T_to_D(X, Y, Z)  
    f.write("\n")
    write_totalflow_transit_constraint(X, Y)
    f.write("\n")
    write_totalflowconstraint_S_to_T(X, Y)
    f.write("\n")
    write_totalflowconstraint_T_to_D(Y, Z)
    write_path_flow_bounds(X, Y, Z)
    write_capacity_S_to_T(X, Y)
    write_capacity_T_to_D(Y, Z)
    write_linkflow_bound_S_to_T(X, Y)
    write_linkflow_bound_T_to_D(Y, Z)
    write_to_binary(X, Y, Z)

    #Close file
    f.close()
    
    #To time the execution time
    before = time.time()
    print(run_in_cplex("LPfile.lp"))
    elapsed_time = time.time() - before
    print(elapsed_time)
        
if __name__ == "__main__":
    main()  