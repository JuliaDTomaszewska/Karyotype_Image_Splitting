import pytesseract
from PIL import Image
import os
import cv2
import numpy as np
pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"

#Reading the karyotype image 
image = cv2.imread('50.tif')

#Converting the image to grayscale 
grayscale_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
cv2.imshow("Window", grayscale_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

#Applying Threshold 
ret, threshold_image = cv2.threshold(grayscale_image, 254, 255, cv2.THRESH_BINARY_INV)
cv2.imshow("Window2", threshold_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

#Contouring 
contours, hierarchy = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(len(contours))

#Limiting Contours to Chromosomes 
min_area = 100
max_area = 100000
contours_filtered = []

for c in contours:
    area = cv2.contourArea(c)
    if min_area < area < max_area:
        contours_filtered.append(c)

print(len(contours_filtered))

#Drawing rectangles around chromosome pair, creating image, extracting chromosome numbers, & creating file
 
#Maximum distance between chromosomes in order for them to be considered a pair 
proximity_threshold = 50
list_of_paired_chromosomes = [] 

#Create a list of chromosome contours that are pairs 
for chromosome1 in contours_filtered: 
    x, y, w, h = cv2.boundingRect(chromosome1)
    center_of_rectangle_1  = (x + w/2, y + h/2)
    for chromosome2 in contours_filtered: 
        x, y, w, h = cv2.boundingRect(chromosome2)
        center_of_rectangle_2  = (x + w/2, y + h/2)
        distance = cv2.norm(center_of_rectangle_1, center_of_rectangle_2) 
        if distance < proximity_threshold and not np.array_equal(chromosome1, chromosome2) and not any([np.array_equal(x[0], chromosome2) for x in list_of_paired_chromosomes]): 
            list_of_paired_chromosomes.append((chromosome1, chromosome2))

#Create images of the chromosome pairs 
for chromosome_pair in list_of_paired_chromosomes: 
    
    #Get the coordinates of both chromosomes 
    x1, y1, w1, h1 = cv2.boundingRect(chromosome_pair[0])
    x2, y2, w2, h2 = cv2.boundingRect(chromosome_pair[1])
    min_x, max_x= min(x1, x2), max(x1, x2)
   
    #Get the coordinates of the left chromosome & right chromosome 
    left_chromosome, right_chromosome = (min_x, y1 if min_x == x1 else y2, w1 if min_x == x1 else w2), (max_x, y1 if max_x == x1 else y2, w1 if max_x == x1 else w2)
    
    #Exclude the long black line at the bottom of karyotypes 
    if w1+w2 < 150: 

        #Finds the start & end coordinates of the chromosome pair and draws a rectangle around it 
        start = (left_chromosome[0], min(y1,y2))
        end = (left_chromosome[0]+w1+w2 + (right_chromosome[0] - (left_chromosome[0] + left_chromosome[2])), min(y1,y2) + max(h1, h2) + ((max(y1,y2) - min(y1,y2)) if (min(y1,y2) + max(h1,h2) < max(y1,y2) + (h1 if max(y1,y2) == y1 else h2)) else 0))
        cropped_image = image[start[1]:end[1], start[0]:end[0]]

        #Draws a rectangle around the number of the chromosome 
        numbers_image = image[end[1]:end[1] + 20, end[0] - w1 - w2:end[0]]
        gray_numbers_image = cv2.cvtColor(numbers_image, cv2.COLOR_BGR2GRAY)
        ret, bw_numbers_image = cv2.threshold(gray_numbers_image, 175 , 255, cv2.THRESH_BINARY)
        bw_numbers_image = cv2.resize(bw_numbers_image, (800,600 ))
        cv2.imshow("Window2", bw_numbers_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        #numbers_image = cv2.resize(numbers_image, (600, 360))
        cv2.imwrite("Image_testing.jpg", bw_numbers_image)

        #Creating files & Identifying Numbers   
        number = pytesseract.image_to_string('Image_testing.jpg', lang="eng", timeout=10000)
        print(number)


 






 
