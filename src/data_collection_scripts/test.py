from clients.praw_client import PrawClient
import os
import sys


def tester():
    client = PrawClient()
    print(client)

    # print("Current Working Directory:", os.getcwd())
    # print("sys.path entries:")
    # for p in sys.path:
    #     print("-", p)


tester()
