from PIL import Image
from collections import defaultdict
import operator

class image_class:
    def __init__(self,filename,width,height,colours,pixels):
        self.filename = filename
        self.width = width
        self.height = height
        self.colours = colours
        self.pixels = pixels

def get_colours(colours):
    h_colours = {}
    for color in colours:
        try:
            h_colours[color]=h_colours[color]+1
        except:
            h_colours[color]=1
    sorted_h_colours = sorted(iter(h_colours.items()), key=operator.itemgetter(1), reverse=True)
    return sorted_h_colours

def load_image(filename):
    im = Image.open(filename)
    im = im.convert('RGB', palette=Image.ADAPTIVE, colors=256)
    colours = list(im.getdata())
    width, height = im.size
    pixels = [colours[i * width:(i + 1) * width] for i in range(height)]
    colours = get_colours(colours)
    return image_class(filename,width,height,colours, pixels)


def convert_to_hex(color):
    import struct
    return struct.pack('BBB',*color).encode('hex')

def is_similar(colour_a, colour_b, threshold):
    tolerance = threshold * 255 * 255 * 3
    distance = 0
    distance += (colour_a[0]-colour_b[0])**2
    distance += (colour_a[1]-colour_b[1])**2
    distance += (colour_a[2]-colour_b[2])**2
    return distance <= tolerance

def contrasting_colours(colours,threshold=0.01):
    
    new_colours = []
    new_colours.append(colours[0][0])
    for colour in colours[1::]:
        has_similar = False
        for new_colour in new_colours:
            if is_similar(colour[0],new_colour,threshold):
                has_similar = True
        if not has_similar:
            new_colours.append(colour[0])

    debug = False
    if debug :
        for color in new_colours:
            print('<div style="width:50px;height:50px;border:1px solid #000; background: #%s "></div>' % (convert_to_hex(color)))
    return new_colours

def fitness(filename):
	imagem = load_image(filename)
	colors = contrasting_colours(imagem.colours)
	return len(colors)

