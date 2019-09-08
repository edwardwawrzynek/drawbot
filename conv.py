import numpy as np
import cv2
import random

'''
Basic Algorithm:
1. pick a starting location (random)
2. find means of all pixels within a certain distance that haven't been drawn on
3. Pick the pixel from 2 whose's mean is greatest than its value in image
4. draw a line to the pixel chosen in 3
5. goto 2
'''

#factor for scaling (doesn't work well)
scaling_factor = 1

file_out = open("out.cmds", "w")

def emit(command):
    file_out.write(command + "\n")

#get the mean value for an area around a pixel in an image
#size used is variable
def mean(image, x, y, size, img_w, img_h):
    low_y = max(y-int(size/2), 0)
    high_y = min(y+int(size/2), img_h-1)

    low_x = max(x-int(size/2), 0)
    high_x = min(x+int(size/2), img_w-1)

    val = cv2.mean(image[low_y:high_y, low_x:high_x])[0]
    #adjust value (getting mean of 0 with just lines is hard)
    #val = max(val-100,0)*(255/100)
    return val*(scaling_factor**2)

num_moves = 0
p_num_moves = 0

#find pixel with bigest diff between current mean and target within area
def findTarget(image, output, pos, width, height, mean_size, move_max, move_min, try_num):
    max_diff = 0
    new_pos = [0,0]
    #find all pixels within move_max
    for y in range(pos[1]-move_max, pos[1]+move_max):
        for x in range(pos[0]-move_max, pos[0]+move_max):
            if x < 0 or y < 0 or x > width-1 or y > height-1:
                continue
            
            dist2 = ((x-pos[0])**2) + ((y-pos[1])**2)
            if dist2 < move_min**2 or dist2 > move_max**2:
                continue
            
            #don't choose pixels already draw over
            if output[y,x] < 200:
                continue
            
            diff = mean(output, x, y, mean_size, width, height)-image[y,x]
            if diff >= max_diff:

                max_diff = diff
                new_pos = [x,y]

    if max_diff < 10:
        if try_num < 3:
            return findTarget(image, output, pos, width, height, mean_size, move_max*2, move_min, try_num+1)
        else:
            #we are probably done
            return None

    return new_pos

#choose new area of image to move to and start drawing (find area that has highest mean - not drawn there yet)
def chooseNew(image, output, width, height, mean_size):
    max_mean = 0
    new_pos = [0,0]
    for y in range(0, height, 100):
        for x in range(0, width, 100):
            val = mean(output, x, y, 150, width, height)
            if val > max_mean:
                max_mean = val
                new_pos = [x,y]
    
    return new_pos

def genMeans(output, width, height, mean_size):
    outputMeans = np.zeros((height, width), np.uint8)
    for x in range(width):
        for y in range(height):
            outputMeans[y,x] = mean(output, x, y, mean_size, width, height)
    
    return outputMeans
  
#must be black and white image
def run(image, width, height, mean_size, move_max, move_min):

    image = cv2.resize(image, (width, height))

    output = np.zeros((height, width), np.uint8)
    output[:] = 255

    #bring pen up
    emit("U")
    #should start with darkest pixel
    pos = [int(width/2), int(height/2)]
    emit("G %i %i" % (pos[0], pos[1]))
    emit("D")

    i = 0
    while i < 200000:
        new_pos = findTarget(image, output, pos, width, height, mean_size, move_max, move_min, 0)
        if new_pos == None:
            global num_moves
            #pos = [random.randint(0,width), random.randint(0, height)]
            emit("U")
            pos = [random.randint(int(width/1.5),width), random.randint(int(height/1.5), height)]
            emit("G %i %i" % (pos[0], pos[1]))
            emit("D")
            num_moves+=1
            continue
        
        cv2.line(output, (pos[0], pos[1]), (new_pos[0], new_pos[1]), 0)
        emit("G %i %i" % (new_pos[0], new_pos[1]))

        if i%100 == 0:
            global p_num_moves
            print(num_moves, i)
            if num_moves - p_num_moves >= 3:
                break
            
            p_num_moves = num_moves
            cv2.imshow("output", output)
            cv2.waitKey(1)
        

        pos = new_pos
        i+=1

    cv2.imshow("source", image)
    cv2.imshow("output", output)
    while cv2.waitKey(0) != 27:
        pass
    cv2.destroyAllWindows()

width = 1000
height = 600
mean_size = 4
max_move = 5
min_move = 2

img = cv2.imread("image")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
run(gray, width*scaling_factor, height*scaling_factor, mean_size*scaling_factor, max_move*scaling_factor, min_move*scaling_factor)
