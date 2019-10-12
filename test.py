import log.client
from time import sleep

def mynewfunction():
    l = log.client.ClientLoggerJSON("Main", __file__)
    l2 = log.client.ClientLoggerJSON("Secondary", __file__)
    for i in range(1000):
        if i < 500:
            l2.logif(i % 2 != 0, "Hello Secondary %s" % i, "Sosi", context=mynewfunction.__name__)
        else:
            l.log("Hello Main %s" % i)
        sleep(.1)

if __name__ == "__main__":
    mynewfunction()

