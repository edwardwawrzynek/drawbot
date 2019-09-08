import numpy as np
import cv2

import sys

#draw a preview of what a set of commands will look like
if len(sys.argv) != 4:
    print("Usage: draw.py file max_x max_y")
    exit()

f = open(sys.argv[1])
org_w = int(sys.argv[2])
org_h = int(sys.argv[3])

output = np.zeros((800, 800), np.uint8)
output[:] = 255

draw = False
pos = [0,0]
for l in f:
    if l[0] == 'U':
        draw = False
    elif l[0] == 'D':
        draw = True
    elif l[0] == 'G':
        l = l.split()
        x = int(l[1])
        y = int(l[2])

        if draw:
            cv2.line(output, (int((pos[0]*800)/org_w), int((pos[1]*800)/org_h)), (int((x*800)/org_w), int((y*800)/org_h)), 0)
        pos = [x,y]

cv2.imshow("output", output)
while cv2.waitKey(0) != 27:
    pass
cv2.destroyAllWindows()

        
