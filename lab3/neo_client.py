from neo4f_server import NeoServer
import os

clear = lambda: os.system('cls')


def print_options():
    print("[1] Users with tags")
    print("[2] Pairs of connected users with length N through sent or received messages")
    print("[3] Shortest path between users ")
    print("[4] Friends-spammers")
    print("[5] Unrelated users with tags")
    print("[6] Exit")


def print_list(lst):
    for x in lst:
        print(x)
    print()


def menu():
    option = 1
    server = NeoServer()

    while option != 0:
        clear()
        print_options()
        try:
            option = int(input("Enter your option: "))
        except Exception:
            continue
        if option == 1:
            print("Enter tags")
            string = input()
            print_list(server.get_users_by_tags(string.split(',')))
        elif option == 2:
            print("Enter n")
            try:
                n = int(input())
            except:
                continue
            print_list(server.get_pairs_with_n_length(n))
        elif option == 3:
            print("Enter users")
            arr = input().split(",")
            if len(arr) < 2:
                print("Enter 2 users")
                continue
            result = server.get_shortest(arr[0], arr[1])
            if not result:
                print("No relations or users do not exists")
            else:
                print_list(result)
        elif option == 4:
            print_list(server.get_spam_bounded())
        elif option == 5:
            print("Enter tags")
            string = input()
            print_list(server.get_unrelated_tags_related(string.split(',')))
        elif option == 6:
            break
        else:
            server.close()
            print("Invalid option")
        input()
        clear()


if __name__ == '__main__':
    menu()
