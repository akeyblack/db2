from multiprocessing import Process
from neo4f_server import NeoServer as Neo

import os
import redis
import atexit
import keyboard
import datetime


def clear():
    return os.system('cls')


class Client:
    __db = redis.Redis(host='localhost', port=6379, db=0)
    __pubsub = __db.pubsub()
    __user_id = ""
    __user_role = 0
    __neo = Neo()

    __pubsub.subscribe("event_journal")

    def get_role(self):
        return self.__user_role

    def login(self, name, password):
        if name == "":
            return False
        if password == "":
            if int(self.__db.sismember("users", f"{name}:null")) != 1:
                self.__db.sadd("users", f"{name}:null")
                self.__neo.registration(name)
            self.__user_id = name
            self.__neo.login(name)
        else:
            if int(self.__db.sismember("users", f"{name}:{password}")) == 1:
                self.__user_id = name
                self.__user_role = 1
            else:
                print("Wrong pass")
                return False
        self.__db.sadd("users_online", self.__user_id)
        self.__db.publish("events", f"Login by {self.__user_id} at {datetime.datetime.now()}")
        return True

    def send_message(self, username, message, tags):
        if tags is None:
            tags = list()
        if int(self.__db.sismember("users", f"{username}:null")) != 1:
            return False
        else:
            new_num = self.__db.zcard(f"user_msgs:{self.__user_id}") + 1
            msg_id = f"msg:{self.__user_id}{new_num}"

            self.__db.hset(msg_id, "text", message)
            self.__db.hset(msg_id, "rec", username)
            self.__db.hset(msg_id, "owner", self.__user_id)

            tag_string = ""
            if len(tags) > 0:
                for x in tags:
                    tag_string += str(x) + ","
            self.__db.hset(msg_id, "tags", tag_string)

            self.__db.zadd(f"user_msgs:{self.__user_id}", {msg_id: 1})
            self.__db.publish("created_msgs", msg_id)
            return True

    def get_messages(self):
        msg_list = []
        id_list = []
        for i in range(self.__db.llen(f"received_msgs:{self.__user_id}")):
            id_list.append(self.__db.lindex(f"received_msgs:{self.__user_id}", i))
        for m_id in id_list:
            msg_info = self.__db.hmget(m_id, {"text", "owner"})
            self.__db.zadd(f"user_msgs:{msg_info[1].decode('utf-8')}", {m_id: 6})
            msg_list.append(f"{msg_info[1].decode('utf-8')}: {msg_info[0].decode('utf-8')}")
        return msg_list

    def get_journal(self):
        j_list = []
        for x in range(self.__db.llen("event_list")):
            j_list.append(self.__db.lindex("event_list", x).decode("utf-8"))
        return j_list

    def listen_for_messages(self):
        msg_pubsub = self.__db.pubsub()
        msg_pubsub.subscribe(f"msgs:{self.__user_id}")
        for imsg in msg_pubsub.listen():
            if imsg['data'] != 1:
                msg_info = self.__db.hmget(imsg['data'], {"text", "owner"})
                self.__db.zadd(f"user_msgs:{msg_info[1].decode('utf-8')}", {imsg: 6})
                print(f"{msg_info[1].decode('utf-8')}: {msg_info[0].decode('utf-8')}")

    def listen_for_journal(self):
        for event in self.__pubsub.listen():
            if event['data'] != 1:
                print(event['data'].decode("utf-8"))

    def get_users_list(self):
        u_list = []
        for u in self.__db.smembers("users_online"):
            u_list.append(u.decode("utf-8"))
        return u_list

    def get_statistics(self, num):
        stat_list = []
        if self.__user_role == 1:
            spammers = self.__db.zrevrange("spammers", 0, num-1, withscores=True)
            favorite_users = self.__db.zrevrange("user_stats", 0, num-1, withscores=True)
            stat_list.append(f"Top {num} spammers:")
            for spammer in spammers:
                stat_list.append(f"{spammer[0].decode('utf-8')}: {int(spammer[1])}")
            stat_list.append(f"Top {num} true users:")
            for fav in favorite_users:
                stat_list.append(f"{fav[0].decode('utf-8')}: {int(fav[1])}")
        else:
            stat_list.append("Created: {}".format(self.__db.zcount(f"user_msgs:{self.__user_id}", 1, 1)))
            stat_list.append("Queued: {}".format(self.__db.zcount(f"user_msgs:{self.__user_id}", 2, 2)))
            stat_list.append("Checking for spam: {}".format(self.__db.zcount(f"user_msgs:{self.__user_id}", 3, 3)))
            stat_list.append("Blocked due to spam: {}".format(self.__db.zcount(f"user_msgs:{self.__user_id}", 4, 4)))
            stat_list.append("Sent: {}".format(self.__db.zcount(f"user_msgs:{self.__user_id}", 5, 5)))
            stat_list.append("Delivered: {}".format(self.__db.zcount(f"user_msgs:{self.__user_id}", 6, 6)))
        return stat_list

    def exit_fun(self):
        if self.__user_id == "":
            return
        self.__db.srem("users_online", self.__user_id)
        self.__neo.logout(self.__user_id)
        self.__db.publish("events", f"Logout by {self.__user_id} at {datetime.datetime.now()}")
        self.__db.save()


if __name__ == '__main__':
    cl = Client()
    while True:
        clear()
        print("Input username and/or password:")
        n = input()
        passw = input()
        if not cl.login(n, passw):
            continue
        else:
            usr_role = cl.get_role()
            atexit.register(cl.exit_fun)
            while True:
                clear()
                if usr_role != 1:
                    print("1.My messages\n2.Send message\n3.Statistics")
                else:
                    print("1.Journal\n2.Users list\n3.Statistics")
                print("\nPress something to continue...")
                key = input()
                clear()
                li = []
                if key == "1":
                    if usr_role == 1:
                        li = cl.get_journal()
                        clear()
                        print("Press something to return...\n")
                        for item in li:
                            print(item)
                        p = Process(target=cl.listen_for_journal)
                        p.start()
                        input()
                        p.terminate()
                        continue
                    else:
                        li = cl.get_messages()
                        clear()
                        print("Press something to return...\n")
                        for item in li:
                            print(item)
                        p = Process(target=cl.listen_for_messages)
                        p.start()
                        input()
                        p.terminate()
                        continue
                elif key == "2":
                    if usr_role == 1:
                        li = cl.get_users_list()
                    else:
                        clear()
                        print("Enter username and message")
                        usrnm = input()
                        msg = input()
                        if cl.send_message(usrnm, msg):
                            print("Done")
                        else:
                            print("User not found")
                        input("\nPress something to continue...")
                        continue
                elif key == "3":
                    nums = 1
                    if usr_role == 1:
                        print("Enter n:")
                        nums = int(input())
                    li = cl.get_statistics(nums)
                else:
                    continue

                for item in li:
                    print(item)
                print("\nPress something to continue...")
                input()
