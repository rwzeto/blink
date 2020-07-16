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

class frame_holder():
    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.filenames = self.load_dataset(data_directory)
        self.active_images = []
        self.active_indices = []
        self.initialize_images(ACTIVE_IMAGES)
    def load_dataset(self, data_directory):
        return [str(data_directory / filename) for filename in os.listdir(data_directory) if ".tif" in filename]
    def load_image(self, filename):
        return np.array(Image.open(filename).convert(mode='L'))
    def lookup(self, query_index):
        return [image for image, index in zip(self.active_images, self.active_indices) if index==query_index][0]
    def initialize_images(self, n_images):
        if n_images == 'all':
            n_images = len(self.filenames)
        self.active_images = [self.load_image(filename) for filename in self.filenames[:n_images]]
        self.active_indices = [n for n, _ in enumerate(self.filenames[:n_images])]

class interface():
    def __init__(self, x, y, click, frame_holder, mode=None):
        self.x = x
        self.y = y
        self.click = click
        self.frame_holder = frame_holder
        self.fig, self.ax = plt.subplots(1,1)
        self.im = self.ax.imshow(self.frame_holder.active_images[0])
        self.mainloop()
    def mainloop(self):
        plt.ion()
        plt.show()
        def onclick(event):
            self.x.value = event.xdata
            self.y.value = event.ydata
            self.click.value = 1
        self.cid = self.fig.canvas.mpl_connect('button_press_event', onclick)
        while True:
            for frame_index in self.frame_holder.active_indices[:20]:
                self.im.set_data(self.frame_holder.lookup(frame_index))
                self.ax.set_title("%d"%(frame_index))
                self.fig.canvas.draw()
                frame_index = frame_index + 1
                self.fig.canvas.flush_events()
                time.sleep(.1)
    
def generate_report(x, y, click, frame_holder):
    while True:
        if click.value == 1:
            mapped_x, mapped_y = x.value, y.value
            click.value = 0
            print(int(mapped_x), int(mapped_y))
        time.sleep(0.01)
        

if __name__ == '__main__':
    dset2 = frame_holder(data_directory / "002")
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


    

# mapping function for 1d graph