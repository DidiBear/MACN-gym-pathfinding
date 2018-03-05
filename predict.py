import gym
import gym_pathfinding
from time import sleep
import tensorflow as tf 
import numpy as np 
from model import MACN
from itertools import permutations
### MACN conf

# VIN conf
k = 10
ch_i = 2
ch_h = 150
ch_q = 4

# DNC conf
hidden_size = 256
memory_size = 32
word_size = 8
num_reads = 4
num_writes = 1

episodes = 20


imsize = 7

def main():

    # Input tensor: Stack obstacle image and goal image, i.e. ch_i = 2
    X = tf.placeholder(tf.float32, shape=[None, imsize, imsize, 2], name='X')

    # MACN model
    macn = MACN(X, k=k, ch_i=ch_i, ch_h=ch_h, ch_q=ch_q, 
        access_config={
            "memory_size": memory_size, "word_size": word_size, "num_reads": num_reads, "num_writes": num_writes
        }, 
        controller_config={
            "hidden_size": hidden_size
        }
    )


    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, "./model/weights.ckpt")

        env = gym.make('partially-observable-pathfinding-free-{n}x{n}-d2-v0'.format(n=imsize))

        dones = 0
        for episode in range(episodes):
            env.seed(episode)
            print(episode, end="\r")

            state = env.reset()
            for timestep in range(15):
                env.render()
                sleep(0.2)

                grid, grid_goal = parse_state(state)

                actions_probabilities = sess.run([macn.prob_actions], feed_dict={
                    X: [np.stack([grid, grid_goal], axis=2)],
                })
                
                action = np.argmax(actions_probabilities)
                state, reward, done, _ = env.step(action)

                if done:
                    dones += 1
                    break
        print("accuracy : {}/{}".format(dones, episodes))
        env.close()

def parse_state(state):
    goal = state == 3
    state[goal] = 0

    return state, create_goal_grid(state.shape, goal)

def create_goal_grid(shape, goal):
    goal_grid = np.zeros(shape, dtype=np.int8)
    goal_grid[goal] = 10
    return goal_grid

if __name__ == "__main__":
    main()
