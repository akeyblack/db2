import redis
import random
import sys
import time

from multiprocessing import Process


def random_bit():
    return random.getrandbits(1)


class Worker(Process):
    __db = redis.Redis(host='localhost', port=6379, db=0)
    __pubsub = __db.pubsub()
    __pubsub.subscribe('worker_queue')
    __t = -1

    def __init__(self, t):
        super(Worker, self).__init__()
        self.__t = t

    def run(self):
        self.messages_processing()

    def message_processing(self, msg_to_process):
        inc = 1
        msg_owner = self.__db.hget(msg_to_process, "owner").decode('utf-8')
        msg_rec = self.__db.hget(msg_to_process, "rec").decode('utf-8')
        msg_text = self.__db.hget(msg_to_process, "text").decode('utf-8')
        self.__db.zincrby(f"user_msgs:{msg_owner}", inc, msg_to_process)
        if self.__t < 0:
            time.sleep(random.randint(1, 5))
        else:
            time.sleep(self.__t)
        print(msg_to_process)
        if bool(random_bit()):
            inc = 2
            self.__db.rpush(f"received_msgs:{msg_rec}", msg_to_process)
            self.__db.publish(f"msgs:{msg_rec}", msg_to_process)
            self.__db.zincrby("user_stats", 1, msg_owner)
        else:
            self.__db.publish("events", f"Spam from {msg_owner} to {msg_rec}. Text: {msg_text}")
            self.__db.zincrby("spammers", 1, msg_owner)
        self.__db.zincrby(f"user_msgs:{msg_owner}", inc, msg_to_process)

    def messages_processing(self):
        num = self.__db.llen("queue")
        for x in range(num):
            try:
                self.message_processing(self.__db.lpop("queue"))
            except Exception:
                break;

        for cur_msg in self.__pubsub.listen():
            if cur_msg['data'] != 1:
                try:
                    self.message_processing(self.__db.lpop("queue"))
                except Exception:
                    time.sleep(2)


if __name__ == '__main__':
    worker = Worker(-1)
    worker.start()
    worker.join()
