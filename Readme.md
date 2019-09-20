# Jarvis IT Asset Tracking
Jarvis is an asset tracking web application for tracking IT assets across a college campus. It is built on Django and MongoDB.
## Setting up Dev Environment
- Clone this repo
- install docker desktop (Select linux containers)
- Share local drive with docker daemon (this should be the drive you cloned this repo to)
- open vscode (must have [vscode-remote-development extension pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack))
- run vscode command "Remote Containers: Open Folder in Container" -> select the root project folder
- inside the container

    ```bash
    // sets up the database collections
    python manage.py migrate

    // create application superuser
    python manage.py createsuperuser    // follow prompts

    // start the dev webserver
    run                                 //alternatively 'python manage.py runserver 0.0.0.0:8000'
    ```
- open a browser and navigate to 'http://localhost:8000/'
