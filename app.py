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
def return_subway_json():
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


        for train in trains:
            for update in train.stop_time_updates:
                delta = update.arrival - now
                minutes = delta.seconds//60
                seconds = delta.seconds%60
                number = int(train.nyc_train_id[:2])
                if '121S' in update.stop_id:
                    train_json['southbound'].append({'number': str(number), 'minutes': str(minutes)})
                elif '121N' in update.stop_id:
                    train_json['northbound'].append({'number': str(number), 'minutes': str(minutes)})
                    
        return jsonify(train_json)
    
    else:
        return jsonify({'message': 'ERROR: Unauthorized'})
       





if __name__ == '__main__':
    app.run(debug=True)
