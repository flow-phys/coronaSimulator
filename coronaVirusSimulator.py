# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as npy
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import time


class person():
    
    def __init__(self):
        
        self.x = npy.random.random()
        self.y = npy.random.random()
                
        self.U = npy.random.random() - .5   # This makes speed (-.5, .5)
        self.V = npy.random.random() - .5   # This makes speed (-.5, .5)

        self.infected = False
        self.carrier  = False
        self.immune   = False
        self.dead     = False
        self.SD       = False
        
        self.timeSick = 0.0
        #self.SIP      = 1.0

    def step(self,stepsize,immuneTime):
        
        
        if self.infected:
            self.timeSick += stepsize
        
        if self.timeSick > immuneTime:
            self.infected = False
            self.immune   = True
        
        if self.SD:
            return
        
        dt = stepsize
        self.x = self.x + dt * self.U
        self.y = self.y + dt * self.V
        
        if self.x > 1.0:
            self.x = 2.0 - self.x
            self.U = -self.U
            
        if self.x < 0.0:
            self.x = -self.x
            self.U = -self.U
        
        if self.y > 1.0:
            self.y = 2.0 - self.y
            self.V = -self.V
            
        if self.y < 0.0:
            self.y = -self.y
            self.V = -self.V
            
 
                     

    def distance(self,neighbor):
        dist = npy.sqrt( (self.x-neighbor.x)**2 + (self.y - neighbor.y)**2 )
        return dist
        
    
        

class swarm():
    
    def __init__(self,nPeople,infectionRadius,immuneTime,distance,swarmID,axis = None):
        
        self.n = nPeople
        self.infectionRadius = infectionRadius
        self.immuneTime = immuneTime
        self.people = []
        
    
        self.socialDistance = distance

        self.swarmID = swarmID
        swarmID += 1
        
        self.time = 0.0
        self.cycle = 0
        
        self.timeHistory = []
        self.immuneHistory = []
        self.infectedHistory = []
        
        self.maxDist = npy.zeros( (self.n,self.n) )
        
        # Setup plots
        if not axis:
            self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1)
        else:
            self.ax1 = axis[0]
            self.ax2 = axis[1]
        
        
        print("You've made a swarm of %s people" % self.n )
              
        for p in range( self.n ):
            self.people.append( person() )
            rn = npy.random.random()
            if rn < self.socialDistance:
                #self.people[-1].U = 0.0
                #self.people[-1].V = 0.0
                self.people[-1].SD = True
        
    def plot(self,infectionRadius=.01):
        
        
        axs = self.ax1
        axs.cla()
  
        # Plot non-infected people first
        x = [p.x for p in self.people if p.infected == False]
        y = [p.y for p in self.people if p.infected == False]
        axs.plot( x , y, 'go',label="Not-infected")
        
        # Plot non-infected people first
        x = [p.x for p in self.people if p.SD == True]
        y = [p.y for p in self.people if p.SD == True]
        axs.plot( x , y, 'yo',label="Social distancing")
        
        # Plot infected people first
        x = [p.x for p in self.people if p.infected == True]
        y = [p.y for p in self.people if p.infected == True]
        axs.plot( x , y, 'ro',label="Infected")      
        #Circle( (x,y) , radius = infectionRadius )
        
        # Plot immune/recovered people
        x = [p.x for p in self.people if p.immune == True]
        y = [p.y for p in self.people if p.immune == True]
        axs.plot( x , y, 'bo',label="Recovered")          
        
        axs.set_xlim([0,1])
        axs.set_ylim([0,1])
        plt.pause(.01)
    
        
        
    def move(self,stepsize):
        dt = stepsize  # Small unit of time
        for p in self.people:
            p.step(dt,self.immuneTime)
            
    def numberInfected(self):
        sick = [s for s in self.people if s.infected == True]
        return len(sick)
    
    def numberImmune(self):
        immune = [s for s in self.people if s.immune == True]
        return len(immune)
        
            
    def run(self,stepsize,nsteps):
        
        self.stepsize = stepsize
        for n in range(nsteps):
            self.move(stepsize)
            self.time += stepsize
            self.cycle += 1
            self.whoseTouching()
            
            if self.cycle%1 == 0:
                self.plot( infectionRadius=self.infectionRadius )
            
            self.timeHistory.append( self.time )
            self.immuneHistory.append( self.numberImmune()  )
            self.infectedHistory.append( self.numberInfected()  )
            
            if self.cycle%1 == 0:
                axs = self.ax2
                axs.cla()
                axs.plot( self.timeHistory, self.infectedHistory, 'r',label="Infected")
                axs.plot( self.timeHistory, self.immuneHistory, 'b',label="Recovered")
                axs.set_xlim([0,10.0])
                axs.set_ylim([0,self.n])
                plt.pause(.01)
            
            
        
    def whoseTouching(self):
        
        touching = []
        
        skips = 0
        for ip in range(len(self.people)):        
            for inn in range(ip,len(self.people)):
                

                if self.maxDist[ip,inn] >= 2:
                    dist = self.infectionRadius * 1.1
                    skips += 1
                    continue
                else: 
                    p = self.people[ip]
                    n = self.people[inn]
                    dist = p.distance(n)
                    steps =  dist / (2.*npy.sqrt(2.0)*self.stepsize )
                    self.maxDist[ip,inn] = steps
                    self.maxDist[inn,ip] = steps

                
                if dist < self.infectionRadius:
                    if n != p:
                        touching.append( [p,n] )
                        if (p.immune == False and n.immune == False):
                            if (p.infected == True) or (n.infected == True):
                                p.infected = True
                                n.infected = True
                                #print("Virus is spreading!")
        self.maxDist -= 1.0
        print("Skipped %s evals" % skips)
        

sample = 200
radius = 0.025
immuneTime = 2.0
socialDistance = 0.0


fig, [ [ax1, ax2, ax3], [ax4, ax5, ax6] ] = plt.subplots(2, 3)
fig.set_size_inches(11,8)

mySwarm = swarm(sample,radius,immuneTime,socialDistance,1,axis=[ax1,ax4])
mySwarm.people[0].infected = True
mySwarm.people[0].SD = False 

socialDistance = 0.5
mySwarm2 = swarm(sample,radius,immuneTime,socialDistance,2,axis=[ax2,ax5])
mySwarm2.people[0].infected = True
mySwarm2.people[0].SD = False 

socialDistance = 0.85
mySwarm3 = swarm(sample,radius,immuneTime,socialDistance,2,axis=[ax3,ax6])
mySwarm3.people[0].infected = True
mySwarm3.people[0].SD = False 

#mySwarm.run(.01,1000)

for ii in range(1000):
    mySwarm.run(.01,1)
    mySwarm2.run(.01,1)
    mySwarm3.run(.01,1)
    ax1.title.set_text('0% Social Distancing')
    ax2.title.set_text('50% Social Distancing')
    ax3.title.set_text('85% Social Distancing')
    ax1.legend(loc='lower right')
    ax4.legend(loc='upper right')
    plt.pause(.01)
    fig.savefig('movie1/sim_%s.png' % str(ii).zfill(4))

#end = time.time()
#print("Time ellapse: %s" % ( end - start)  )
#plt.close('all')
     
        
            


