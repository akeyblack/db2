from neo4j import GraphDatabase


class NeoServer:

    def __init__(self):
        self.__db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123123"))

    def close(self):
        self.__db.close()

    def registration(self, name):
        with self.__db.session() as session:
            session.run(f"CREATE (:User {{username:'{name}', online:false}})")

    def login(self, name):
        with self.__db.session() as session:
            session.run(f"MATCH (n:User {{username: '{name}'}}) SET n.online = true")

    def logout(self, name):
        with self.__db.session() as session:
            session.run(f"MATCH (n:User {{username: '{name}'}}) SET n.online = false")

    def create_message_relation(self, sender, rec, msg_id, tags, spam):
        with self.__db.session() as session:
            if spam:
                session.run(f"MATCH (a:User {{username:'{sender}'}}), (b:User {{username:'{rec}'}})"
                            f"MERGE (a)-[r:messages]->(b)"
                            f"ON CREATE SET r.all_messages=['{msg_id}'], r.spam=['{msg_id}'], r.tags=[]"
                            f"ON MATCH SET r.all_messages=r.all_messages+'{msg_id}', r.spam=r.spam+'{msg_id}'")

            if not spam:
                session.run(f"MATCH (a:User {{username:'{sender}'}}), (b:User {{username:'{rec}'}})"
                            f"MERGE (a)-[r:messages]->(b)"
                            f"ON CREATE SET r.all_messages=['{msg_id}'], r.spam=[], r.tags=[]"
                            f"ON MATCH SET r.all_messages=r.all_messages+'{msg_id}'")
            for tag in tags:
                session.run(f"MATCH (:User {{username:'{sender}'}})-[r]->(:User {{username:'{rec}'}})"
                            f"FOREACH(x in CASE WHEN '{tag}' in r.tags THEN [] ELSE [1] END |"
                            f"SET r.tags=r.tags+'{tag}')")

    def get_users_by_tags(self, tags):
        with self.__db.session() as session:
            query = ""
            for tag in tags:
                query += f"'{tag}' IN r.tags AND"
            query = query[:-3]

            return self.user_records_to_list(session.run(f"MATCH (u:User)-[r:messages]-(:User)"
                                                         f"WHERE {query}"
                                                         f"RETURN u.username"))

    def get_pairs_with_n_length(self, n):
        with self.__db.session() as session:
            return self.user_pairs_records_to_list(session.run(f"MATCH (u1:User)-[*{n}]->(u2:User) WHERE u1<>u2 "
                                                               f"RETURN u1.username,u2.username"))

    def get_shortest(self, user1, user2):
        with self.__db.session() as session:
            result = session.run(f"MATCH sh = shortestPath((u1:User {{username:'{user1}'}})-[*..10]-"
                                 f"(u2:User {{username: '{user2}'}}))"
                                 f"RETURN sh")
            if result.peek() is None:
                return False
            else:
                for x in result:
                    nodes = x[0].nodes
                    lst = list()
                    for node in nodes:
                        lst.append(node['username'])
                    return lst

    def get_spam_bounded(self):
        with self.__db.session() as session:
            return self.user_pairs_records_to_list(
                session.run(f"MATCH p = (u1:User)-[]->(u2:User)"
                            f"WHERE u1 <> u2 AND all(x in relationships(p) WHERE x.all_messages =x.spam) "
                            f"RETURN u1.username, u2.username"))

    def get_unrelated_tags_related(self, tags):
        with self.__db.session() as session:
            users = self.get_users_by_tags(tags)
            for user in users:
                for x in users:
                    if user != x:
                        result = session.run(f"MATCH  (u1:User {{username: '{user}'}}), (u2:User {{username: '{x}'}}) "
                                             "RETURN EXISTS((u1)-[:messages]-(u2))").single()[0]
                        if result:
                            users.remove(x)
            return users

    @staticmethod
    def user_records_to_list(recs):
        recs = list(recs)
        lst = list()
        for x in recs:
            x = list(x)
            lst.append(x[0])

        return list(set(lst))

    @staticmethod
    def user_pairs_records_to_list(recs):
        recs = list(recs)
        lst = list()
        for x in recs:
            x = list(x)
            lst.append(x)
        lst = set({tuple(i) for i in lst})
        return list(lst)
