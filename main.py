import cv2
import os
import time

# supported file formats
IMG_FE = (".jpg", ".png", ".bmp", ".jpeg")
# TIMEOUT
T_OUT = 60

if os.name == "posix":
    PATH = "/home/pi/dropbox"
    DISPLAY_WIDTH, DISPLAY_HEIGHT = 1920, 1080
    os.system("rclone sync -v dropbox:digitalerBilderrahmen /home/pi/dropbox")
else:
    PATH = "images"
    DISPLAY_WIDTH, DISPLAY_HEIGHT = 1280, 720

def scaleToMaxSize(src_img, dst_size):
    img_h, img_w, elem_h, elem_w = src_img.shape[0], src_img.shape[1], dst_size[1], dst_size[0] # extract dimensions
    img_r, elem_r = img_w/img_h, elem_w/elem_h # calculate ratios
    if img_r == elem_r: # if ratio is same
        dst_img = cv2.resize(src_img, (elem_w, elem_h)) # resize
    else:
        if img_h > img_w:
            adjusted_width = int(elem_h*(img_w/img_h))
            dst_img = cv2.resize(src_img, (adjusted_width, elem_h)) # resize to maximum width and adjusted height
        else:
            adjusted_height = round(img_h/(img_w/elem_w)) # calculate new height
            dst_img = cv2.resize(src_img, (elem_w, adjusted_height)) # resize to maximum width and adjusted height

    height = (dst_size[1]-dst_img.shape[0])//2 if (dst_size[1]-dst_img.shape[0])//2 > 0 else 0 # calculate height of border
    width = (dst_size[0]-dst_img.shape[1])//2 if (dst_size[0]-dst_img.shape[1])//2 > 0 else 0 # calculate width of border
    dst_img = cv2.copyMakeBorder(dst_img, height, height, width, width, cv2.BORDER_CONSTANT, None, value=0) # add border to image
        
    return dst_img

class Viewer:
    def __init__(self):
        self.file_list = []
        self.file_idx = 0

        self.running = True
    
    def sync_files(self):
        self.file_list = []
        for elem in os.listdir(PATH):
            path = os.path.join(PATH, elem)
            if path.endswith(IMG_FE): # if file endswith file extension
                self.file_list.append(path) # append file to list
            elif os.path.isdir(path):
                for file in os.listdir(path):
                    if file.endswith(IMG_FE):
                        self.file_list.append(os.path.join(path, file)) # append file to list
            else:
                pass
    
    def plus_idx(self):
        if self.file_idx < len(self.file_list)-1:
            self.file_idx += 1
        else:
            self.file_idx = 0
            self.sync_files()
    
    def minus_idx(self):
        if self.file_idx > 0:
            self.file_idx -= 1
        else:
            self.file_idx = len(self.file_list)-1
    
    def on_touch(self, event, x, y, flags, param):
        if event == cv2.EVENT_FLAG_LBUTTON:
            if x > DISPLAY_WIDTH//2:
                self.plus_idx()
            else:
                self.minus_idx()
            self.ts = time.time()

    def run(self):
        if os.name == "posix":
            cv2.namedWindow("viewer", cv2.WND_PROP_FULLSCREEN) # create window
            cv2.setWindowProperty("viewer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN) # display window in full screen
        else:
            cv2.namedWindow("viewer")
        cv2.resizeWindow("viewer", DISPLAY_WIDTH, DISPLAY_HEIGHT)
        cv2.setMouseCallback("viewer", self.on_touch)

        self.sync_files()
        self.ts = time.time()
        while self.running:
            
            self.t_diff = time.time()-self.ts
            if  self.t_diff < T_OUT:
                if len(self.file_list) > 0:
                    file = self.file_list[self.file_idx]
                    if file.endswith(IMG_FE): # file ends with image file extension and therefore is image
                        if os.path.exists(file):
                            img = cv2.imread(file, cv2.IMREAD_COLOR) # read image

                            if img.shape[0]!= DISPLAY_HEIGHT or img.shape[1]!= DISPLAY_WIDTH:
                                img = scaleToMaxSize(img, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

                            cv2.imshow("viewer", img)
                            key = cv2.waitKey(1)
                            if key == ord("q"):
                                self.running = False
                        else:
                            self.sync_files()
                            self.file_idx = 0
            else:
                self.plus_idx()
                self.ts = time.time() 

if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()