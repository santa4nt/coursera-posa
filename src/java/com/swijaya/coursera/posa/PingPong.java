/* Prompt:

You are to design a simple Java program where you create two threads, Ping and Pong, to alternately display
“Ping” and “Pong” respectively on the console.  The program should create output that looks like this:

Ready… Set… Go!

Ping!
Pong!
Ping!
Pong!
Ping!
Pong!
Done!

It is up to you to determine how to ensure that the two threads alternate printing on the console, and how to
ensure that the main thread waits until they are finished to print: “Done!”  The order does not matter
(it could start with "Ping!" or "Pong!").

 */

package com.swijaya.coursera.posa;
 
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.SynchronousQueue;

public class PingPong {

    static class Ball {
        public int lives;          // the number of times this ball can be bounced around
        public Ball(int lives) { this.lives = lives; }
    }

    static class Worker extends Thread {

        private String action;      // the action string that gets printed out (e.g. "Ping!")
        private BlockingQueue<Ball> queue;
        public Worker(String action, BlockingQueue<Ball> queue) {
            this.action = action;
            this.queue = queue;
        }

        @Override
        public void run() {
            Ball ball;
            boolean running = true;
            while (running) {
                try {
                    ball = queue.take();  // blocks until the ball is put back into the queue
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    return;
                }
                System.out.println(action);
                switch (--ball.lives) {
                    case 1:
                        // last bounce!
                        running = false;
                        break;
                    case 0:
                        // must drop ball and exit
                        return;
                }
                try {
                    queue.put(ball);    // blocks until someone is ready to take it from the queue
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    return;
                }
            }
        }
    }

    public static void main(String[] args) throws InterruptedException {
        BlockingQueue<Ball> queue = new SynchronousQueue<Ball>();
        Ball ball = new Ball(6);
        Worker ping = new Worker("Ping!", queue);
        Worker pong = new Worker("Pong!", queue);
        System.out.println("Ready... Set... Go!");
        ping.start();
        queue.put(ball);  // give "ping" the first chance to retrieve the ball
        pong.start();
        // wait until all threads finish
        ping.join();
        pong.join();
        System.out.println("Done!");
    }

}

