import numpy as np
import pandas as pd
import dill
import copy
import seaborn as sns;
import optparse
import pathlib
import sys
current_dir = pathlib.Path(__file__).resolve().parent
sys.path.append(str(current_dir) + '/../')

from testConstants import *

sns.set()


def run_episodes(_mdp, _agent, step=50, episode=100, s=0, decision_cb=None, display_cb=None, pause_cb=None):
    if decision_cb is None: decision_cb = _agent
    df_list = list()
    for e in range(episode):
        # print("-------- new episode: {0:04} starts --------".format(e))
        # INIT ENV AND AGENT
        _mdp.reset()
        _agent.reset_of_episode()
        cumulative_reward = 0.0
        # GET STATE
        state = _mdp.get_cur_state()
        # SELECT ACTION
        action = decision_cb.act(state)
        _agent.update(state, action, 0.0, learning=False, goal=_mdp.goal_query)
        # _mdp.print_gird()

        # DISPLAY CURRENT STATE
        if display_cb is not None:
            display_cb(state)
            pause_cb()
        for t in range(1, step):
            # EXECUTE ACTION AND UPDATE ENV
            _mdp, reward, done, info = _mdp.step(action)
            cumulative_reward += reward
            # print(state.get_state(), action, reward, _mdp.get_visited(state))

            # GET STATE
            state = copy.deepcopy(_mdp.get_cur_state())

            # DISPLAY CURRENT STATE
            if display_cb is not None:
                display_cb(state)
                pause_cb()
            # _mdp.print_gird()

            # SELECT ACTION
            action = decision_cb.act(state)

            # UPDATE LEARNER
            _agent.update(state, action, reward, episode=e)

            # END IF DONE
            if done:
                # print(reward)
                # UPDATE LEARNER
                _agent.update(state, action, reward, episode=e)
                # print("The agent arrived at tearminal state.")
                # print("Exit")
                break

        #############
        # Logging
        #############
        # if e % int(episode/2 + 0.5) == 0:  # record agent's log every 250 episode
        #     _mdp.to_pickle(PKL_DIR + "mdp_{0}_{1}_{2}_{3}.pkl".format(_agent.name, _mdp.name, s, e))
        #     _agent.to_pickle(PKL_DIR + "{0}_{1}_{2}_{3}.pkl".format(_agent.name, _mdp.name, s, e))
        #     _agent.q_to_csv(CSV_DIR + "q_{0}_{1}_{2}_{3}.csv".format(_agent.name, _mdp.name, s, e))
        df_list.append([e, _agent.step_number, cumulative_reward, s, _agent.name, _mdp.name, _agent.alpha, _agent.gamma, _agent.epsilon, _agent.rmax, _agent.u_count, _agent.lookahead])
    df = pd.DataFrame(df_list, columns=['Episode', 'Timestep', 'Cumulative Reward', 'seed', 'AgentName', 'MDPName', 'alpha', 'gamma', 'epsilon', 'rmax', 'ucount', 'lookahead'])
    df.to_csv(CSV_DIR + "{0}_{1}_{2}_fin.csv".format(_agent.name, _mdp.name, s))
    _mdp.to_pickle(PKL_DIR + "mdp_{0}_{1}_{2}_fin.pkl".format(_agent.name, _mdp.name, s))
    _agent.q_to_csv(CSV_DIR + "q_{0}_{1}_{2}_fin.csv".format(_agent.name, _mdp.name, s))
    _agent.to_pickle(PKL_DIR + "{0}_{1}_{2}_fin.pkl".format(_agent.name, _mdp.name, s))



def runs_episodes(_mdp, _agent, step=50, episode=100, seed=10):
    print("Running experiment: {0} in {1}".format(_agent.name, _mdp.name))
    for s in range(0, seed):
        _agent.reset()
        print("-------- new seed: {0:02} starts --------".format(s))
        run_episodes(_mdp, _agent, step, episode, s)


def run_experiments(_mdp, _agents, step=50, episode=100, seed=10):
    for a in _agents:
        runs_episodes(_mdp, a, step, episode, seed)


def episode_data_to_df(tmp, df, agent, seed, columns=("Timestep", "episode", "seed", "agent")):
    plot_df = pd.DataFrame(columns=columns)
    plot_df.loc[:, columns[0]] = tmp[seed]
    plot_df.loc[:, columns[1]] = range(len(tmp[seed]))
    plot_df.loc[:, columns[2]] = seed
    plot_df.loc[:, columns[3]] = str(agent)
    df = df.append(plot_df)
    return df


def load_agent(filename):
    with open(filename, "rb") as f:
        return dill.load(f)


def parseOptions():
    optParser = optparse.OptionParser()
    optParser.add_option('-d', '--discount', action='store',
                         type='float', dest='discount', default=0.9,
                         help='Discount on future (default %default)')
    optParser.add_option('-e', '--epsilon', action='store',
                         type='float', dest='epsilon', default=0.1,
                         metavar="E", help='Chance of taking a random action in q-learning (default %default)')
    optParser.add_option('-l', '--learningRate', action='store',
                         type='float', dest='alpha', default=0.5,
                         metavar="L", help='TD learning rate (default %default)')
    optParser.add_option('-i', '--iterations', action='store',
                         type='int', dest='iters', default=50,
                         metavar="I", help='Number of rounds of value iteration (default %default)')
    optParser.add_option('-k', '--episodes', action='store',
                         type='int', dest='episodes', default=100,
                         metavar="K", help='Number of epsiodes of the MDP to run (default %default)')
    optParser.add_option('-t', '--lookahead', action='store',
                         type='int', dest='lookahead', default=10,
                         metavar="T", help='Number of times of the planning to look ahead (default %default)')
    optParser.add_option('-a', '--agent', action='store', metavar="A",
                         type='string', dest='agent', default="q-learning",
                         help='Agent type (options are \'q-learning\', \'sarsa\' and \'rmax\', \'dynaq\' default %default)')
    optParser.add_option('-p', '--pause', action='store_true',
                         dest='pause', default=False,
                         help='Pause GUI after each time step when running the MDP')
    optParser.add_option('-q', '--quiet', action='store_true',
                         dest='quiet', default=False,
                         help='Skip display of any learning episodes')
    optParser.add_option('-s', '--speed', action='store', metavar="S", type=float,
                         dest='speed', default=100.0,
                         help='Speed of animation, S > 1.0 is faster, 0.0 < S < 1.0 is slower (default %default)')
    # optParser.add_option('-v', '--valueSteps', action='store_true', default=False,
    #                      help='Display each step of value iteration')
    optParser.add_option('-m', '--manual', action='store_true',
                         dest='manual', default=False,
                         help='Manually control agent')

    opts, args = optParser.parse_args()

    if opts.manual and opts.agent != 'q':
        print('## Disabling Agents in Manual Mode (-m) ##')
        opts.agent = None

    if opts.manual:
        opts.pause = True

    return opts



if __name__ == "__main__":

    from RL.mdp.MDPGridWorld import MDPGridWorld

    from RL.agent.qlearning import QLearningAgent
    from RL.agent.sarsa import SarsaAgent
    from RL.agent.rmax import RMAXAgent
    from RL.agent.dynaq import DynaQAgent

    opts = parseOptions()

    np.random.seed(0)
    ###########################
    # GET THE GRIDWORLD
    ###########################
    width, height = 5, 5
    init_loc = (1, 0)
    starts_loc=((1, 0), (0, 4), )
    goals_loc = ((4, 4), )
    # starts_loc=((1, 0), )
    # goals_loc = ((4, 4), )
    walls_loc = ((3, 1), (3, 2), (3, 3), )
    # walls_loc =()
    holes_loc = ()
    env = MDPGridWorld(width, height, starts_loc=starts_loc, is_rand_goal=True, is_rand_init=True,
                       init_loc=init_loc, goals_loc=goals_loc, walls_loc=walls_loc, holes_loc=holes_loc, name="testEnv")
    env.set_slip_prob(0.3)
    env.set_step_cost(0.0)
    env.set_hole_cost(1.0)
    env.set_goal_reward(1.0)
    mdp = env

    ###########################
    # GET THE DISPLAY ADAPTER
    ###########################
    from RL.mdp import display as graphic

    display = graphic.GraphicsGridworldDisplay(mdp)
    try:
        display.start()
    except KeyboardInterrupt:
        sys.exit(0)

    ###########################
    # GET THE AGENT
    ###########################
    qlearning = QLearningAgent(mdp.get_actions(), name="QLearning", alpha=opts.alpha, gamma=opts.discount, epsilon=opts.epsilon, explore="uniform")
    sarsa = SarsaAgent(mdp.get_actions(), name="Sarsa", alpha=opts.alpha, gamma=opts.discount, epsilon=opts.epsilon, explore="uniform")
    rmax = RMAXAgent(mdp.get_actions(), name="RMAX", rmax=1, u_count=2, gamma=opts.discount, epsilon=opts.epsilon)
    dynaq = DynaQAgent(mdp.get_actions(), name="DynaQ", alpha=opts.alpha, gamma=opts.discount, epsilon=opts.epsilon, lookahead=opts.lookahead, explore="uniform")
    agent = None
    if opts.agent == 'q-learning': agent = qlearning
    elif opts.agent == 'sarsa': agent = sarsa
    elif opts.agent == 'rmax': agent = rmax
    elif opts.agent == 'dynaq': agent = dynaq

    agent = rmax
    
    # DISPLAY Q/V VALUES BEFORE SIMULATION OF EPISODES
    try:
        if not opts.manual and opts.agent == 'value':
            display.displayValues(agent, message="VALUES AFTER " + str(opts.iters) + " ITERATIONS")
            display.pause()
            display.displayQValues(agent, message="Q-VALUES AFTER " + str(opts.iters) + " ITERATIONS")
            display.pause()
    except KeyboardInterrupt:
        sys.exit(0)

    # FIGURE OUT WHAT TO DISPLAY EACH TIME STEP (IF ANYTHING)
    messageCallback = lambda x: print(x)
    if opts.quiet:
        displayCallback = lambda x: None
        messageCallback = lambda x: None
    else:
        displayCallback = lambda state: display.displayQValues(agent, state, "CURRENT Q-VALUES")

    # FIGURE OUT WHETHER TO WAIT FOR A KEY PRESS AFTER EACH TIME STEP
    pauseCallback = lambda: None
    if opts.pause:
        pauseCallback = lambda: display.pause()

    # FIGURE OUT WHETHER THE USER WANTS MANUAL CONTROL (FOR DEBUGGING AND DEMOS)
    if opts.manual:
        decisionCallback = graphic.User(mdp.get_actions())
    else:
        decisionCallback = agent



    ###########################
    # RUN
    ###########################
    run_episodes(mdp, agent, step=opts.iters, episode=opts.episodes, decision_cb=decisionCallback ,display_cb=displayCallback, pause_cb=pauseCallback)
    # run_experiments(mdp, agents, step=50, episode=100, seed=5)


    # DISPLAY POST-LEARNING VALUES / Q-VALUES
    if not opts.manual:
        try:
            displayCallback = lambda state: display.displayQValues(agent, state, "CURRENT Q-VALUES")
            display.displayQValues(agent, message="Q-VALUES AFTER " + str(opts.episodes) + " EPISODES")
            display.pause()
            display.displayValues(agent, message="VALUES AFTER " + str(opts.episodes) + " EPISODES")
            display.pause()
        except KeyboardInterrupt:
            sys.exit(0)