#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
import png
import math

def read_image(filename):
    png_img = png.Reader(filename=filename).read_flat()
    return [png_img[0], png_img[1], list(png_img[2])]

def write_image(image, w, h, filename='subimage.png'):
    print 'writing image: ', filename
    f = open(filename, 'wb')
    if type(image[0]) != type([]):
        image_out = reshape_list(image, w, h)
    else:
        image_out = image
    writer = png.Writer(w, h, greyscale=True)
    writer.write(f, image_out)
    f.close()    

def reshape_list(pixels, w, h):
    o = []
    for x in range(0, w*h, w):
        o.append(pixels[x:x+w])
    return o

def generate_error_image():
    [iw, ih, image] = read_image('checkers.png')
    tw = th = 16
    x = y = 51
    template = select_subimage(image, iw, x, y, tw, th)
    d = sum_diff(image, iw, ih, 0, 0, template, tw, th)
    # no need to normalize errors - everything is 16x16
    print 'getting full error image'
    error_image = create_error_image(image, iw, ih, template, tw, th)
    normalized = normalize_image(error_image)
    write_image(normalized, iw-tw+1, ih-th+1, filename='error_image.png')

def filter_error_image():
    [iw, ih, image] = read_image('error_image.png')
    for threshold in range(100, 110):
        filtered = [0] * len(image)
        # for each pixel, if above a threshold
        for i in xrange(len(image)):
            if image[i] < threshold:
                filtered[i] = 255
            else:
                filtered[i] = 0
        write_image(filtered, iw, ih, filename='filtered_error_image_%0.3d.png' % threshold)

def find_checkerboards(threshold = 120):
    # a list of lists of (x,y) hypotheses for checkboards
    checkerboard_sets = []
    [iw, ih, image] = read_image('error_image.png')
    for y in xrange(ih):
        offset = iw * y
        for x in xrange(iw):
            if image[offset + x] < threshold:
                found_match = False
                if len(checkerboard_sets) == 0:
                    checkerboard_sets.append([[x,y]])
                    continue
                # for each set
                for checkerboard_set in checkerboard_sets:
                    # for each point
                    for checkerboard in checkerboard_set:
                        # if overlap, add to set
                        if(overlap(checkerboard[0], checkerboard[1], x, y)):
                            found_match = True
                            checkerboard_set.append([x,y])
                            break
                    if found_match:
                        break
                # start a new set
                if not found_match:
                    checkerboard_sets.append([[x,y]])
    best_results = []
    # for each set
    for checkerboard_set in checkerboard_sets:
        # find the point at the peak (assume there is true max)
        best = checkerboard_set[0]
        best_val = image[best[0] + best[1]*iw]
        for checkerboard in checkerboard_set[1:]:
            val = image[checkerboard[0] + checkerboard[1]*iw]
            # least error wins
            if val < best_val:
                best = checkerboard
                best_val = val
        best_results.append(best)
    return best_results

# times like this I could make a closure and bind it to some operator like {x,y}
def val_at(image, x, y, w):
    return image[y*w + x]

def print_checkerboard_sets(checkerboard_sets):
    print '\n=========================================================\n'
    for checkerboard_set in checkerboard_sets:
        print '.'
        for checkerboard in checkerboard_set:
            print checkerboard,

# the geomety of two boxes, of a given width/height and top-left pixels, whether they overlap
def overlap(x1, y1, x2, y2):
    # hard coded template size - boooo
    return abs(x1-x2) < 16 and abs(y1-y2) < 16

def normalize_image(image):
    _max = float(max(image))
    # this is a retardedly long operation to perform at each pixel
    normalized = [int(math.floor((255 * x) / _max)) for x in image]
    return normalized

def create_error_image(image, iw, ih, template, tw, th):
    d_img = []
    for j in range(0,ih-th+1):
        offset = iw * j
        for i in range(0,iw-tw+1):
            ind = i + offset
            d_img.append(sum_diff(image, iw, ih, i, j, template, tw, th))
    return d_img

# x & y is the top left pixel
def select_subimage(image, iw, x, y, w, h):
    new_image = []
    for row_start in range(y*iw, (y+h)*iw, iw):
        new_image += image[row_start + x: row_start + x + w]
    return new_image


# used to help extract the ideal checkerboard
def sample_subimage(image, x,y,w,h):
    subimage = select_subimage(image, x, y, w, h)
    o = reshape_list(subimage, w, h)
    write_png(o, w, h)
    return subimage

def sum_diff(image, iw, ih, x, y, template, tw, th):
    d = 0
    # image_subsection_indices
    isi = get_range(iw, x, y, tw, th)
    for i in range(tw*th):
        d += abs(image[isi[i]] - template[i]);
    return d

def get_range( image_w, x, y, w, h):
    r = []
    # is there a 2d range?
    for i in range(image_w*y, image_w*(y+h), image_w):
        r += range(i + x, i + x + w)
    return r

if __name__ == '__main__':
    # # to select a sub area to estimate the size of the checkboard
    # # (and test the image manipulation code)
    # sample_subimage
    
    # # to generate an error image - where each pixel is the error at that location
    # # error is sum(image_region - checkboard_template). Lower is good
    # generate_error_image()
    
    # # to filter the error image to find a good error threshold
    # filter_error_image()
    
    # to find the locations in the end
    locations = find_checkerboards(109)
    print 'there are %d locations:' % len(locations)
    print locations
    