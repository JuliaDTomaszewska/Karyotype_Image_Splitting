from PIL import Image
import os
import cv2
import numpy as np
import shutil


#Set the path of the directory containing the karyotype images 
directory = '/Users/julia/Desktop/CARAIO/Karyotype_Images'

for filename in os.listdir(directory):
    #Reading the karyotype image 
    image_path = os.path.join(directory, filename)
    image = cv2.imread(image_path)

    #Converting the image to grayscale 
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    #Applying Threshold 
    ret, threshold_image = cv2.threshold(grayscale_image, 254, 255, cv2.THRESH_BINARY_INV)

    #Contouring 
    contours, hierarchy = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Limiting Contours to Chromosomes 
    min_area = 92.5 
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
        paired = False
        for chromosome2 in contours_filtered: 
            x, y, w, h = cv2.boundingRect(chromosome2)
            center_of_rectangle_2  = (x + w/2, y + h/2)
            distance = cv2.norm(center_of_rectangle_1, center_of_rectangle_2) 
            if distance < proximity_threshold and not np.array_equal(chromosome1, chromosome2) and not any([np.array_equal(x[0], chromosome2) for x in list_of_paired_chromosomes]): 
                list_of_paired_chromosomes.append((chromosome1, chromosome2))
            if distance < proximity_threshold and not np.array_equal(chromosome1, chromosome2):
                paired = True 
        if not paired: 
            list_of_paired_chromosomes.append((chromosome1, chromosome1))

    cropped_images = []
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
            cropped_images.append((cropped_image, (start, end)))


    #Label the chromosome image with the chromsome number 
    sorted_cropped_images = sorted(cropped_images, key=lambda x: x[1][0][1])
    row_1 = [x[0] for x in sorted(sorted_cropped_images[:5], key=lambda x: x[1][0][0])]
    row_2 = [x[0] for x in sorted(sorted_cropped_images[5:12], key=lambda x: x[1][0][0])]
    row_3 = [x[0] for x in sorted(sorted_cropped_images[12:18], key=lambda x: x[1][0][0])]
    row_4 = [x[0] for x in sorted(sorted_cropped_images[18:], key=lambda x: x[1][0][0])]
    chromosomes_images_in_order = row_1 + row_2 + row_3 + row_4
    chromosome_dictionary = {}
    index = 0
    while index < 22: 
        chromosome_dictionary[index+1] = chromosomes_images_in_order[index]
        index += 1
    if len(chromosomes_images_in_order) == 24: 
        chromosome_dictionary[23] = chromosomes_images_in_order[22]
        chromosome_dictionary[24] = chromosomes_images_in_order[23]
    else: 
        chromosome_dictionary[23] = chromosomes_images_in_order[22]

    #Create the folder for the chromosome images from this metaphase 
    directory_name = '/Users/julia/Desktop/CARAIO'                     #Path to the folder where you want to save the folders of images for each metaphase
    folder_name = filename[:2]
    folder_path = os.path.join(directory_name, folder_name)
    os.makedirs(folder_path)

    #Create the files with labels 
    for chromosome_image_and_label in chromosome_dictionary: 
        name_of_image = os.path.join(folder_path, filename[:2] + "_" + str(chromosome_image_and_label) + ".jpg")
        cv2.imwrite(name_of_image, chromosome_dictionary[chromosome_image_and_label])
    print("Metaphase " + filename[:2] + " finished.")
    
    






    
