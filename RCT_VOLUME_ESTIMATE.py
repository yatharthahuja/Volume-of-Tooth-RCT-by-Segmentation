# Importing Libraries
import matplotlib.pyplot as plt
import numpy as np
import argparse
import cv2

# Otsu's thresholding and segmentation
def otsu_segmentation(image, scan):
    if scan == 'pre':
        shifted = cv2.pyrMeanShiftFiltering(image, 21, 96)
    elif scan == 'post':
        shifted = cv2.pyrMeanShiftFiltering(image, 21, 51)
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Sobel Filtering
def sobel_filter(thresh):
    rows, cols = thresh.shape
    sobel_horizontal = cv2.Sobel(thresh, cv2.CV_64F, 1, 0, ksize=31)
    sobel_vertical = cv2.Sobel(thresh, cv2.CV_64F, 0, 1, ksize=31)
    return sobel_vertical, sobel_horizontal

# Function to remove duplicate list entries
def rem_dup(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list

# Vertical closed column detection using look-ahead 
def vertical_closed_curve(sobel_vertical): 
    coords_ver = []
    col_trios = []#representing [rowstrrtin, row ending, column] of closed curve
    c = 0
    while c < len(sobel_vertical):
        #print("c")
        r = 0
        hole_found = False
        while r < len(sobel_vertical):
            #print("r")
            #print(sobel_vertical[r][c])
            if sobel_vertical[r][c] < 0 :
                r_dash = r
                #print("looking ahead")
                while r_dash < len(sobel_vertical):
                    if sobel_vertical[r_dash][c] > 0:
                        #print("hole found!")
                        col_trios.append([r, r_dash, c])
                        hole_found = True
                        break
                    r_dash+=1  
            if hole_found:
                break  
            r+=1
        c+=1
    #print("hole search finished!")
    col_trios = rem_dup(col_trios)
    for trio in col_trios:
        row = trio[0]
        while row < trio[1]:
            coords_ver.append([row, trio[2]])
            row+=1
    #print(len(coords_ver))
    return coords_ver

# Horizontal closed rows detection using look-ahead
def horizontal_closed_curve(sobel_horizontal):
    coords_hor = []
    row_trios = []#representing [row , column strarting, column ending] of closed curve
    r = 0
    while r < len(sobel_horizontal):
        #print("r")
        c = 0
        hole_found = False
        while c < len(sobel_horizontal):
            #print("c")
            #print(sobel_horizontal[r][c])
            if sobel_horizontal[r][c] < 0 :
                c_dash = c
                #print("looking ahead")
                while c_dash < len(sobel_horizontal):
                    if sobel_horizontal[r][c_dash] > 0:
                        #print("hole found!")
                        row_trios.append([r, c, c_dash])
                        hole_found = True
                        break
                    c_dash+=1    
            if hole_found:
                break    
            c+=1
        r+=1
    #print("hole search finished!")
    row_trios = rem_dup(row_trios)
    for trio in row_trios:
        col = trio[1]
        while col < trio[2]:
            coords_hor.append([trio[0], col])
            col+=1
    #print(len(coords_hor))
    return coords_hor

# Function for intersection of both detected regions
def intersecting_pixels( coords_ver, coords_hor):
    coords_ver_stuff = set(map(tuple, coords_ver))
    return [x for x in coords_hor if tuple(x) in coords_ver_stuff]

# Function to display hole findings and store their corresponding detection canvas
def vis_hole(thresh, enclosed_pixels, dataset_canvas, image_i):
    canvas = np.zeros([len(thresh), len(thresh)])
    i = 0
    #print(enclosed_pixels[0])
    while i<len(enclosed_pixels):
        [r, c] = enclosed_pixels[i]
        canvas[r, c]=1
        i+=1
    plt.imshow(canvas)
    filename = str(dataset_canvas+str(image_i))
    plt.savefig(filename)
    #return canvas

if __name__ == "__main__":
    
    # From arguments total no of images, area per pixel, slide thickness
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--scan", required=True, help="Scan Set: Pre/Post")
    ap.add_argument("-i", "--images_i", required=True, help="Starting Index of Images in Dataset")
    ap.add_argument("-n", "--images_n", required=True, help="Total Number of Images in Dataset")
    ap.add_argument("-a", "--area_pp", required=True, help="Area per Pixel in MicroCT scan in microns squared")
    ap.add_argument("-t", "--slide_thickness", required=True, help="Thickness per slide in MicroCT scan in microns")
    ap.add_argument("-dc", "--dataset_canvas", required=True, help="Path to directory for storing hole detections")
    ap.add_argument("-d", "--dataset_dir", required=True, help="Path to dataset directory")
    args = vars(ap.parse_args())
        
    # Scan Set
    scan = args['scan']

    # Path to directory for storing hole detections
    dataset_canvas = args['dataset_canvas']#"/home/yatharth/Desktop/rct/canvas/"

    # Path to scan images dataset directory
    dataset_dir = args['dataset_dir']#"/home/yatharth/Desktop/rct/dataset/"

    # Total number of images in dataset
    images_n = int(args['images_n'])#341 args[images_n]

    # Area per Pixel in MicroCT scan in microns squared
    area_pp = float(args['area_pp']) #1.75*1.75

    # Thickness per slide in MicroCT scan in microns
    slide_thickness = float(args['slide_thickness']) #14

    # Total Volume in microns^3
    volume = 0

    # Hole pixels per layer list record
    pixels_pl = []

	# Read the images in ./dataset folder
    image_i = int(args['images_i'])#200 # image index
    
    while image_i <= images_n :# modify as per images in dataset folder

        print("     Analysing Image: "+str(image_i)+" / "+str(images_n))
        if scan == 'pre':
            image = cv2.imread(str(dataset_dir)+"C0001194_0"+str(image_i)+".TIF")
        elif scan == 'post':
            image = cv2.imread(str(dataset_dir)+"C0001561_0"+str(image_i)+".TIF")

        # Otsu's Segmentation
        thresh = otsu_segmentation(image, scan)

        # Sobel Filtering
        sobel_vertical, sobel_horizontal = sobel_filter(thresh)

        # Estimating verical and horizontal closed pixel pairs:
        coords_ver = vertical_closed_curve(sobel_vertical)
        coords_hor = horizontal_closed_curve(sobel_horizontal)

        # Estimating exclosed pixels in drill hole
        enclosed_pixels = intersecting_pixels( coords_ver, coords_hor)
        print("Hole Search Finished!")
        print(str(len(enclosed_pixels))+" pixels found enclosed in the hole.")
        print("Estimated volume of slide image: "+str(len(enclosed_pixels)*area_pp*slide_thickness))
        print("Creating Canvas...", end = " ")
        print("Canvas Created!")
        vis_hole(thresh, enclosed_pixels, dataset_canvas, image_i)

        volume+=(len(enclosed_pixels)*area_pp*slide_thickness)
        pixels_pl.append(len(enclosed_pixels))
        image_i+=1

    #print("************")
    print("TOTAL TOOTH RCT VOLUME ESTIMATION: "+ str(volume) + " cubic microns")
    print("************")

    file = open("./results/"+str(scan)+"-scan-results.txt","w")
    file.write(str(volume))
    file.close()