from flask import Flask, jsonify, send_from_directory, render_template, request

import requests

import datetime

from nyct_gtfs import NYCTFeed

import os
api_key = os.environ['X_Api_Key']
subway_key = os.environ['subway_api_key']



feed = NYCTFeed("1", api_key=subway_key)

app = Flask(__name__)



@app.route('/', methods=['GET'])
def return_message_json():
    headers = request.headers
    auth = headers.get('X-Api-Key')
    if auth == api_key:

        feed.refresh()
        now = datetime.datetime.now()
        trains = feed.filter_trips(headed_for_stop_id=['121N', '121S'], underway=True)

        train_json = {
            'southbound': [],
            'northbound': []
        }

        northbound_86 = []
        southbound_86 = []


        for train in trains:
            for update in train.stop_time_updates:
                delta = update.arrival - now
                minutes = delta.seconds//60
                seconds = delta.seconds%60
                number = int(train.nyc_train_id[:2])
                if '121S' in update.stop_id:
                    southbound_86.append({'number': number, 'minutes': minutes})
                elif '121N' in update.stop_id:
                    northbound_86.append({'number': number, 'minutes': minutes})

        northbound_86 = sorted(northbound_86, key=lambda d: d['minutes'])
        southbound_86 = sorted(southbound_86, key=lambda d: d['minutes'])

        northbound_86 = ['NB ' + str(i['number']) + ': ' + str(i['minutes']) + 'min' for i in northbound_86]
        southbound_86 = ['NB ' + str(i['number']) + ': ' + str(i['minutes']) + 'min' for i in southbound_86]

        message_json = {
            'data': [
                ['86th Street', northbound_86[0], northbound_86[1]],
                ['86th Street', southbound_86[0], southbound_86[1]],
                ['Hello', 'There', 'Gary']
            ]
        }
                    
        return jsonify(message_json)
    
    else:
        return jsonify({'message': 'ERROR: Unauthorized'})
       





if __name__ == '__main__':
    app.run(debug=True)
