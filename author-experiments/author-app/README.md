# InSentive Human Authoring Task

This code recreates the app that was used to conduct the human authoring experiment, where participants wrote infilled sentences before and after observing generated examples. It loads the authoring prompts and generated examples from input_data/ and writes the sentence responses to user_outputs/. See the paper for details about the design of this task.

This app was built with the ReactJS UI framework using the [Create React App](https://github.com/facebook/create-react-app) tool. It uses a Flask backend to serve API requests (api/app.py).

For running locally, on the front end:

You'll need node.js (`nvm install node`).
Configure the "proxy" setting in ./package.json to specify the address where the Flask server will be running.
Inside the current directory, install the JS packages: `npm install`
Then run with: `npm start`

...and on the back-end:

Install the dependencies in InSentive/requirements.txt (`pip install -r requirements.txt`)
Inside api/, run the Flask app: `flask run --port 5000`
(Make sure the port/address matches what is in ./package.json)
