# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 18:47:53 2017

@author: simon
"""

import numpy as np
import torch
from torch.autograd import Variable


def preProcessImage(img):
    #return a torch variable containing the preProcessed image 
    
    #rescale between 0 and 1
    img=np.array(img,dtype= "float")
    maxValue=np.max(img)
    minValue=np.min(img)
    img=(img-minValue)/(maxValue-minValue)
    #ensure the right order of shapes
    #standard shape order for pytorch is (channels, dimX, dimY)
    if(len(img.shape)==4):
        print('error, for now we process images 1 per 1, not per batch')
    
    a,b,c=img.shape
    #print(img.shape)
    #cate to avoid : shape = (dimX, dimY, channels)
    if(a>c):
        #we always have channels=3 and dimX,Y>3
        #the current shape order is(dimX, dimY, channels)
        img=np.swapaxes(img,0,2)
        img=np.swapaxes(img,1,2)
        #print("new ",img.shape)

    #set to pytorch Variable
    img=Variable(torch.from_numpy(img).float())

    if(torch.cuda.is_available()):
        img=img.cuda()
    

    #reshape for a batch of 1
    return(img.unsqueeze(0))

def affineTransformation(x,gamma,beta):
    #assuming that the shapes are
    # x : B,C,H,W
    # gamma and beta : B,C
    # produces a tensor of shape : B,C,H,W and store it into x

    gamma = gamma.unsqueeze(2).unsqueeze(3).expand_as(x)
    beta = beta.unsqueeze(2).unsqueeze(3).expand_as(x)


    return(gamma*x+beta)


#test

#A=[1,2]
#B=np.array([3,4],dtype="float")
#
#A1=preProcessImage(A)
#print(type(A1))
#
#B1=preProcessImage(B)
#print(type(B1))
##
#img=np.ones((7,7,3))
#img[:,:,0]=0
#img[:,:,1]=0.5
#img[0,:,:]=1
#img[1,:,:]=0
#for i in range(3):
#    pl.imshow(img[:,:,i])
#    pl.show()
#    
#new=np.swapaxes(img,0,2)
#new=np.swapaxes(new,1,2)
#for i in range(3):
#    pl.imshow(new[i,:,:])
#    pl.show()