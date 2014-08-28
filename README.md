Copyright 2013 NPR.  All rights reserved.  No part of these materials may be reproduced, modified, stored in a retrieval system, or retransmitted, in any form or by any means, electronic, mechanical or otherwise, without prior written permission from NPR.

(Want to use this code? Send an email to nprapps@npr.org!)

playgrounds2
========================

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [What's in here?](#whats-in-here)
* [Install requirements](#install-requirements)
* [Project secrets](#project-secrets)
* [Adding a template/view](#adding-a-templateview)
* [Run the project locally](#run-the-project-locally)
* [Editing workflow](#editing-workflow)
* [Run Javascript tests](#run-javascript-tests)
* [Run Python tests](#run-python-tests)
* [Compile static assets](#compile-static-assets)
* [Test the rendered app](#test-the-rendered-app)
* [Deploy to S3](#deploy-to-s3)
* [Deploy to EC2](#deploy-to-ec2)
* [Install cron jobs](#install-cron-jobs)
* [Install web services](#install-web-services)
* [Add fake changelog data](#add-fake-changelog-data)
* [Run the remote cron](#run-the-remote-cron)
* [If cron fails](#if-cron-fails)
* [DNS Configuration)](dns-configuration)

What is this?
-------------

**Describe playgrounds2 here.**

Assumptions
-----------

The following things are assumed to be true in this documentation.

* You are running OSX.
* You are using Python 2.7. (Probably the version that came OSX.)
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.

What's in here?
---------------

The project contains the following folders and important files:

* ``confs`` -- Server configuration files for nginx and uwsgi. Edit the templates then ``fab <ENV> render_confs``, don't edit anything in ``confs/rendered`` directly.
* ``data`` -- Data files, such as those used to generate HTML.
* ``etc`` -- Miscellaneous scripts and metadata for project bootstrapping.
* ``jst`` -- Javascript ([Underscore.js](http://documentcloud.github.com/underscore/#template)) templates.
* ``less`` -- [LESS](http://lesscss.org/) files, will be compiled to CSS and concatenated for deployment.
* ``templates`` -- HTML ([Jinja2](http://jinja.pocoo.org/docs/)) templates, to be compiled locally.
* ``tests`` -- Python unit tests.
* ``www`` -- Static and compiled assets to be deployed. (a.k.a. "the output")
* ``www/live-data`` -- "Live" data deployed to S3 via cron jobs or other mechanisms. (Not deployed with the rest of the project.)
* ``www/test`` -- Javascript tests and supporting files.
* ``app.py`` -- A [Flask](http://flask.pocoo.org/) app for rendering the project locally.
* ``app_config.py`` -- Global project configuration for scripts, deployment, etc.
* ``copytext.py`` -- Code supporting the [Editing workflow](#editing-workflow)
* ``crontab`` -- Cron jobs to be installed as part of the project.
* ``fabfile.py`` -- [Fabric](http://docs.fabfile.org/en/latest/) commands automating setup and deployment.
* ``public_app.py`` -- A [Flask](http://flask.pocoo.org/) app for running server-side code.
* ``render_utils.py`` -- Code supporting template rendering.
* ``requirements.txt`` -- Python requirements.

Install requirements
--------------------

Node.js is required for the static asset pipeline. If you don't already have it, get it like this:

```
brew install node
curl https://npmjs.org/install.sh | sh
```

Then install the project requirements:

```
cd playgrounds2
npm install less universal-jst
mkvirtualenv playgrounds2
pip install -r requirements.txt
fab update_copy
fab local_bootstrap
```

Project secrets
---------------

Project secrets should **never** be stored in ``app_config.py`` or anywhere else in the repository. They will be leaked to the client if you do. Instead, always store passwords, keys, etc. in environment variables and document that they are needed here in the README.

Adding a template/view
----------------------

A site can have any number of rendered templates (i.e. pages). Each will need a corresponding view. To create a new one:

* Add a template to the ``templates`` directory. Ensure it extends ``_base.html``.
* Add a corresponding view function to ``app.py``. Decorate it with a route to the page name, i.e. ``@app.route('/filename.html')``
* By convention only views that end with ``.html`` and do not start with ``_``  will automatically be rendered when you call ``fab render``.

Run the project locally
-----------------------

A flask app is used to run the project locally. It will automatically recompile templates and assets on demand.

```
workon playgrounds2
python app.py
```

Visit [localhost:8000](http://localhost:8000) in your browser.

To test playground edits, access playgrounds2 directory from a second command line.

```
workon playgrounds2
python public_app.py
```

Editing workflow
-------------------

The app is rigged up to Google Docs for a simple key/value store that provides an editing workflow.

View the sample copy spreadsheet [here](https://docs.google.com/spreadsheet/pub?key=0AlXMOHKxzQVRdHZuX1UycXplRlBfLVB0UVNldHJYZmc#gid=0). A few things to note:

* If there is a column called ``key``, there is expected to be a column called ``value`` and rows will be accessed in templates as key/value pairs
* Rows may also be accessed in templates by row index using iterators (see below)
* You may have any number of worksheets
* This document must be "published to the web" using Google Docs' interface

This document is specified in ``app_config`` with the variable ``COPY_GOOGLE_DOC_KEY``. To use your own spreadsheet, change this value to reflect your document's key (found in the Google Docs URL after ``&key=``).

The app template is outfitted with a few ``fab`` utility functions that make pulling changes and updating your local data easy.

To update the latest document, simply run:

```
fab update_copy
```

Note: ``update_copy`` runs automatically whenever ``fab render`` is called.

At the template level, Jinja maintains a ``COPY`` object that you can use to access your values in the templates. Using our example sheet, to use the ``byline`` key in ``templates/index.html``:

```
{{ COPY.attribution.byline }}
```

More generally, you can access anything defined in your Google Doc like so:

```
{{ COPY.sheet_name.key_name }}
```

You may also access rows using iterators. In this case, the column headers of the spreadsheet become keys and the row cells values. For example:

```
{% for row in COPY.sheet_name %}
{{ row.column_one_header }}
{{ row.column_two_header }}
{% endfor %}
```

Run Javascript tests
--------------------

With the project running, visit [localhost:8000/test/SpecRunner.html](http://localhost:8000/test/SpecRunner.html).

Run Python tests
----------------

Python unit tests are stored in the ``tests`` directory. Run them with ``fab tests``.

Compile static assets
---------------------

Compile LESS to CSS, compile javascript templates to Javascript and minify all assets:

```
workon playgrounds2
fab render
```

(This is done automatically whenever you deploy to S3.)

Test the rendered app
---------------------

If you want to test the app once you've rendered it out, just use the Python webserver:

```
cd www
python -m SimpleHTTPServer
```

Deploy to S3
------------

To deploy all assets **except** the playgrounds pages:

```
fab staging master deploy
```

To deploy the playgrounds pages:

```
fab staging remote:deploy_playgrounds
```

Deploy to EC2
-------------
You can deploy to EC2 for a variety of reasons. We cover two cases: Running a dynamic Web application and executing cron jobs.

For running a Web application:
* In ``fabfile.py`` set ``env.deploy_to_servers`` to ``True``.
* Also in ``fabfile.py`` set ``env.deploy_web_services`` to ``True``.
* Run ``fab staging master setup`` to configure the server.
* Run ``fab staging master bootstrap`` to bootstrap the database.
* Run ``fab staging master deploy`` to deploy the app.
* Run ``fab staging master remote:deploy_playgrounds`` to render and deploy the playgrounds pages.
* Run ``fab staging master remote:update_search_index`` to bootstrap Cloudsearch.

For running cron jobs:
* In ``fabfile.py`` set ``env.deploy_to_servers`` to ``True``.
* Also in ``fabfile.py``, set ``env.install_crontab`` to ``True``.
* Run ``fab staging master setup`` to configure the server.
* Run ``fab staging master deploy`` to deploy the app.

You can configure your EC2 instance to both run Web services and execute cron jobs; just set both environment variables in the fabfile.

Install cron jobs
-----------------

Cron jobs are defined in the file `crontab`. Each task should use the `cron.sh` shim to ensure the project's virtualenv is properly activated prior to execution. For example:

```
* * * * * ubuntu bash /home/ubuntu/apps/$PROJECT_NAME/repository/cron.sh fab $DEPLOYMENT_TARGET cron_test
```

**Note:** In this example you will need to replace `$PROJECT_NAME` with your actual deployed project name.

To install your crontab set `env.install_crontab` to `True` at the top of `fabfile.py`. Cron jobs will be automatically installed each time you deploy to EC2.

Install web services
---------------------

Web services are configured in the `confs/` folder. Currently, there are two: `nginx.conf` and `uwsgi.conf`.

Running ``fab setup`` will deploy your confs if you have set ``env.deploy_to_servers`` and ``env.deploy_web_services`` both to ``True`` at the top of ``fabfile.py``.

To check that these files are being properly rendered, you can render them locally and see the results in the `confs/rendered/` directory.

```
fab render_confs
```

You can also deploy the configuration files independently of the setup command by running:

```
fab deploy_confs
```

Add fake changelog data
---------------------

Call ```fab create_test_revisions``` and look at this playground: http://localhost:8000/playground/strong-reach-playground-bowdon-ga.html

Run the remote cron
-------------------

To manually run the cron job on the remote server (which will also redeploy all playgrounds), use the following command:

```
fab [staging|production] [master|stable] remote:process_updates
```

If cron fails
-------------

If the overnight cron job fails changes in process may not have been applied. The changes that were in process will have been staged in `changes-in-process.json` in the root directory of the repository. The accumulating changeset will have been deleted from `data/changes.json`. Depending on what stage of the cron job failed (processing or rendering) the changes may or may not have been applied in their entirety. It is virtually impossible to automatically handle every case that may arise, so instead you must manually investigate which changes were applied and determine if changes staged in `changes-in-process.json` need to be copied by into `data/changes.json` so they will be applied the next time the cron job is run. This can not be done automatically because it could result in duplicate playgrounds being created if, for example, the cron job failed half-way through the processing step.

If you determine that all changes have been successfully applied (even if they were not rendered), simply delete `changes-in-process.json`, fix the bug and rerun the cron process to render those changes.

DNS Configuration
-----------------

The `www` version of this application CNAME'd to S3 as usual. Our internal DNS doesn't support issuing a 301 for the bare domain and S3 doesn't support bare domains unless using Route 53. To work around this we've configured a custom Nginx rule to redirect bare domain traffic to www:

```
server {
    listen 80;
    server_name playgroundsforeveryone.com;
    return 301 $scheme://www.playgroundsforeveryone.com$request_uri;
}
```

In order for this to work the default Nginx server must be modified to be the default server:

```
server {
    listen 80 default_server;
    client_max_body_size 15M;
    root /var/www;
    server_name $hostname "";
    include /etc/nginx/locations-enabled/*;
}
```
