from PIL import Image
import numpy as np

def converse(npArray):
    rows = npArray.shape[0]
    cols = npArray.shape[1]
    for r in range(rows):
        for c in range(cols):
            if(npArray[r][c] < 70.0):
                npArray[r][c] = 255.0
            else:
                if(npArray[r][c] > 200.0):
                    npArray[r][c] = 0.0
    return npArray

if __name__ == '__main__':
    pass
