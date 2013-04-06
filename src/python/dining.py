#!/usr/bin/python

import sys
import threading
from Queue import Queue, Empty


stdout_lock = threading.RLock()     # a global lock to synchronize printing to stdout console
def syncprint(string):
    stdout_lock.acquire()
    print string
    stdout_lock.release()


REQUEST = 0
RESPONSE = 1


class Resource(object):

    def __init__(self, num):
        self._num = num
        self._holder = None
        # the "dirty" flag serves as a mechanism to prevent deadlock AND starvation
        # if this resource (chopstick) is "dirty", the current holder must give it up when asked
        # moreover, if the current holder is sending it over, he must clean it first
        self._dirty = False      

    @property
    def num(self):
        return self._num

    @property
    def dirty(self):
        return self._dirty

    @property
    def clean(self):
        return not self._dirty

    @property
    def holder(self):
        return self._holder

    @holder.setter
    def holder(self, holder):
        self._holder = holder

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
        self._dirty = False

    def __str__(self):
        return 'Resource(%s, dirty=%s)' % (repr(self._num), str(self._dirty))


class Agent(object):

    def __init__(self, num, resources_needed, capacity=5):
        self._num = num
        self._res_needed = resources_needed
        self._res_held = []
        self._neighbors = []

        # the number of times this agent does work
        self._capacity = capacity
        self._counter = 0

        # for message passing mechanism
        self._queue = Queue(maxsize=5)
        self._pend_queue = []
        self._alive = True

    def initialize(self, neighbors, initial_resources_held):
        self._neighbors = neighbors
        for res in initial_resources_held:
            self._res_held.append(res)
            res.holder = self

    @property
    def num(self):
        return self._num

    @property
    def full(self):
        return self._counter < self._capacity

    @property
    def alive(self):
        return self._alive

    def eat(self):
        """The "work" function.

        Pre-condition: This agent owns the resources it needs.
        Post-condition: Said resources are "dirty" after this work.

        """
        assert set(self._res_held) >= set(self._res_needed)
        syncprint('%s eats.' % str(self))
        self._counter += 1
        for res in self._res_held:
            res.mark_dirty()

    def clean(self, resource):
        """The "cleaning" function of a held resource.

        """
        assert resource in self._res_held
        if resource not in self._res_needed:
            assert False
            pass
        resource.mark_clean()

        # for printout purpose
        if resource is self._res_needed[0]:
            which = 'left'
        elif resource is self._res_needed[1]:
            which = 'right'
        else:
            assert False
        syncprint('%s puts down %s chopstick.' % (str(self), which))

    def claim(self, resource):
        """Claim a resource by putting it into the hold-list.

        """
        assert resource not in self._res_held
        self._res_held.append(resource)
        resource.holder = self

        # for printout purpose
        if resource is self._res_needed[0]:
            which = 'left'
        elif resource is self._res_needed[1]:
            which = 'right'
        else:
            assert False
        syncprint('%s picks up %s chopstick.' % (str(self), which))

    def send(self, msg):
        """Send a message to this agent by putting said message in said agent's
        internal queue. This call potentially blocks until a free slot is
        available.

        """
        self._queue.put(msg)

    def run(self):
        while True:
            # exit condition: we're at capacity and not holding any resource
            if self.full and (len(self._res_held) == 0):
                self._alive = False
                return
            elif not self.full:
                # note that this branch should be no-op if we are already holding
                # all the resources we need

                # for each resource we need that we are not already holding
                for res in [r for r in self._res_needed if r not in self._res_held]:
                    for neighbor in [n for n in self._neighbors if n.alive]:
                        # send a request for the required resource
                        req = (REQUEST, self, res)
                        neighbor.send(req)

            # now, pop (block if empty) a message from this agent's message queue
            try:
                message = self._queue.get(block=False)
            except Empty:
                pass
            else:
                msgtype, source, resource = message
                if msgtype == REQUEST:
                    if resource not in self._res_held:
                        # nothing to do, drop this message
                        pass
                    elif resource.clean:
                        # our neighbor is requesting a clean resource, we can pend it
                        self._pend_queue.append(message)
                    else:
                        # we are holding a dirty resource that is requested, we must give it up
                        # remove the resource from our hold-list
                        self._res_held = [res for res in self._res_held if res is not resource]
                        self.clean(resource)
                        resp = (RESPONSE, self, resource)
                        source.send(resp)
                elif msgtype == RESPONSE:
                    assert resource.clean
                    self.claim(resource)
                else:
                    assert False, 'Unknown message type'

            # check if we can eat
            if set(self._res_held) >= set(self._res_needed):
                self.eat()
                # now that we've potentially dirtied previously "clean" resources,
                # we should merge back requests that we pended because they were asking
                # for those resources
                for msg in self._pend_queue:
                    self.send(msg)      # take care not to block on this!
                self._pend_queue = []

    def __str__(self):
        return 'Philosopher %d' % self.num


def main(args):
    # setting the stage, create the philosophers and chopsticks
    (a, b, c, d, e) = (
            Resource('a'),
            Resource('b'),
            Resource('c'),
            Resource('d'),
            Resource('e'),
            )
    (p1, p2, p3, p4, p5) = (
            Agent(1, [a, e]),
            Agent(2, [b, a]),
            Agent(3, [c, b]),
            Agent(4, [d, c]),
            Agent(5, [e, d]),
            )

    # create thread objects for each philosopher
    threads = []
    for p in (p1, p2, p3, p4, p5):
        t = threading.Thread(target=p.run)
        threads.append(t)

    print 'Dinner is starting!'
    print

    # initially, assign each shared chopstick to the lower-numbered philosopher
    p1.initialize([p2, p5], [a, e])
    p2.initialize([p1, p3], [b,])
    p3.initialize([p2, p4], [c,])
    p4.initialize([p3, p5], [d,])
    p5.initialize([p4, p1], [])     # this means p5 initially holds nothing, breaking the cycle

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print
    print 'Dinner is over!'
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))

