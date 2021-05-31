from server import Server
from client import Client
from worker import Worker
from multiprocessing import Process
from tags import tags as tg

import random
import time

if __name__ == '__main__':
    my_server = Server()

    p = Process(target=my_server.event_sub)
    pm = Process(target=my_server.message_sub)
    p.start()
    pm.start()

    print('Enter N workers')
    n_workers = int(input())

    print('Enter T workers')
    workers_t = int(input())

    workers = [None] * n_workers
    for i in range(n_workers):
        workers[i] = Worker(workers_t)
        workers[i].start()

    print("Enter N users")
    n_users = int(input())

    clients = [None] * n_users
    for i in range(n_users):
        clients[i] = Client()
        clients[i].login(f"user{i}", "")

    print("Clients created")

    for x in range(2):
        for i in range(n_users):
            tags = list()
            for it in random.sample(range(0, 5), random.randint(0, 3)):
                tags.append(tg[it])
            sender = i
            rec = sender
            while rec == sender:
                rec = random.randint(0, n_users)
            clients[i].send_message(f"user{rec}", f"Hi, user{rec}", tags)

    print("Users created")

    for i in range(n_users):
        time.sleep(5)
        clients[i].exit_fun()
        print(f"User{i} goes offline")

    p.join()
    pm.join()
