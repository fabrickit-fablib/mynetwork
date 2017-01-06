# coding: utf-8

from fabkit import task
from fablib.mynetwork import MyNetwork


@task
def setup():
    mynetwork = MyNetwork()
    mynetwork.setup()

    return {'status': 1}
