# -*- coding: utf-8 -*-

__author__ = 'loelkes'

import json, sys, os, time
import subprocess
import config

# Configure the script here

# openscad = '/Applications/OpenSCAD.app/Contents/MacOS/./OpenSCAD'   # If used on OSX
openscad = 'C:\\Program Files\\OpenSCAD\\openscad.com'  # If used on Windows

extension = '.stl'  # Extensions used for output of OpenSCAD
output_folder = 'D:\\BottleClips-Script\\Tags\\'  # Relative to the script location

openscad_file_path = 'C:\\Users\\kinect\\ownCloud\\Projekte\\3DPrinter\\OpenSCAD\\Mate_Tag'
# openscad_file = '../31C3-bottle-clip.scad'                        # OpenSCAD File used
openscad_file = openscad_file_path + '\\' + 'CCCamp15-bottle-tag.scad'

# All the colors in the DB
# ToDo: get the colors from the DB
colorDB = ['Glow in the dark', 'Random (always fallback option)']

# Configuration for API Access
config.APILimit = "200"
config.APIFields = "id,line_items,status"

start_from_order = 0

def getAPIData():
    api_r = config.wcapi.get("orders?filter[limit]=" + config.APILimit + "&fields=" + config.APIFields).text
    return json.loads(api_r)


def now():
    return time.strftime('%X %x %Z')


# Filter all the orders
def filterOrders(orders):
    mate_tags = []
    global start_from_order

    # Filter out all mate tag orders
    for order in orders['orders']:
        if order['status'] == 'processing' and order['id'] >= int(start_from_order):  # Get only the open orders
            for item in order['line_items']:  # Get each item in the order
                if item['product_id'] == 278:  # Only get the mate tags
                    new_item = [item['meta'][0]['value'],   # Color
                        item['meta'][1]['value'],           # Bottle Type
                        item['meta'][2]['value'],           # Nick
                        item['meta'][3]['value'],           # Icons
                        order['id']                         # Order ID
                        ]
                    if new_item[3].find('#') >= 1:
                        new_item[3] = '#'
                    mate_tags.append(new_item)
                    print new_item
    return mate_tags


# def getOrderNick(orders):
#     data = dict()
#     for order in orders['orders']:
#         order_id = order['id']
#         if order['status'] == 'processing':
#             for item in order['line_items']:
#                 if item['product_id'] == 278:
#                     values = {'id': order_id, 'nickname': item['meta'][3]['value']}
#                     print(values)


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
        subprocess.call(openscad + ' -o ' + output_folder + filename + extension
                        + ' -D "name1="""' + tagset[0][2] + '"" '
                        + ' -D "icons1="""' + tagset[0][3] + '"" '
                        + ' -D "type1="""' + tagset[0][1].title() + '"" '
                        + ' -D "name2="""' + tagset[1][2] + '"" '
                        + ' -D "icons2="""' + tagset[1][3] + '"" '
                        + ' -D "type2="""' + tagset[1][1].title() + '"" '
                        + openscad_file)

def stats(tags):
    print()
    print("------ Begin Data Stats ------")
    for color in colorDB:
        count = len(filterColors(tags, color))
        print(color + ': ' + str(count))
    print('Total unique tags in the queue: ' + str(len(tags)))
    print("------ End Data Stats ------")
    print("")


print(" ")
print("------ Proto3.de Bottle Tag script ------")
print(" ")
start_from_order = raw_input("Please enter starting order ID: ")

global APIdata
APIdata = getAPIData()
global tags
tags = filterOrders(APIdata)
stats(tags)

color_input = raw_input("Please enter color to generate tags: ")
if color_input in colorDB:
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

# sys.exit(0)
