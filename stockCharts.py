from importlib.resources import contents
import numpy as np
from time import time
import math
from tkinter import N
from xml.dom.minicompat import NodeList
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import xlsxwriter
import sys
np.set_printoptions(threshold=sys.maxsize) #print all numpy liness without truncation
#------------------
lines=[]
entryname=''
n=0
#------------------
class Graph:
    def __init__(self,graph): #initial method for create graph
        self.graph = graph
        self.line = len(graph)
        self.lines = len(graph[0])
 
    def bpm(self, u, matchR, seen): #create bipartie matching for graph , recursive function that returns true if a matching for vertex u is possible
 
        # Try every line one by one
        for v in range(self.lines):
 
            # If line u is interested in line v and v is not seen
            if self.graph[u][v] and seen[v] == False:
                seen[v] = True
                if matchR[v] == -1 or self.bpm(matchR[v], matchR, seen):
                    matchR[v] = u
                    return True
        return False
 
    
    def MaximumBipartieMatching(self): # max bipartie matching 
        matchR = [-1] * self.lines #first iteration we have no matching for each line 
         
        # Count of lines matching to line
        result = 0
        for i in range(self.line):
             
            # Mark all lines as not seen for next line.
            seen = [False] * self.lines
             
            # Find if the line 'u' can get a line
            if self.bpm(i, matchR, seen):
                result += 1
        return result,matchR
#------------------
def create_file(name):
    workbook = xlsxwriter.Workbook('E:/master99/3/optimization_algo/HW/hw4/stock_charts/results/'+name+'.xlsx')
    worksheet = workbook.add_worksheet(name)

    worksheet.write('A1', 'File Name')
    worksheet.write('B1', 'N')
    worksheet.write('C1', 'K')
    worksheet.write('D1', 'overlaid charts')
    worksheet.write('E1', 'expected result')
    worksheet.write('F1', 'Execution Time')

    return workbook, worksheet
#------------------
def write_to_file(workbook, worksheet,filename,n,k,overlaids, exresult,exectime,i):
    worksheet.write('A' + str(i+2), filename)
    worksheet.write('B' + str(i+2), n)
    worksheet.write('C' + str(i+2), k)
    worksheet.write('D' + str(i+2), overlaids)
    worksheet.write('E' + str(i+2), exresult)
    worksheet.write('F' + str(i+2), exectime)
#------------------
def main():
    global lines
    global n
    global entryname
    entries = Path('E:/master99/3/optimization_algo/HW/hw4/stock_charts/Instances')
    results = Path('E:/master99/3/optimization_algo/HW/hw4/stock_charts/expected_results')
    index=0
    exresult=0
    wb, ws = create_file("stock_charts")
    for entry in entries.iterdir():
        entryname=entry.name
        lines=[]
        
        print ("----------------------")
        print("entry name:"+entry.name)
        f = open('E:/master99/3/optimization_algo/HW/hw4/stock_charts/Instances/'+entry.name, "r")
        line1=f.readline().split()
        n=int(line1[0])
        k=int(line1[1])

        for i in range(n):
            line=f.readline().split()
            linelist=list(map(int, line))
            lines.append(linelist)

        start=time()

        matchinglines = [[] for _ in range(n)] #for each line we have list of lines matchs by this line
        for i in range(n): #create edges between matching lines 
                for j in range(n):
                    if all(a < b for (a, b) in zip(lines[i], lines[j])): #each line is node in graph
                        matchinglines[i].append(j)
        edges=np.zeros((n,n))
        for i,nodelist in enumerate(matchinglines): #if we have edge between line i,n (each line is one node in graph ) then set temp[i,n]=1
            for node in nodelist:
                edges[i,node]=1
        g = Graph(edges)


        overlaidlist = [[] for _ in range(n)] #calculate overlaids
        match=g.MaximumBipartieMatching()[1]
        visited = [False for i in range(n)]
        xlist=[]
        for i in range(n):
            xlist.append(i)
            x=i
            while len(xlist)>0 :
                x=xlist.pop(0)
                if x==i and visited[i]==True:
                    break
                visited[x]=True
                overlaidlist[i].append(x)
                tmp=match[x]
                if tmp!=-1 and visited[tmp]==False:
                    xlist.append(tmp)
                    visited[tmp]=True
                for k in range(i,n):
                    if match[k]== x and visited[k]==False:
                        xlist.append(k)
                        visited[k]=True
                        break
                match[x]=-1
            
        for i in range(n):#add alone lines to overlaidlist
            if visited[i]==False:
                overlaidlist.append(i)

        overlaidlist = [x for x in overlaidlist if x != []] #remove empty lists in overlaid list

        end=time()
        executiontime=end-start
        print("execution time:",executiontime)
        print("overlaids:",len(overlaidlist))
        print('charts: ',overlaidlist)
                

        #representation
        with open('E:/master99/3/optimization_algo/HW/hw4/stock_charts/charts/'+entryname+'.txt' , 'w' , encoding='utf-8') as f: #cleare file 
            f.write("max matching: ")
            f.write(str(g.MaximumBipartieMatching()[0]))
            f.write("\n")
            f.write("overlaids: ")
            f.write(str(len(overlaidlist)))
            f.write("\n\n\n")
            f.write("overlaidlist:")
            f.write("\n")
            f.write(str(overlaidlist))
            f.write("\n\n\n")
            f.close
        with open('E:/master99/3/optimization_algo/HW/hw4/stock_charts/charts/'+entryname+'.txt' ,'a', encoding='utf-8') as f: #appends to file 
            # f.write("edges:") #matchings 
            # f.write("\n")
            # f.write(str(edges))
            # f.write("\n\n\n")
            f.write("matchR:") #max matchings
            f.write("\n")
            f.write(str(g.MaximumBipartieMatching()[1]))
            f.close()

        for result in results.iterdir(): #expected results
            name = result.name.split('.')
            if name[0]==entry.name:
                f = open('E:/master99/3/optimization_algo/HW/hw4/stock_charts/expected_results/'+result.name, "r")
                line1=f.readline().split()
                exresult=int(line1[0])
                
        write_to_file(wb, ws, entry.name,n,k, len(overlaidlist),exresult, executiontime, index)
        index+=1
    wb.close()
#-------------------------
if __name__ == "__main__":
   print ('Start')
   main()
   print ('Done!')
 