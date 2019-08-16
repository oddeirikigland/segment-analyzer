import os
from flask import request, jsonify

from constants import ROOT_DIR
from modules.app import app  # , mongo
from modules import logger


LOG = logger.get_root_logger(
    os.environ.get(__name__),
    filename=os.path.join(ROOT_DIR, "modules/logger/output.log"),
)


@app.route("/user", methods=["GET"])
def user():
    if request.method == "GET":
        # query = request.args
        data = {"name": "Ole", "age": 20}  # mongo.db.users.find_one(query)
        return jsonify(data), 200
