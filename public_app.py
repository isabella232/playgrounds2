#!/usr/bin/env python

import datetime
import json
import os
import time

from flask import Flask, redirect, abort
import peewee
import pytz

import app_config
import copytext
from models import Playground

app = Flask(app_config.PROJECT_NAME)

FIELD_OPS = {
    peewee.FloatField: float,
    peewee.CharField: unicode,
    peewee.IntegerField: int,
    peewee.BooleanField: bool,
    peewee.PrimaryKeyField: int,
    peewee.TextField: unicode
}

def write_data(payload, path='data/changes.json'):
    """
    DRYs out the process of editing/creating the changes.json file.
    It sucks that there is no single mode for read/edit/create a file.
    """
    if os.path.exists(path):
        # Read the file into a list before doing other things.
        f = open(path, 'r+')

        # Get the file data.
        filedata = f.read()

        # Seek to the beginning of the file.
        f.seek(0)

        # Load the file -- it's a list.
        try:
            output = json.loads(filedata)

        except ValueError:
            output = []

        # Nuke the file contents.
        f.truncate()

    else:
        # Set up a blank list, since the file doesn't exist.
        f = open(path, 'w')

        output = []

    # Append our payload to the list we have created.
    output.append(payload)

    # Write the output to the file.
    f.write(json.dumps(output, indent=4))

    f.close()

@app.route('/%s/test/' % app_config.PROJECT_SLUG, methods=['GET'])
def _test_app():
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@app.route('/%s/' % app_config.PROJECT_SLUG)
def _dynamic_page():
    """
    Example dynamic view demonstrating rendering a simple HTML page.
    """
    return datetime.datetime.now().isoformat()


@app.route('/%s/update-playground/' % app_config.PROJECT_SLUG, methods=['POST'])
def update_playground():

    from flask import request

    # Only handle POST requests.
    if request.method == 'POST':

        # How to know what fields are on this model?
        # Pick a single instance from the DB and serialize it.
        playground = Playground.get(id=request.form.get('id'))
        playground_fields = playground.__dict__['_data'].keys()

        # Prep the payload.
        payload = {}
        payload['action'] = 'update'
        payload['timestamp'] = time.mktime(datetime.datetime.now(pytz.utc).timetuple())
        payload['playground'] = {}
        payload['request'] = {}
        payload['request']['ip_address'] = request.remote_addr
        payload['request']['cookies'] = request.cookies
        payload['request']['headers'] = {}

        # Write the request headers to the payload.
        # It's nicer when they use underscores instead of dashes.
        for key, value in request.headers:
            payload['request']['headers'][key.lower().replace('-', '_')] = value

        # Loop over all of the model fields looking to see if they're present in the POST.

        for field in playground_fields:
            if field in ['slug', 'nprid', 'reverse_geocoded']:
                continue
            if request.form.get(field, None):
                op = FIELD_OPS[getattr(Playground, field).__class__]
                payload['playground'][field] = op(request.form.get(field, None))

            else:
                if getattr(Playground, field) is None:
                    payload['playground'][field] = None
                else:
                    payload['playground'][field] = ''

        # Set up a list for features.
        payload['playground']['features'] = []

        # Loop over all of the possible features to see if they're present in the POST.
        for feature in copytext.COPY.feature_list:
            slug = feature['key']

            if request.form.get(slug, None):
                payload['playground']['features'].append(slug)

        # If there weren't any features in this POST, remove the features list from payload.
        if len(payload['playground']['features']) == 0:
            del(payload['playground']['features'])

        # Write to the changes.json file.
        write_data(payload)

        # return json.dumps(payload)
        return redirect('%s/playground/%s.html?action=editing_thanks' % (app_config.S3_BASE_URL, playground.slug))


@app.route('/%s/insert-playground/' % app_config.PROJECT_SLUG, methods=['POST'])
def insert_playground():
    """
    Create a new playground with data cross-posted from the app.
    """
    from flask import request

    if request.method == 'POST':

        playground_fields = Playground._meta.get_field_names()

        # Prep the payload.
        payload = {}
        payload['action'] = 'insert'
        payload['timestamp'] = time.mktime(datetime.datetime.now(pytz.utc).timetuple())
        payload['playground'] = {}
        payload['request'] = {}
        payload['request']['ip_address'] = request.remote_addr
        payload['request']['cookies'] = request.cookies
        payload['request']['headers'] = {}

        # Write the request headers to the payload.
        # It's nicer when they use underscores instead of dashes.
        for key, value in request.headers:
            payload['request']['headers'][key.lower().replace('-', '_')] = value

        # Loop over all of the model fields looking to see if they're present in the POST.
        for field in playground_fields:
            if field in ['slug', 'nprid', 'reverse_geocoded']:
                continue
            if request.form.get(field, None):

                op = FIELD_OPS[getattr(Playground, field).__class__]
                payload['playground'][field] = op(request.form.get(field, None))
                print field, request.form.get(field, None)
            else:
                if getattr(Playground, field) is None:
                    payload['playground'][field] = None
                else:
                    payload['playground'][field] = ''

        # Set up a list for features.
        payload['playground']['features'] = []

        # Loop over all of the possible features to see if they're present in the POST.
        for feature in copytext.COPY.feature_list:
            slug = feature['key']

            if request.form.get(slug, None):
                payload['playground']['features'].append(slug)

        # If there weren't any features in this POST, remove the features list from payload.
        if len(payload['playground']['features']) == 0:
            del(payload['playground']['features'])

        # Write to the changes.json file.
        write_data(payload)

        # return json.dumps(payload)
        return redirect('%s/search.html?action=create_thanks' % (app_config.S3_BASE_URL))


@app.route('/%s/request-delete-playground/' % app_config.PROJECT_SLUG, methods=['POST'])
def delete_playground():
    """
    Recommend a playground for deletion.
    """
    from flask import request

    # Two things required for a removal request.
    # 1.) A slug so that we can do the lookup.
    # 2.) Some text so that you can justify yourself.
    playground_slug = request.form.get('slug', None)
    text = request.form.get('text', None)

    # Only do this if we have both.
    if playground_slug and text:

        # Prep the payload.
        payload = {}
        payload['action'] = 'delete-request'
        payload['timestamp'] = time.mktime(datetime.datetime.now(pytz.utc).timetuple())
        payload['playground'] = {}
        payload['request'] = {}
        payload['request']['ip_address'] = request.remote_addr
        payload['request']['cookies'] = request.cookies
        payload['request']['headers'] = {}

        # Write the request headers to the payload.
        # It's nicer when they use underscores instead of dashes.
        for key, value in request.headers:
            payload['request']['headers'][key.lower().replace('-', '_')] = value

        # Write the playground info to the payload.
        payload['playground']['slug'] = playground_slug
        payload['playground']['text'] = text

        # Write to the changes.json file.
        write_data(payload)

        return redirect('%s/playground/%s.html?action=deleting_thanks' % (app_config.S3_BASE_URL, playground_slug))

    # Otherwise, bork. A 400 error should do nicely.
    else:
        abort(400)


@app.route('/%s/delete-playground/<playground_slug>/' % app_config.PROJECT_SLUG, methods=['GET'])
def delete_playground_confirm(playground_slug=None):
    from flask import request

    # Only handle POST requests.
    if request.method == 'GET' and playground_slug:

        # Run the id through Playground and flag it as deactivated
        Playground.get(slug=playground_slug).deactivate()

        return json.dumps({"slug": playground_slug, "action": "delete", "success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=app_config.DEBUG)
