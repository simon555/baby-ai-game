import pickle
import gym
from gym import Wrapper
import numpy as np

class Teacher(Wrapper):
    def __init__(self, env):
        super(Teacher, self).__init__(env)

    def _close(self):
        super(Teacher, self)._close()

    def _reset(self, **kwargs):
        """
        Called at the start of an episode
        """

        obs = self.env.reset(**kwargs)

        return obs
    
    def pickUpTheKey(self):
        if self.env.carrying == None:
            return((False, 'pick up the key'))
        else:
            return((True,""))      
            
    def ToggleTheDoor(self):
        if (not self.env.grid.get(self.env.doorPos[0],self.env.doorPos[1]).isOpen):
            return((False, 'open the door'))
        else:
            return((True,""))  
            
            
            
    
    def goDown(self):
        DirVec=self.env.getDirVec()
        if DirVec==(1,0):
            return('go right')
        elif DirVec==(-1,0):
            return('go left')
        elif DirVec==(0,1):
            return('continue')
        elif DirVec==(0,-1):
            return('turn back')
        
    
    def goRight(self):
        DirVec=self.env.getDirVec()
        if DirVec==(1,0):
            return('continue')
        elif DirVec==(-1,0):
            return('turn back')
        elif DirVec==(0,1):
            return('go left')
        elif DirVec==(0,-1):
            return('go right')
            
    def goUp(self):
        DirVec=self.env.getDirVec()
        if DirVec==(1,0):
            return('go left')
        elif DirVec==(-1,0):
            return('go right')
        elif DirVec==(0,1):
            return('turn back')
        elif DirVec==(0,-1):
            return('continue')
    
    def goLeft(self):
        DirVec=self.env.getDirVec()
        if DirVec==(1,0):
            return('turn back')
        elif DirVec==(-1,0):
            return('continue')
        elif DirVec==(0,1):
            return('turn right')
        elif DirVec==(0,-1):
            return('turn left')
    
    def inFrontOf(self,ojectivePos):
        #return a tuple (bool,advice), if bool=True the agent is in front of the obective, else the advice
        #helps him to set his position
        
        
        #get the desired direction
        currentPos=self.env.agentPos
        delta=ojectivePos[0]-currentPos[0],ojectivePos[1]-currentPos[1]
        if delta==(1,0):
            obj=0
        elif delta==(-1,0):
            obj=2
        elif delta==(0,1):
            obj=1
        elif delta==(0,-1):
            obj=3
        
        #working modulo 4 on the agent dir
        currentDir=self.env.agentDir
        diff=(obj-currentDir)%4
        if diff==0:
            return((True,''))
        elif diff==1:
            return((False,'go Right'))
        elif diff==2:
            return((False,'turn back'))
        elif diff==3:
            return((False,'turn left'))
                
        
    def getPosKey(self):
        for i in range(self.env.gridSize):
            for j in range(self.env.gridSize):
                if (self.env.grid.get(i,j) != None):
                    if self.env.grid.get(i,j).type == 'key':
                        outputPos=(i,j)                        
                        print(" key found in position : ", outputPos)
                        return(outputPos)
                        
        print("key not found...")
        return(False)
                
        
    def nextTo(self,objectivePos):
        currentPos=self.env.agentPos
        delta=objectivePos[0]-currentPos[0],objectivePos[1]-currentPos[1]


        if np.abs(delta[0])>1:
            if delta[0]>0:
                return((False,self.goRight()))
            elif delta[0]<0:
                return((False,self.goLeft()))
            
        if (np.abs(delta[1])>1 or (np.abs(delta[1])==1 and np.abs(delta[0])==1)):
            if delta[1]>0:
                return((False,self.goDown()))
            elif delta[1]<0:
                return((False,self.goUp()))
        
        #print("you reached your objective, you need to get the right orientation now")
        return((True,''))
        
    
    def reach(self,objectivePos):
        currentPos=self.env.agentPos
        delta=objectivePos[0]-currentPos[0],objectivePos[1]-currentPos[1]


        if np.abs(delta[0])>0:
            if delta[0]>0:
                return((False,self.goRight()))
            elif delta[0]<0:
                return((False,self.goLeft()))
            
        if (np.abs(delta[1])>0):
            if delta[1]>0:
                return((False,self.goDown()))
            elif delta[1]<0:
                return((False,self.goUp()))
        
        #print("you reached your objective, you need to get the right orientation now")
        return((True,''))
            

        
    def getKey(self):
        objectivePos=self.env.keyPos     
        
        isNextTo,adviceDirection=self.nextTo(objectivePos)             
        if (not isNextTo):
            return((False,adviceDirection))               
        else:
            isOriented,adviceOrienation=self.inFrontOf(objectivePos)
            if (not isOriented):
                return((False,adviceOrienation))
            else:
                hasKey,adviceKey =self.pickUpTheKey()
                if (not hasKey):
                    return((False,adviceKey))        
        return((True,''))
            
            
    def openTheDoor(self):
        objectivePos=self.env.doorPos  
        isNextTo,adviceDirection=self.nextTo(objectivePos)             
        if (not isNextTo):
            return((False,adviceDirection))               
        else:
            isOriented,adviceOrienation=self.inFrontOf(objectivePos)
            if (not isOriented):
                return((False,adviceOrienation))
            else:
                doorOpen,adviceDoor =self.ToggleTheDoor()
                if (not doorOpen):
                    return((False,adviceDoor))        
        return((True,''))
        

        
        
    def generateAdvice(self):
        
        doorOpen=self.env.grid.get(self.env.doorPos[0],self.env.doorPos[1]).isOpen    
        if (not doorOpen):
            hasKey=(self.env.carrying!=None)        
            if (not hasKey):
                subgoal="current sub goal : picking the key"
                hasKey,advice=self.getKey()
                #print("advice generated : ",advice)        
            else:
                subgoal="current sub goal : opening the door"
                isOpen,advice=self.openTheDoor()
                #print("advice generated : ",advice)
          
        else:
            goal=self.env.goalPos
            subgoal="current sub goal : reaching the goal"
            finished, advice=self.reach(goal)
            #print("advice generated : ",advice)
            
        #info['advice'] = advice



        print(" ")
        print(" ")
        return(subgoal,advice)
        
            

    def _step(self, action):
        """
        Called at every action
        """
        
        obs, reward, done, info = self.env.step(action)

        
        
        



        return obs, reward, done, info
