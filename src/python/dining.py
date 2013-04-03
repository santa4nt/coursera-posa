#!/usr/bin/python

import sys
import threading


stdout_lock = threading.RLock()     # a global lock to synchronize printing to stdout console
def syncprint(string):
    stdout_lock.acquire()
    print string
    stdout_lock.release()


class Chopstick(object):

    def __init__(self):
        self._cond = threading.Condition()
        self._holder = None
        # the "dirty" flag serves as a mechanism to prevent deadlock AND starvation
        # if this resource (chopstick) is "dirty", the current holder must give it up when asked
        # moreover, if the current holder is sending it over, he must clean it first
        self._dirty = False      

    @property
    def dirty(self):
        return self._dirty

    @property
    def clean(self):
        return not self._dirty

    def _init_holder(self, who):
        """Initialization function: set the initial holder of this resource, and mark it as dirty.

        """
        who.pickup(self)
        self._holder = who
        self._dirty = True

    def mark_dirty(self):
        # since we might have philosophers waiting for this chopstick to become dirty,
        # we do additional notification on top of marking this chopstick dirty
        self._cond.acquire()
        self._dirty = True
        self._cond.notify()
        self._cond.release()

    def mark_clean(self):
        self._dirty = False

    def acquire(self, who):
        """Send a request to the current holder to acquire this resource.

        If the current holder is holding a "clean" resource (i.e. they have yet to use the
        resource), then this call will block until notified by the current holder.

        """
        assert who

        # sanity check: attempting to acquire already-owned resource
        if self._holder is who:
            return

        self._cond.acquire()

        while self._holder is not who:
            if self.dirty:
                # the current holder is holding a "dirty" resource, he must give it up
                self._holder.putdown(self)  # he marks the resource clean (and prints out action to stdout)
                self._holder = who
            else:
                # the current holder has not had a chance to use the resource yet (it is "clean")
                # so we block until the former notifies us that he is done
                self._cond.wait()
                # when we wake up, the resource should now have been marked "dirty"
                assert self.dirty

        self._holder.pickup(self)   # prints out action to stdout

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

    def putdown(self, chopstick):
        """The intermediary step in the process of giving up the chopstick resource
        to a contending neighbor.

        We mark the resource as "clean", and print out our action to stdout.

        """
        if chopstick is self.left:
            which = 'left'
        elif chopstick is self.right:
            which = 'right'
        else:
            assert False

        chopstick.mark_clean()
        syncprint('%s puts down %s chopstick.' % (str(self), which))

    def pickup(self, chopstick):
        """The intermediary step in the process of receiving a chopstick that a
        contending neighbor is giving up.

        At this point, said neighbor should already have marked this resource "clean".

        """
        if chopstick is self.left:
            which = 'left'
        elif chopstick is self.right:
            which = 'right'
        else:
            assert False

        assert chopstick.clean
        syncprint('%s picks up %s chopstick.' % (str(self), which))

    def _acquire_chopsticks(self):
        self._left.acquire(self)
        self._right.acquire(self)

    def _eat(self):
        syncprint('%s eats.' % str(self))
        # the process of eating would mark the resources uses as "dirty"
        self._left.mark_dirty()
        self._right.mark_dirty()

    def run(self):
        while self.portions:
            self._acquire_chopsticks()
            self._eat()
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
    a._init_holder(p1)
    b._init_holder(p2)
    c._init_holder(p3)
    d._init_holder(p4)
    e._init_holder(p1)   # this breaks the cycle in the initial state!

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print
    print 'Dinner is over!'
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))

