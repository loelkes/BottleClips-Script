# -*- coding: utf-8 -*-

__author__ = 'loelkes'

import json, sys, os, time
import subprocess
from woocommerce import API

#import config

import ConfigParser
settings = ConfigParser.ConfigParser()

settings.read('config.ini')

WebAPI = API(
        settings.get('WC', 'URL'),
        settings.get('WC', 'Key'),
        settings.get('WC', 'Secret'),
        version = settings.get('WC', 'Version')
)

# Configuration for API Access
WebAPI.APILimit = settings.get('WC', 'APILimit')
WebAPI.APIFields = settings.get('WC', 'APIFields')

# Configure the script here

# openscad = '/Applications/OpenSCAD.app/Contents/MacOS/./OpenSCAD'   # If used on OSX
# openscad = 'C:\\Program Files\\OpenSCAD\\openscad.com'  # If used on Windows

# extension = '.stl'  # Extensions used for output of OpenSCAD
# output_folder = 'D:\\BottleClips-Script\\Tags\\'  # Relative to the script location

# openscad_file_path = 'C:\\Users\\kinect\\ownCloud\\Projekte\\3DPrinter\\OpenSCAD\\Mate_Tag'
# openscad_file = '../31C3-bottle-clip.scad'                        # OpenSCAD File used
# openscad_file = openscad_file_path + '\\' + 'CCCamp15-bottle-tag.scad'

start_from_order = 0
product_id = 278
colors = []

def getAPIOrders():
    orders_raw = WebAPI.get("orders?filter[limit]=" + WebAPI.APILimit + "&fields=" + WebAPI.APIFields).text
    return json.loads(orders_raw)

def getAPIProducts():
    products_raw = WebAPI.get("products?fields=variations,title").text
    return json.loads(products_raw)

def now():
    return time.strftime('%X %x %Z')

# Filter all the orders
def filterOrders(orders):
    mate_tags = []
    global colors
    global start_from_order
    global product_id

    # Filter out all mate tag orders
    for order in orders['orders']:
        if order['status'] == 'processing' and order['id'] >= int(start_from_order):    # Get only the open orders
            for item in order['line_items']:                                            # Get each item in the order
                if item['product_id'] == int(product_id):                           # Only get the mate tags
                    new_item = [item['meta'][0]['value'],   # Color
                        item['meta'][1]['value'],           # Bottle Type
                        item['meta'][2]['value'],           # Nick
                        item['meta'][3]['value'],           # Icons
                        order['id']                         # Order ID
                    ]
                    if new_item[3].find('#') != -1:         # Set all icons to random if # is found.
                        new_item[3] = '#'
                    mate_tags.append(new_item)
                    print new_item[0] + ' ' + new_item[1] + ' ' + new_item[2]
                    if new_item[0] not in colors:
                        colors.append(new_item[0])
    return mate_tags

# Filter array by colors and output array containing only the given color
def filterColors(data, color):
    color_orders = []  # Array to return
    for item in data:
        if item[0] == color:
            color_orders.append(item)  # Append array containing the desired color to the output array
    return color_orders


def pair2tags(data):
    pairs = []
    for i in range(0, len(data), 2):
        if (i == (len(data) - 1) and len(data) % 2):
            pairs.append([data[i], [' ', ' ', ' ', ' ']])
        else:
            pairs.append([data[i], data[i + 1]])

    return pairs


def tags2openscad(data):
    for tagset in data:
        filename = active_color.replace(" ", "") + '_' + tagset[0][2].replace(" ", "") + '_' + tagset[1][2].replace(" ","")
        print(' Generating Tags: ' + filename + extension)
        # print('Current order ID: ' + str(tagset[0][4]))
        if settings.get('General', 'System') == 'Windows':
            subprocess.call(openscad + ' -o ' + output_folder + filename + extension
                + ' -D "name1="""' + tagset[0][2] + '"" '
                + ' -D "icons1="""' + tagset[0][3] + '"" '
                + ' -D "type1="""' + tagset[0][1].title() + '"" '
                + ' -D "name2="""' + tagset[1][2] + '"" '
                + ' -D "icons2="""' + tagset[1][3] + '"" '
                + ' -D "type2="""' + tagset[1][1].title() + '"" '
                + openscad_file)
        elif settings.get('General', 'System') == 'OSX':
            os.system(openscad + ' -o ' + output_folder + filename + extension
                + ' -D \'name1="' + tagset[0][2] + '"\''
                + ' -D \'icons1="' + tagset[0][3] +'"\''
                + ' -D \'type1="' + tagset[0][1].title() + '"\''
                + ' -D \'name2="' + tagset[1][2] + '"\''
                + ' -D \'icons2="' + tagset[1][3] +'"\''
                + ' -D \'type2="' + tagset[1][1].title() + '"\' '+
                openscad_file + ' > /dev/null 2>&1')



def stats(tags, colors):
    print("\n------ Begin Data Stats ------\n")
    print('Total unique tags in the queue: ' + str(len(tags)))
    print('Total colors: ' + str(len(colors)) + '\n')
    index = 0
    for color in colors:
        count = len(filterColors(tags, color))
        print(str(index) + ' ' + color + ': ' + str(count))
        index += 1
    print("\n------ End Data Stats ------\n")

def main():
    print("\n------ Proto3.de Bottle Tag script ------\n")
    start_from_order = raw_input("Please enter starting order ID: ")
    product_id = raw_input("Please enter product ID: ")
    print("\n------ Fetching data from API, please wait ------\n")
    global APIdata
    APIdata = getAPIOrders()
    global tags
    tags = filterOrders(APIdata)
    stats(tags, colors)

    color_input = raw_input("Please enter color ID to generate tags: ")
    if color_input < len(colors):
        active_color = color_input
    else:
        print("Error: Color \"" + color_input + "\" not found in database.")
        sys.exit(1)

    print("------ Start ------")
    print('starting with order: ' + start_from_order)
    print("Generating tags with the color: " + active_color)

    colorset = filterColors(tags, active_color)
    colorpairs = pair2tags(colorset)
    tags2openscad(colorpairs)

main()
