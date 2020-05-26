# Segment Analyzer &middot; [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/your/your-project/blob/master/LICENSE)

## Developing

### Setting environment variables

For local development, set all required environment variables in a .env file

```.env
SECRET_KEY=something_secret
FLASK_APP=run
FLASK_ENV=development
DB=mongodb://localhost:27017/segment-analyzer
```

### Setting up Dev

```shell
https://github.com/oddeirikigland/segment-analyzer
cd segment-analyzer/
python setup.py install --user
pre-commit install
```

### Run the application

```shell
flask run
```
