import os

os.environ["ENV"] = "development"
os.environ["PORT"] = "5000"
os.environ["DB"] = "mongodb://mongodb:27017/segment"
os.system("python run.py")
