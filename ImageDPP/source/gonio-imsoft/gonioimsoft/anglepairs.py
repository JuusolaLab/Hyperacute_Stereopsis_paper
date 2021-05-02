'''
Working with anglepairs.txt file
'''

import csv


def saveAnglePairs(fn, angles):
    '''
    Saving angle pairs to a file.
    '''
    with open(fn, 'w') as fp:
        writer = csv.writer(fp)
        for angle in angles:
            writer.writerow(angle)

def loadAnglePairs(fn):
    '''
    Loading angle pairs from a file.
    '''
    angles = []
    with open(fn, 'r') as fp:
        reader = csv.reader(fp)
        for row in reader:
            if row:
                angles.append([int(a) for a in row])
    return angles

def toDegrees(angles):
    '''
    Transform 'angles' (that here are just the steps of rotary encoder)
    to actual degree angle values.
    '''
    for i in range(len(angles)):
        angles[i][0] *= (360/1024)
        angles[i][1] *= (360/1024)


def step2degree(step):
    return step * (360/1024)


def degrees2steps(angle):
    '''
    Transform an angle (degrees) to corresponging rotary encoder steps.
    '''
    return angle*(1024/360)

