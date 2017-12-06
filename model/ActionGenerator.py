

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 15:13:14 2017

@author: sebbaghs
"""

import torch
import matplotlib.pyplot as pl
import numpy as np
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import sentenceEmbedder as SE
import torch.nn.functional as F
import UsefulComputations as cp
import timeit

torch.manual_seed(1)


class FilmBlock(nn.Module):
    def __init__(self, Nchannels):        
        super(FilmBlock, self).__init__()
        self.Conv_1=nn.Conv2d(Nchannels,Nchannels,3,stride=1,padding=1) 
        self.BN_1=torch.nn.BatchNorm2d(Nchannels)
        self.Conv_2=nn.Conv2d(Nchannels,Nchannels,3,stride=1,padding=1)
        self.BN_2=torch.nn.BatchNorm2d(Nchannels,affine=False)
        
    
    def forward(self,image,paramFromText):
        image = self.Conv_1(image)
        image = self.BN_1(image)
        image = F.relu(image)
        
        x = self.Conv_2(image)
        x = self.BN_2(x)
        x = cp.affineTransformation(x,paramFromText[:,0,:],paramFromText[:,1,:])
        x = F.relu(x)
        
        x+=image
        x = F.relu(x)        
        
        return(x)


class ActionGenerator(nn.Module):
    def __init__(self,
        pathToWordEmbedding="C:\\Users\\simon\\Desktop\\MILA\\GloveData\\glove50.txt",
        hiddenSize_GM=100,
        batch_GM=1,
        numLayers_GM=1,
        numDirections_GM=1,
        dropout_GM=0,
        batch_A=1,
        numLayers_A=1,
        numDirections_A=1,
        dropout_A=0,
        inputShape_V=(72,72),
        numberOfBlocks=4,
        numberOfFeaturesInBlock=64,
        numberOfActions=4):
        super(ActionGenerator, self).__init__()

        #Setting sentence encoder
        self.useCuda=torch.cuda.is_available()     
        
        #should be implemented but not work on my machine for now
        #self.TextEncoder=SE.Sentence2Vec(useCuda=self.useCuda)
        
        self.TextEncoder=SE.Sentence2Vec(useCuda=False)

            
        self.dense1_SE=nn.Linear(4096,numberOfFeaturesInBlock*2*numberOfBlocks) 
        #self.dense2_SE=nn.Linear(2048,1024)

       
        #visual parameters
        self.inputShape_V=inputShape_V
        self.numberOfBlocks=numberOfBlocks
        self.PreConv0=nn.Conv2d(3,8,3,stride=1,padding=1)
        self.PreBN0=torch.nn.BatchNorm2d(8)
        self.PreConv1=nn.Conv2d(8,16,3,stride=1,padding=1)
        self.PreBN1=torch.nn.BatchNorm2d(16)
        self.PreConv2=nn.Conv2d(16,32,3,stride=1,padding=1)
        self.PreBN2=torch.nn.BatchNorm2d(32)
        self.PreConv3=nn.Conv2d(32,64,3,stride=1,padding=1)
        self.PreBN3=torch.nn.BatchNorm2d(64)
        self.PreConv4=nn.Conv2d(64,64,3,stride=1,padding=1)
        self.PreBN4=torch.nn.BatchNorm2d(64)

        self.numberOfFeaturesInBlock=numberOfFeaturesInBlock

        #blocks for FILM
        self.dicOfBlocks={}

        #block0
        self.Block0=FilmBlock(self.numberOfFeaturesInBlock)
        self.dicOfBlocks["Block0"]=self.Block0
        #block1
        self.Block1=FilmBlock(self.numberOfFeaturesInBlock)
        self.dicOfBlocks["Block1"]=self.Block1
        #block2
        self.Block2=FilmBlock(self.numberOfFeaturesInBlock)
        self.dicOfBlocks["Block2"]=self.Block2
        #block3
        self.Block3=FilmBlock(self.numberOfFeaturesInBlock)
        self.dicOfBlocks["Block3"]=self.Block3
        
        

        #Selection network
        self.numberOfActions=numberOfActions
        self.conv1_S=nn.Conv2d(self.numberOfFeaturesInBlock,self.numberOfFeaturesInBlock,5,stride=1,padding=0) 
        self.conv2_S=nn.Conv2d(self.numberOfFeaturesInBlock,self.numberOfFeaturesInBlock,5,stride=1,padding=0) 
        self.dense1_S=nn.Linear(128*2*2,256) 
        self.dense2_S=nn.Linear(256,self.numberOfActions) 
        
        if (self.useCuda):
            self.cuda() 
            print("Using Cuda")

    #in the future, this would be only a setence2glove embedding function
    #and the LSTM will be called in adaptText()
    def preProcessText(self,sentence):
        output=self.TextEncoder.encodeSent(sentence)
        if(self.useCuda):
            output=Variable(output.cuda())
        else:
            output=Variable(output)
#        print(output.type)
#        output=Variable(output)
#        print(output.type)
        return(output)
        
        
    def adaptText(self,sentence):
        shape=sentence.size()
        output=F.relu(self.dense1_SE(sentence))
        #output=F.relu(self.dense2_SE(output))
        return(output.view(shape[0],self.numberOfBlocks,2,self.numberOfFeaturesInBlock) )

    def visual(self,image):
        #first pre-process

        #PreConv
        x = self.PreConv0(image)
        x = self.PreBN0(x)
        x = F.relu(x)

        x = self.PreConv1(x)
        x = self.PreBN1(x)
        x = F.relu(x)

        x = self.PreConv2(x)
        x = self.PreBN2(x) 
        x = F.relu(x)


        x = self.PreConv3(x)
        x = self.PreBN3(x)
        x = F.relu(x)

        x = self.PreConv4(x)
        x = self.PreBN4(x)
        x = F.relu(x)

        return(x)


    def mixVisualAndText(self,image,paramFromText):
        # #blocks
        x=image
        for i in range(self.numberOfBlocks):
            x = self.dicOfBlocks["Block{}".format(i)](x,paramFromText[:,i,:,:])
            
        return(x)

    def selectAction(self,x):

        x = self.conv1_S(x)
        x = torch.nn.BatchNorm2d(x.size()[1],affine=False)(x)
        x = F.relu(x)
        #print("size 1 :", x.size())

        x = self.conv2_S(x)
        x = torch.nn.BatchNorm2d(x.size()[1],affine=False)(x)
        x = F.relu(x)
        #print("size 2 :", x.size())


        x = x.view(-1, 512)
        #print("size 3 :", x.size())

        x = self.dense1_S(x)
        x = F.relu(x)
        #print("size 4 :", x.size())


        x = self.dense2_S(x)
        x = F.relu(x)
        return(x)






    def forward(self,image,generalMission,advice):
        fromText=self.processText(generalMission,advice)
        fromVision=self.visual(image)
        mix=self.mixVisualAndText(fromVision,fromText)
        action=self.selectAction(mix)
        output=torch.max(action, 1)
        return(output)









#def adaptParameters(self,fromText):

model=ActionGenerator()

sequence="this is my sequence haha"
sequence=model.preProcessText(sequence)
img=np.random.randn(3,7,7)
img=cp.preProcessImage(img)
print(img.size())


img=model.visual(img)

paramFromText=model.adaptText(sequence)

vector=model.mixVisualAndText(img,paramFromText)


'''
start = timeit.timeit()
output=gen.processText(sequence,advice)
print ("output from process text", output.size())
print("value check ",output[0,0,0,0])
vi=gen.visual(img)
print("output from visual",vi.size())
mix=gen.mixVisualAndText(vi,output)
print("output from mix",mix.size())
out=gen.selectAction(mix)
print("output from select",out.size())


end = timeit.timeit()
print ("forward time",end - start)




sequence2="this is my sequence haha"
sequence2=Variable(gen.dico.seq2matrix(sequence2))

advice2="you should maybe go right or left"
advice2=Variable(gen.dico.seq2matrix(advice2))


inputsize=160
img2=np.random.rand(3,inputsize,inputsize)
img2=Variable(cp.preProcessImage(img2))

output2=gen(img2,sequence2,advice2)
output2=output2.data.numpy()
output2=torch.from_numpy(output2)
output2=Variable(output2)



criterion = nn.MSELoss()
optimizer = optim.SGD(gen.parameters(), lr=0.001, momentum=0.9)
optimizer.zero_grad()




start = timeit.timeit()
output1=gen(img,sequence,advice)
loss = criterion(output1, output2)
end = timeit.timeit()

print ("forward time",end - start)

start = timeit.timeit()
loss.backward()
end = timeit.timeit()
print ("backward time",end - start)

start = timeit.timeit()
optimizer.step()
end = timeit.timeit()
print ("optim time",end - start)
"""
'''