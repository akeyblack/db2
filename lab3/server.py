from multiprocessing import Process
import redis
import time


class Server:
    __db = redis.Redis(host='localhost', port=6379, db=0)
    __event_pubsub = __db.pubsub()
    __message_pubsub = __db.pubsub()

    def __init__(self):
        self.__db.sadd("users", "admin:admin")

    def event_sub(self):
        self.__event_pubsub.subscribe("events")
        for item in self.__event_pubsub.listen():
            if item['data'] == 1:
                continue
            self.__db.rpush("event_list", item['data'])
            self.__db.publish("event_journal", item['data'])

    def message_sub(self):
        self.__message_pubsub.subscribe("created_msgs")
        for msg in self.__message_pubsub.listen():
            if msg['data'] == 1:
                continue
            time.sleep(2)
            self.__db.lpush("queue", msg['data'])
            self.__db.publish("worker_queue", msg['data'])
            msg_owner = self.__db.hmget(msg['data'], "owner")[0]
            self.__db.zincrby(f"user_msgs:{msg_owner.decode('utf-8')}", 1, msg['data'])


if __name__ == '__main__':
    server = Server()
    p = Process(target=server.event_sub)
    pm = Process(target=server.message_sub)
    p.start()
    pm.start()
