#!/usr/bin/python

# Prompt:
#
# You are to design a simple Python program where you create two threads, Ping and Pong, to alternately display
# "Ping" and "Pong" respectively on the console.  The program should create output that looks like this:
#
# Ready... Set... Go!
#
# Ping!
# Pong!
# Ping!
# Pong!
# Ping!
# Pong!
# Done!
#
# It is up to you to determine how to ensure that the two threads alternate printing on the console, and how to
# ensure that the main thread waits until they are finished to print: "Done!"  The order does not matter
# (it could start with "Ping!" or "Pong!").
#

import sys
import threading
from Queue import Queue


class Ball(object):
    
    def __init__(self, lives):
        self.lives = lives      # the maximum number of times this ball can be bounced around


class Worker(object):

    def __init__(self, action):
        self.action = action    # e.g. 'Ping!', printed out during each loop
        self._queue = Queue(maxsize=1)
        self._colleague = None

    @property
    def colleague(self):
        return self._colleague

    @colleague.setter
    def colleague(self, colleague):
        self._colleague = colleague

    def offer(self, ball):
        self._queue.put(ball)

    def run(self):
        running = True
        while running:
            ball = self._queue.get()  # blocks until the ball is put into the queue
            print self.action
            ball.lives -= 1
            if (ball.lives <= 1):
                running = False
            # bounce the ball to the colleague
            self.colleague.offer(ball)


def main(args):
    ball = Ball(6)

    ping = Worker('Ping!')
    pong = Worker('Pong!')
    ping.colleague = pong
    pong.colleague = ping

    ping_thr = threading.Thread(target=ping.run)
    pong_thr = threading.Thread(target=pong.run)

    ping_thr.start()
    pong_thr.start()

    # start by giving "ping" the ball
    ping.offer(ball)

    # wait until both workers are done
    ping_thr.join()
    pong_thr.join()

    print 'Done!'


if __name__ == '__main__':
    sys.exit(main(sys.argv))

