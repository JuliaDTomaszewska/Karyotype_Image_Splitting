from PIL import Image
import os
import cv2
import numpy as np
import shutil

filenames_that_did_not_work = []
#Set the path of the directory containing the karyotype images 
directory = '/Users/julia/Desktop/CARAIO/Karyotype_Images/Batch_5'

for filename in os.listdir(directory):
    if filename.endswith(".tif"):
        print("Starting metaphase " + filename[:filename.index(".tif")])
        #Reading the karyotype image 
        image_path = os.path.join(directory, filename)
        image = cv2.imread(image_path)
        print(image.size)
        #Converting the image to grayscale 
        grayscale_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        #Applying Threshold 
        ret, threshold_image = cv2.threshold(grayscale_image, 254, 255, cv2.THRESH_BINARY_INV)

        #Contouring 
        contours, hierarchy = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #Limiting Contours to Chromosomes
        min_area = 65 
        max_area = 100000
        contours_filtered = []

        #Excluding numbers at the bottom of the screen 
        height, width, channels = image.shape
        for c in contours:
            area = cv2.contourArea(c)
            if min_area < area < max_area:
                # Get the bounding rectangle of the contour
                x, y, w, h = cv2.boundingRect(c)

                # Check if the contour's y-coordinate is above the desired threshold (to not include the numbers at the bottom of the image)
                if y < height - (height/6.75):
                    contours_filtered.append(c)


        #Drawing rectangles around chromosome pair, creating image, extracting chromosome numbers, & creating file

        #Maximum distance between chromosomes in order for them to be considered a pair 
        proximity_threshold = 50
        list_of_paired_chromosomes = [] 
        index = 0

        #Create a list of chromosome contours that are pairs 
        for chromosome1 in contours_filtered: 
            x1, y1, w1, h1 = cv2.boundingRect(chromosome1)
            center_of_rectangle_1  = (x1 + w1/2, y1 + h1/2)
            paired = False
            for chromosome2 in contours_filtered: 
                x2, y2, w2, h2 = cv2.boundingRect(chromosome2)
                center_of_rectangle_2  = (x2 + w2/2, y2 + h2/2)
                distance = cv2.norm(center_of_rectangle_1, center_of_rectangle_2) 
                #Checks that the total distance is less than threshold, the distance in y values is less than 30, the chromosomes are not the same one, and the same pair isn't added twice in a different order. 
                if distance < proximity_threshold and abs(y2-y1) < 30 and not np.array_equal(chromosome1, chromosome2) and not any([np.array_equal(x[0], chromosome2) for x in list_of_paired_chromosomes]): 
                    list_of_paired_chromosomes.append((chromosome1, chromosome2))
                if distance < proximity_threshold and not np.array_equal(chromosome1, chromosome2):
                    paired = True 
            if not paired: 
                list_of_paired_chromosomes.append((chromosome1, chromosome1))
        print(len(list_of_paired_chromosomes))


        cropped_images = []
        #Create images of the chromosome pairs 
        for chromosome_pair in list_of_paired_chromosomes: 
            #Get the coordinates of both chromosomes 
            x1, y1, w1, h1 = cv2.boundingRect(chromosome_pair[0])
            x2, y2, w2, h2 = cv2.boundingRect(chromosome_pair[1])
            min_x, max_x= min(x1, x2), max(x1, x2)

            #Get the coordinates of the left chromosome & right chromosome 
            left_chromosome, right_chromosome = (min_x, y1 if min_x == x1 else y2, w1 if min_x == x1 else w2, h1 if min_x == x1 else h2), (max_x, y1 if max_x == x1 else y2, w1 if max_x == x1 else w2, h1 if max_x == x1 else h2)
            
            #Exclude the long black line at the bottom of karyotypes 
            if w1+w2 < 150: 

                #Finds the start & end coordinates of the chromosome pair and draws a rectangle around it 
                start = (left_chromosome[0], min(y1,y2))
                end = (left_chromosome[0]+w1+w2 + (right_chromosome[0] - (left_chromosome[0] + left_chromosome[2])), min(y1,y2) + max(h1, h2) + ((max(y1,y2) - min(y1,y2)) if (min(y1,y2) + max(h1,h2) < max(y1,y2) + (h1 if max(y1,y2) == y1 else h2)) else 0))
                cropped_image = image[start[1]:end[1], start[0]:end[0]]
                cropped_images.append((cropped_image, (start, end, left_chromosome, right_chromosome)))


        #Label the chromosome image with the chromsome number 
        sorted_cropped_images = sorted(cropped_images, key=lambda x: x[1][0][1])
        row_1 = [x for x in sorted(sorted_cropped_images[:5], key=lambda x: x[1][0][0])]
        row_2 = [x for x in sorted(sorted_cropped_images[5:12], key=lambda x: x[1][0][0])]
        row_3 = [x for x in sorted(sorted_cropped_images[12:18], key=lambda x: x[1][0][0])]
        row_4 = [x for x in sorted(sorted_cropped_images[18:], key=lambda x: x[1][0][0])]
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
            if len(chromosomes_images_in_order) == 23: 
                chromosome_dictionary[23] = chromosomes_images_in_order[22]
            else: 
                filenames_that_did_not_work += [filename]

        #Create the folder for the chromosome images from this metaphase 
        directory_name = '/Users/julia/Desktop/CARAIO/Individual_Chromosome_Images_Batch_5_TEST'       #Path to the folder where you want to save the folders of images for each metaphase
        folder_name = filename[:filename.index(".tif")]        
        folder_path = os.path.join(directory_name, folder_name)
        os.makedirs(folder_path)

        #Create the files with labels 
        if len(chromosomes_images_in_order) != 24: 
            for chromosome_image_and_label in chromosome_dictionary: 
                name_of_chromosome_left = os.path.join(folder_path, filename[:filename.index(".tif")] + "_" + str(chromosome_image_and_label) + "_" + "left" + "_" + "Batch5" + ".jpg")
                cv2.imwrite(name_of_chromosome_left, image[chromosome_dictionary[chromosome_image_and_label][1][2][1]:chromosome_dictionary[chromosome_image_and_label][1][2][1] + chromosome_dictionary[chromosome_image_and_label][1][2][3], chromosome_dictionary[chromosome_image_and_label][1][2][0]:chromosome_dictionary[chromosome_image_and_label][1][2][0] + chromosome_dictionary[chromosome_image_and_label][1][2][2]])
                name_of_chromosome_right = os.path.join(folder_path, filename[:filename.index(".tif")] + "_" + str(chromosome_image_and_label)  + "_" + "right" + "_" + "Batch5" + ".jpg")
                cv2.imwrite(name_of_chromosome_right, image[chromosome_dictionary[chromosome_image_and_label][1][3][1]:chromosome_dictionary[chromosome_image_and_label][1][3][1] + chromosome_dictionary[chromosome_image_and_label][1][3][3], chromosome_dictionary[chromosome_image_and_label][1][3][0]:chromosome_dictionary[chromosome_image_and_label][1][3][0] + chromosome_dictionary[chromosome_image_and_label][1][3][2]])
        else: 
            for chromosome_image_and_label in chromosome_dictionary: 
                if chromosome_image_and_label != 23 and chromosome_image_and_label != 24: 
                    name_of_chromosome_left = os.path.join(folder_path, filename[:filename.index(".tif")] + "_" + str(chromosome_image_and_label) + "_" + "left" + "_" + "Batch5" + ".jpg")
                    cv2.imwrite(name_of_chromosome_left, image[chromosome_dictionary[chromosome_image_and_label][1][2][1]:chromosome_dictionary[chromosome_image_and_label][1][2][1] + chromosome_dictionary[chromosome_image_and_label][1][2][3], chromosome_dictionary[chromosome_image_and_label][1][2][0]:chromosome_dictionary[chromosome_image_and_label][1][2][0] + chromosome_dictionary[chromosome_image_and_label][1][2][2]])
                    name_of_chromosome_right = os.path.join(folder_path, filename[:filename.index(".tif")] + "_" + str(chromosome_image_and_label)  + "_" + "right"+ "_" + "Batch5" + ".jpg")
                    cv2.imwrite(name_of_chromosome_right, image[chromosome_dictionary[chromosome_image_and_label][1][3][1]:chromosome_dictionary[chromosome_image_and_label][1][3][1] + chromosome_dictionary[chromosome_image_and_label][1][3][3], chromosome_dictionary[chromosome_image_and_label][1][3][0]:chromosome_dictionary[chromosome_image_and_label][1][3][0] + chromosome_dictionary[chromosome_image_and_label][1][3][2]])
                else: 
                    name_of_image = os.path.join(folder_path, filename[:filename.index(".tif")] + "_" + str(chromosome_image_and_label) + "_" + "Batch6" + ".jpg")
                    cv2.imwrite(name_of_image, chromosome_dictionary[chromosome_image_and_label][0])

        print("Metaphase " + filename[:2] + " finished.")

print(filenames_that_did_not_work)