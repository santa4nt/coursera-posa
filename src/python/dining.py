#!/usr/bin/python

import sys
import threading


class Chopstick(object):

    def __init__(self):
        self._cond = threading.Condition()
        self._holder = None

    def acquire(self, who, descr=''):
        # blocks until released by its current owner
        assert who

        # sanity check: attempting to acquire already-owned resource
        if self._holder == who:
            return

        self._cond.acquire()

        while self._holder:
            self._cond.wait()   # blocks until notified by current owner
        # this chopstick is available at this point
        self._holder = who
        print '%s picks up %s chopstick.' % (str(who), descr)

        self._cond.release()

    def release(self, descr=''):
        # release ownership of this chopstick

        # sanity check: if not owned by anyone, bail
        if not self._holder:
            return

        self._cond.acquire()

        print '%s puts down %s chopstick.' % (str(self._holder), descr)
        self._holder = None     # make this chopstick available
        self._cond.notify()

        self._cond.release()


class Philosopher(object):

    portions = 5

    def __init__(self, num, left, right):
        self._num = num
        self._left = left
        self._right = right

    @property
    def num(self):
        return self._num

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def _acquire_chopsticks(self):
        self._left.acquire(self, 'left')
        self._right.acquire(self, 'right')

    def _release_chopsticks(self):
        self._left.release('left')
        self._right.release('right')

    def run(self):
        while self.portions:
            self._acquire_chopsticks()
            print '%s eats.' % str(self)
            self._release_chopsticks()
            self.portions -= 1

    def __str__(self):
        return 'Philosopher %d' % self.num


def main(args):
    # setting the stage, create the philosophers and chopsticks
    (a, b, c, d, e) = (
            Chopstick(),
            Chopstick(),
            Chopstick(),
            Chopstick(),
            Chopstick(),
            )
    (p1, p2, p3, p4, p5) = (
            Philosopher(1, a, e),
            Philosopher(2, b, a),
            Philosopher(3, c, b),
            Philosopher(4, d, c),
            Philosopher(5, e, d),
            )

    # create thread objects for each philosopher
    threads = []
    for p in (p1, p2, p3, p4, p5):
        t = threading.Thread(target=p.run)
        threads.append(t)

    print 'Dinner is starting!'
    print

    # initially, assign each shared chopstick to the lower-numbered philosopher
    a.acquire(p1)
    b.acquire(p2)
    c.acquire(p3)
    d.acquire(p4)
    e.acquire(p1)   # this breaks the cycle in the initial state!

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print
    print 'Dinner is over!'
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))

