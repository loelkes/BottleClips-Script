# -*- coding: utf-8 -*-

__author__ = 'loelkes'

import json, sys, os, time
from woocommerce import API

import config

# Configure the script here

openscad = '/Applications/OpenSCAD.app/Contents/MacOS/./OpenSCAD'   # If used on OSX
# openscad = '"C:\Programme\OpenSCAD\openscad.exe"'                 # If used on Windows

extension = '.stl'                                                  # Extensions used for output of OpenSCAD
output_folder = '../CCCamp15/'                                      # Relative to the script location

# openscad_file = '../31C3-bottle-clip.scad'                        # OpenSCAD File used
openscad_file = '../CCCamp15-bottle-tag.scad'

# All the colors in the DB
# ToDo: get the colors from the DB
colorDB = ['Candy Pink', 'Deep Black', 'Glow in the dark', 'Snow White']

# Configuration for API Access
APILimit = "200"
APIFields = "id,line_items,status"

def getAPIData():
    api_r = wcapi.get("orders?filter[limit]=" + APILimit + "&fields=" + APIFields).text
    return json.loads(api_r)

def now():
    return time.strftime('%X %x %Z')

#Filter all the orders
def filterOrders(orders):

    mate_tags = []

    #Filter out all mate tag orders
    for order in orders['orders']:
        if order['status'] == 'processing':         #Get only the open orders
            for item in order['line_items']:        #Get each item in the order
                if item['product_id'] == 278:       #Only get the mate tags
                    #for i in range(item['quantity']):  #Comment this to disable multiple prints of the same tag.
                        try:
                            if item['meta'][4]['value'].find('#')>=0:
                                item['meta'][4]['value'] = '#'

                            mate_tags.append(
                            [item['meta'][0]['value'],
                             item['meta'][1]['value'],
                             item['meta'][3]['value'],
                             item['meta'][4]['value']
                             ])
                        except:
                            mate_tags.append(
                            [item['meta'][0]['value'],
                             item['meta'][1]['value'],
                             item['meta'][3]['value'],
                             " "
                             ])

    return mate_tags

def getOrderNick(orders):
    data = dict()
    for order in orders['orders']:
        order_id = order['id']
        if order['status'] == 'processing':
            for item in order['line_items']:
                if item['product_id'] == 278:
                    values = {'id': order_id, 'nickname': item['meta'][3]['value']}
                    print(values)

#Filter array by colors and output array containing only the given color
def filterColors(data, color):
    color_orders = []   #Array to return
    for item in data:
        if item[0] == color:
            color_orders.append(item)   #Append array containing the desired color to the output array
    return color_orders

def pair2tags(data):
    pairs = []
    for i in range(0, len(data), 2):
        if (i == (len(data)-1) and len(data)%2):
            pairs.append([data[i],[' ', ' ', ' ', ' ']])
        else:
            pairs.append([data[i], data[i+1]])

    return pairs

def tags2openscad(data):
    for tagset in data:

        filename = active_color.replace(" ","") + '_' + tagset[0][2].replace(" ", "") + '_' + tagset[1][2].replace(" ", "")
        print(now() + ' Generating Tags: ' + filename)
        os.system(openscad + ' -o ' + output_folder + filename + extension

            + ' -D \'name1="' + tagset[0][2] + '"\''
            + ' -D \'icons1="' + tagset[0][3] +'"\''
            + ' -D \'type1="' + tagset[0][1].title() + '"\''
            + ' -D \'name2="' + tagset[1][2] + '"\''
            + ' -D \'icons2="' + tagset[1][3] +'"\''
            + ' -D \'type2="' + tagset[1][1].title() + '"\' '+
            openscad_file + ' > /dev/null 2>&1')

def stats():
    print()
    print("------ Begin Data Stats ------")
    for color in colorDB:
        count = len(filterColors(tags, color))
        print(color + ': ' + str(count))
    print('Total unique tags in the queue: ' + str(len(tags)))
    print("------ End Data Stats ------")
    print("")

def main():
    print(" ")
    print("------ Proto3.de Bottel Tag script ------")
    print(" ")
    print("1) Get the data from the API")
    print("2) Show stats")
    print("3) Proceed to generate tags")
    print(" ")
    choice = raw_input("Select action: ")
    if choice == "1":
        print("Fetching API Data...")
        global APIdata
        APIdata = getAPIData()
        global tags
        tags = filterOrders(APIdata)
        print("...Done!")
        stats()

main()

#APIdata = getAPIData() # Get the Data

# print(getOrderNick(APIdata))

## Here starts the running part of the script



#stats()
color_input = raw_input("Please enter color to generate tags: ")
if color_input in colorDB:
    active_color = color_input
else:
    print("Error: Color \"" + color_input + "\" not found in database.")
    sys.exit(1)

print("------ Start ------")
print(now() + " Generating tags with the color: " + active_color)

#colorset = filterColors(tags, active_color)

#colorpairs = pair2tags(colorset)
#tags2openscad(colorpairs)

sys.exit(0)
