# InSentive Demo App

This app was built with the ReactJS UI framework using the [Create React App](https://github.com/facebook/create-react-app) tool. It uses a Flask backend to serve API requests (api/app.py). You can access the app already running here: https://roemmele.github.io/InSentive.

For running locally, on the front end:

You'll need node.js (`nvm install node`).
Configure the "proxy" setting in ./package.json to specify the address where the Flask server will be running.
Inside the current directory, install the JS packages: `npm install`
Then run with: `npm start`

...and on the back-end:

Install the dependencies in InSentive/requirements.txt (`pip install -r requirements.txt`)
Inside api/, run the Flask app: `python app.py -model_path [PATH/TO/INFILLING/MODEL] -port 5000`
(Make sure the port/address matches what is in ./package.json)
You can download the infilling model trained on 10K books [here](https://drive.google.com/file/d/18E8IT__33bU24Nqws-9amY_obHZ0jVNG/view?usp=sharing) (same model being used in the demo linked above)
