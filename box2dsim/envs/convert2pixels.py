import numpy as np
from matplotlib.path import Path
from skimage.transform import resize


def path2pixels(vertices, xlim, ylim, resize_img=None):
    
    xrng = xlim[1] - xlim[0] 
    yrng = ylim[1] - ylim[0] 
    if resize_img is None:
        resize_img = (xrng, yrng)

    x, y = np.meshgrid(np.arange(*xlim), np.arange(*ylim)) # make a canvas with coordinates
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x,y)).T 
    p = Path(vertices) # make a polygon
    grid = p.contains_points(points)

    if np.any(grid==True):
        img = 1.0*grid.reshape(xrng, yrng,order='F').T #pixels 
        img = resize(img, resize_img, mode='constant')
    else:
        img = np.zeros(resize_img)
        
    return img

if __name__ == "__main__":

    import matplotlib.pyplot as plt
    tupVerts=[(60,60), (80,60), (90,20),  (70,20), (60,60)]
    img = path2pixels(tupVerts, [50,100], [0,70], (30,30))
    plt.imshow(img)
    lt.show()

