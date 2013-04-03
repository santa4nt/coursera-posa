/* Prompt:

The Dining Philosophers problem is as follows:  A group of philosophers are sitting down at a circular table
with food in the middle of the table, and a chopstick on each side of each philosopher.  At any time, they are
either thinking or eating.  In order to eat, they need to have two chopsticks.  If the chopstick to their left
or right is currently being used, they must wait for the other philosopher to put it down.  You may notice that
if each philosopher decides to eat at the same time, and each picks up the chopstick to his or her right, he or
she will not be able to eat, because everyone is waiting for the chopstick on their left.  This situation is
called "deadlock".  In this assignment, you will use the Monitor Object pattern in an algorithm to prevent deadlock.

You are to design a simple model of the Dining Philosophers problem in Java and an algorithm using the Monitor Object
pattern to prevent deadlock.  There should be 5 philosophers and 5 chopsticks, and each philosopher should eat exactly
five times, and be represented by a Thread.  The program should create output that looks something like this:

Dinner is starting!

Philosopher 1 picks up left chopstick.
Philosopher 1 picks up right chopstick.
Philosopher 1 eats.
Philosopher 3 picks up left chopstick
Philosopher 1 puts down right chopstick.
Philosopher 3 picks up right chopstick.
Philosopher 2 picks up left chopstick.
Philosopher 1 puts down left chopstick.
Philosopher 3 eats.
Philosopher 2 picks up right chopstick.
Philosopher 2 eats.
Philosopher 2 puts down right chopstick.
Philosopher 2 puts down left chopstick.
Philosopher 3 puts down right chopstick.
Philosopher 3 puts down left chopstick.
...
Dinner is over!

It is up to you to implement the Monitor Object pattern in Java to prevent deadlock.

*/

package com.swijaya.coursera.posa;

public class Dining {

    interface PhilosopherListener {
        public void onFinishedEating(Philosopher who);
    }

    static class Chopstick {

        private boolean dirty;      // if true, this chopstick is in use

        public boolean isDirty() {
            return dirty;
        }

        public void markDirty() {
            dirty = true;
        }

    }

    static class Philosopher extends Thread {

        private int id;
        private Chopstick left, right;
        private Waiter waiter;                  // both a monitor and a subscriber
        private PhilosopherListener listener;

        public Philosopher(int id, Chopstick left, Chopstick right, Waiter waiter) {
            this.id = id;
            this.left = left;
            this.right = right;
            this.waiter = waiter;
            setPhilosopherListener(waiter);
        }

        protected void setPhilosopherListener(PhilosopherListener listener) {
            assert (listener != null);
            this.listener = listener;
        }

        public Chopstick getLeftChopstick() {
            return left;
        }

        public Chopstick getRightChopstick() {
            return right;
        }

        public void pickUpChopsticks() throws InterruptedException {
            // each of these calls potentially blocks until notified (by the waiter)
            waiter.askPermissionForChopstick(left); System.out.println(this.toString() + " picks up left chopstick.");
            waiter.askPermissionForChopstick(right); System.out.println(this.toString() + " picks up right chopstick.");
        }

        public void eat() {
            System.out.println(this.toString() + " eats.");
            finishEating();
        }

        /**
         * Publish a "finished eating" event, where the subscriber's onFinishedEating() callback will be invoked.
         * Here, each callback is invoked when this philosopher is done eating for this round.
         */
        private void finishEating() {
            assert (listener != null);
            if (listener != null)
                listener.onFinishedEating(this);
        }

        @Override
        public void run() {
            int portion = 5;    // each philosopher eats five times
            try {
                for (; portion >=0; portion--) {
                    pickUpChopsticks();
                    eat();
                }
            } catch (InterruptedException e) {
                System.err.println(this.toString() + " choked!");
                e.printStackTrace();
            }
        }

        @Override
        public String toString() {
            return "Philosopher " + id;
        }
    }

    /**
     * As the synchronizing Monitor Object, the waiter observes the state of the "table": the state of each
     * philosopher and what resources (chopsticks) they hold. The waiter also acts as individual philosopher's
     * subscriber that gets called back when each philosopher is "done eating" for a round.
     */
    static class Waiter implements PhilosopherListener {

        /**
         * When a philosopher finishes eating, the waiter notifies all philosophers that are currently waiting
         * on the former's chopsticks. Note that since only one philosopher at a time can talk to the waiter,
         * this callback method is also marked synchronized, forcing each philosopher to own the monitor on
         * this waiter object before invoking this callback.
         *
         * @param who the philosopher that just finished eating
         */
        @Override
        public synchronized void onFinishedEating(Philosopher who) {
            // note that we need to also own the monitor of each chopstick to notify its waiting philosopher
            Chopstick left = who.getLeftChopstick();
            Chopstick right = who.getRightChopstick();

            synchronized (left) {
                left.notifyAll();
            }

            synchronized (right) {
                right.notifyAll();
            }
        }

        /**
         * Only one philosopher at a time can "ask permission" from the waiter to use their shared resources
         * (i.e. chopsticks). If the resource in question is in use, sleep (wait) until notified. Otherwise,
         * or when finally notified that the chopstick is now available, the thread that invoked this permission
         * will mark said chopstick as dirty.
         */
        public synchronized void askPermissionForChopstick(Chopstick chopstick) throws InterruptedException {
            synchronized (chopstick) {      // we need to own the monitor on said chopstick to wait on it
                if (chopstick.isDirty())
                    chopstick.wait();
                chopstick.markDirty();
            }
        }

    }

    public static void main(String[] args) throws Exception {
        // first, let's set the stage: five philosopher, five shared chopsticks, and one waiter (monitor)
        Waiter waiter = new Waiter();
        Chopstick[] chopsticks = new Chopstick[] {
                new Chopstick(),
                new Chopstick(),
                new Chopstick(),
                new Chopstick(),
                new Chopstick()
        };
        Philosopher[] philosophers = new Philosopher[] {
                new Philosopher(1, chopsticks[0], chopsticks[1], waiter),
                new Philosopher(2, chopsticks[1], chopsticks[2], waiter),
                new Philosopher(3, chopsticks[2], chopsticks[3], waiter),
                new Philosopher(4, chopsticks[3], chopsticks[4], waiter),
                new Philosopher(5, chopsticks[4], chopsticks[0], waiter)
        };

        System.out.println("Dinner is starting!\n");

        for (Philosopher philosopher : philosophers) {
            philosopher.start();
        }

        for (Philosopher philosopher : philosophers) {
            philosopher.join();
        }

        System.out.println("\nDinner is over!");
    }

}
