import numpy as np
from PIL import Image
from skimage.morphology import convex_hull_image


def load_image(infilename) -> np.ndarray:
    """
    load image into numpy array
    """
    img = Image.open(infilename)
    img.load()
    data = np.asarray(img, dtype="int32")
    return data


def arr2Pts(arr: np.ndarray):
    """
    convert a matrix of binary pixels to a list of coordinates
    """
    out = []
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i][j] > 0:
                out.append((i, j))
    return out


def ptCount(p: np.ndarray) -> int:
    """
    count the number of filled points in a matrix of binary pixels
    """
    area = 0
    for i in range(len(p)):
        for j in range(len(p[0])):
            if p[i][j] > 0:
                area += 1
    return area


def convPython(binimg: np.ndarray):
    """
    Python equivalent of convMATLAB() from previous versions of this tool, returns area and convhull as bool np.ndarray
    """
    try:
        from skimage.morphology import convex_hull_image
        chull = convex_hull_image(binimg)
        return np.ndarray.sum(chull), chull
    except:
        return 1, np.array([1])
