import pytesseract
import cv2
pytesseract.pytesseract.tesseract_cmd = r"/Users/julia/miniconda3/bin/pytesseract"

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

#Performing Morphology  
#kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
#opening = cv2.morphologyEx(threshold_image, cv2.MORPH_OPEN, kernel)

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

#Extracting Chromosome Numbers 
 
for cnt in contours_filtered: 
    x, y, w, h = cv2.boundingRect(cnt)
    print(x, y, w, h)
    cropped_image = cv2.rectangle(image, (x, y), (x+50, y+h), (0, 245, 0), 2)
    cv2.imshow("Window3", cropped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    try: 
        number = pytesseract.image_to_string(cropped_image, lang = "eng")
    except: 
        continue
    if number: 
        cv2.imwrite(f"{number}", cropped_image)
    else: 
        cv2.imwrite(f"No number found", cropped_image)



#Labeling images & saving them in seperate files'''