"""The Flask App."""

# pylint: disable=broad-except

from flask import Flask, abort, jsonify, request
#from rq.job import Job
#from rq import Queue

from functions import some_long_function
#from redis_resc import redis_conn, redis_queue
from RedisQueue import RedisQueue

redisQueue = RedisQueue('test')
app = Flask(__name__)

@app.errorhandler(404)
def resource_not_found(exception):
    """Returns exceptions as part of a json."""
    return jsonify(error=str(exception)), 404


@app.route("/")
def home():
    """Show the app is working."""
    return "APP is currently running!"


@app.route("/enqueue", methods=["POST", "GET"])
def enqueue():
    """Enqueues a task into redis queue to be processes.
    Returns the job_id."""
    if request.method == "GET":
        query_param = request.args.get("external_id")
        if not query_param:
            abort(
                404,
                description=(
                    "No query parameter external_id passed. "
                    "Send a value to the external_id query parameter."
                ),
            )
        data = {"external_id": query_param}
    if request.method == "POST":
        data = request.json

    job = redis_queue.enqueue(
        some_long_function,
        ttl=30,  # This ttl will be used by RQ
        args=('http://nvie.com',)
        )

    return jsonify({"job_id": job.id})


@app.route("/check_status")
def check_status():
    """Takes a job_id and checks its status in redis queue."""
    job_id = request.args["job_id"]

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as exception:
        abort(404, description=exception)

    return jsonify({"job_id": job.id, "job_status": job.get_status()})


@app.route("/get_result")
def get_result():
    """Takes a job_id and returns the job's result."""
    job_id = request.args["job_id"]

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as exception:
        abort(404, description=exception)

    if not job.result:
        abort(
            404,
            description=f"No result found for job_id {job.id}. Try checking the job's status.",
        )
    return jsonify(job.result)

@app.route("/api/queue/pop")
# Envia requisicao pra fila para
# Obter primeiro elemento da lista e Removê-lo
# Status Code esperado: 200 / 500
# Retorno: "message": "body del mensaje"

@app.route("/api/queue/push")
# Envia requisicao pra fila para
# Adicionar nova mensagem para lista
# Status Code esperado: 200 / 404 / 500
# Retorno: {"message": "Pusheo un mensaje"}
def queueInsert():
    try:
        if request.method == "GET":
            abort(407, description=exception)
        if request.method == "POST":
            messageValue = request.args["message"]
            redisQueue.put(messageValue)
    except Exception as exception:
        abort(407, description=exception)

@app.route("/api/queue/count")
# Checa quantas mensagens existem pendentes
# para processamento em fila
# Status Code esperado: 200 / 404
# Retorno: {"count": 351}
def count():
    queue = redis_queue
    count = len(queue.jobs)
    return f"Jobs in queue: {count}"

@app.route("/api/queue/allData")
def getAllData():
    tamanho_fila = redisQueue.qsize()
    return f"Tamanho fila: {tamanho_fila}"

if __name__ == "__main__":
    app.run(debug=True)
