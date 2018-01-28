import os
import sys
from flask import Flask, render_template, request
import requests
import json
import csv

app = Flask(__name__)

snapped_coordinates = []

response = []
flags = []

# Reading api key form txt file
with open('Google_road_api_key.txt', 'r') as f:
    api_key = f.read()


def handle():
    global snapped_coordinates
    global flags
    # First step We should get snapped points from google api service 'Snap To Road'
    string = 'https://roads.googleapis.com/v1/snapToRoads?path='
    count = 0
    for flag in response['elements']:
        flags.append(flag['key'])
    for coordinate in response['elements']:
        count += 1
        if count == len(response['elements']):
            string += str(coordinate['point']['lat']) + ',' + str(coordinate['point']['lng'])
        else:
            string += str(coordinate['point']['lat']) + ',' + str(coordinate['point']['lng']) + '|'
    string += '&key=' + api_key
    r = requests.get(string).json()
    print(r)
    if 'snappedPoints' not in r:
        print("Cant find nearest road. Please try again")
    else:
        for snapped_point in r['snappedPoints']:
            snapped_coordinates.append(snapped_point['location'])
        for point in snapped_coordinates:
            for key in point.keys():
                if key == 'latitude':
                    point['lat'] = point.pop(key)
                elif key == 'longitude':
                    point['lng'] = point.pop(key)


def import_to_csv():
    global flags
    output_data = []
    print(len(flags))
    print(flags)
    print(len(snapped_coordinates))
    print(snapped_coordinates)
    if len(flags) == len(snapped_coordinates):
        for i in range(len(snapped_coordinates)):
            current_index = len(output_data)
            if i == len(snapped_coordinates)-1:
                output_data[current_index - 1].append(snapped_coordinates[i]['lat'])
                output_data[current_index - 1].append(snapped_coordinates[i]['lng'])

            elif i == 0:
                output_data.append(['WC_ID', 'lat1', 'lng1', 'lat2', 'lng2', 'lat3', 'lng3', 'lat4', 'lng4', 'lat5', 'lng5', 'lat6', 'lng6'])
                output_data.append(['', snapped_coordinates[0]['lat'], snapped_coordinates[0]['lng']])
            elif (flags[i] and flags[i - 1]) or (flags[i] and not flags[i-1]):
                output_data[current_index - 1].append(snapped_coordinates[i]['lat'])
                output_data[current_index - 1].append(snapped_coordinates[i]['lng'])
            elif not flags[i] and not flags[i - 1]:
                output_data[current_index - 1].append(snapped_coordinates[i]['lat'])
                output_data[current_index - 1].append(snapped_coordinates[i]['lng'])
                output_data.append(['', snapped_coordinates[i]['lat'], snapped_coordinates[i]['lng']])
            elif not flags[i] and flags[i - 1]:
                output_data[current_index-1].append(snapped_coordinates[i]['lat'])
                output_data[current_index-1].append(snapped_coordinates[i]['lng'])
                output_data.append(['', snapped_coordinates[i]['lat'], snapped_coordinates[i]['lng']])

    else:
        print('Please reenter input points. input was incorrect')

    file_name = os.path.dirname(sys.argv[0]) + '/output.csv'
    print(file_name)
    with open(file_name, 'a') as csv_file:
        writer = csv.writer(csv_file)
        for row in output_data:
            writer.writerow(row)
    csv_file.close()


@app.route('/snapped', methods=['GET'])
def get():
    return render_template('snapped.html')


# Main page
@app.route("/")
def index():
    return render_template('index.html')


# Post method
@app.route('/server.py', methods=['POST'])
def post():
    if 'it is ok' in request.json:
        import_to_csv()
        return 'ok'
    else:
        global snapped_coordinates
        global response
        global flags
        snapped_coordinates = []
        flags = []
        response = request.json
        print(request.json)
        handle()
        return json.dumps(snapped_coordinates)


if __name__ == "__main__":
    app.run(debug=True)
