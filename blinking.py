import numpy as np
import os
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import time
from multiprocessing import Process, Value

# zips active images and active indices
# slider picks a value that should be currently in active indices
# that frame is loaded from active images

data_directory = Path("./data")
output_directory = Path("./output")

ACTIVE_IMAGES = 'all'

results = np.zeros((256, 256))

class frame_holder():
    def __init__(self, data_directory, output_directory):
        self.data_directory = data_directory
        self.output_directory = output_directory
        self.clicked_pixels = []
        self.filenames = self.load_dataset(data_directory)
        self.active_images = []
        self.active_indices = []
        self.initialize_images(ACTIVE_IMAGES)
    def load_dataset(self, data_directory):
        return [str(data_directory / filename) for filename in os.listdir(data_directory) if ".tif" in filename]
    def load_image(self, filename):
        image = np.array(Image.open(filename).convert(mode='L').resize((256,256)))
        return np.array(image)#/np.mean(image)
    # def lookup(self, query_index):
    #     return [image for image, index in zip(self.active_images, self.active_indices) if index==query_index][0]
    def lookup(self, query_index):
        image = [image for image, index in zip(self.active_images, self.active_indices) if index==query_index][0]
        for coordinate in self.clicked_pixels:
            x, y = round(coordinate[0]), round(coordinate[1])
            image[x, y] = 0
        return [image for image, index in zip(self.active_images, self.active_indices) if index==query_index][0]
    def initialize_images(self, n_images):
        if n_images == 'all':
            n_images = len(self.filenames)
        self.active_images = [self.load_image(filename) for filename in self.filenames[:n_images]]
        self.active_indices = [n for n, _ in enumerate(self.filenames[:n_images])]
    def generate_report(self, x, y):
        global results
        results[x, y] = 1
        np.savetxt(str(self.output_directory / "indices.txt"), results, fmt='%d')
        # print("Generating report for (%d, %d)"%(x, y))
        # trace = np.array([image[x,y] for image in self.active_images])
        # np.savetxt(str(self.output_directory / ("%d_%d.txt"%(x,y))), trace, delimiter=",", fmt='%d')
        # fig, ax = plt.subplots(1,1)
        # # ax.plot(np.linspace(0, 60, len(trace)), trace)
        # ax.plot(range(len(trace)), trace, color='black', linewidth=1)
        # ax.set_xlabel("Time (s)")
        # ax.set_ylabel("Intensity (au)")
        # ax.set_title("Pixel intensity for coords: (%d, %d)"%(x,y))
        # plt.savefig(str(self.output_directory / ("%d_%d.png"%(x,y))), dpi=200)
        # print("Done.")


class interface():
    def __init__(self, x, y, click, frame_holder, mode=None):
        self.x = x
        self.y = y
        self.click = click
        self.frame_holder = frame_holder
        self.fig, self.ax = plt.subplots(1,1)
        self.im = self.ax.imshow(self.frame_holder.active_images[0])
        # self.im.set_clim(0, 75)
        self.cbar = plt.colorbar(self.im, ax=self.ax)
        self.mainloop()
    def mainloop(self):
        plt.ion()
        plt.show()
        def onclick(event):
            # these are transposed compared to the data
            self.y.value = event.xdata
            self.x.value = event.ydata
            self.click.value = 1
            self.frame_holder.clicked_pixels += [(self.x.value, self.y.value)]
        self.cid = self.fig.canvas.mpl_connect('button_press_event', onclick)
        while True:
            for frame_index in self.frame_holder.active_indices:
                self.im.set_data(self.frame_holder.lookup(frame_index))
                self.ax.set_title("%d"%(frame_index))
                # self.cbar.draw_all()
                # self.fig.colorbar(self.im, ax=self.ax)
                self.fig.canvas.draw()
                frame_index = frame_index + 1
                self.fig.canvas.flush_events()
                time.sleep(.1)
    
def generate_report(x, y, click, frame_holder):
    while True:
        if click.value == 1:
            mapped_x, mapped_y = round(x.value), round(y.value)
            click.value = 0
            frame_holder.generate_report(mapped_x, mapped_y)
        time.sleep(0.001)
        
# 002 is done

if __name__ == '__main__':
    current_dir = "003"
    dset2 = frame_holder(data_directory / current_dir, output_directory / current_dir)
    x = Value('f', 0.0)
    y = Value('f', 0.0)
    click = Value('i', 0)

    int2 = Process(target=interface, args=(x, y, click, dset2,))
    int2.start()
    rep2 = Process(target=generate_report, args=(x, y, click, dset2))
    rep2.start()

    # while True:
    #     print(x.value, y.value)
    #     time.sleep(.2)


    
# "generating report" text