from math import log2

import stable_baselines3 as SBL3
from gym import Env, spaces

class DummyEnv(Env):
    def __init__(self):
        super(DummyEnv, self).__init__()
    def set_meta(self, num_legal_actions, num_possible_obs):
        self.action_space = spaces.Discrete(num_legal_actions)
        self.observation_space = spaces.Discrete(num_possible_obs)
    def set_rewards_and_observs(self, rewards, observs):
        self.rewards = rewards
        self.observs = observs
        self.i = 1
    def reset(self):
        return self.observs[0]
    def step(self, action):
        obs = self.observs[self.i]
        reward = self.rewards[self.i]
        self.i += 1
        return obs, reward, False, {}

dummy_env = DummyEnv()

cache_A2C = {}
cache_DQN = {}
cache_PPO = {}

def agent_A2C(prompt, num_legal_actions, num_possible_obs):
    dummy_env.set_meta(num_legal_actions, num_possible_obs)
    meta = (num_legal_actions, num_possible_obs)
    num_observs = (len(prompt)+1)/3
    train_on_len = 3*pow(2, int(log2(num_observs)))-1
    train_on = prompt[:train_on_len]

    if not((train_on, meta) in cache_A2C):
        rewards = [train_on[i+0] for i in range(0,train_on_len,3)]
        observs = [train_on[i+1] for i in range(0,train_on_len,3)]
        dummy_env.set_rewards_and_observs(rewards, observs)

        A = SBL3.A2C('MlpPolicy', dummy_env, n_steps=len(rewards)-1, seed=0)

        A.learn(len(rewards)-1)
        cache_A2C[(train_on, meta)] = A
    else:
        A = cache_A2C[(train_on, meta)]

    action, _ = A.predict(prompt[-1])
    return action

def agent_PPO(prompt, num_legal_actions, num_possible_obs):
    dummy_env.set_meta(num_legal_actions, num_possible_obs)
    meta = (num_legal_actions, num_possible_obs)
    num_observs = (len(prompt)+1)/3
    train_on_len = 3*pow(2, int(log2(num_observs)))-1
    train_on = prompt[:train_on_len]

    if not((train_on, meta) in cache_PPO):
        rewards = [train_on[i+0] for i in range(0,train_on_len,3)]
        observs = [train_on[i+1] for i in range(0,train_on_len,3)]
        dummy_env.set_rewards_and_observs(rewards, observs)
        n_steps = len(rewards)-1

        if n_steps < 2:
            return 0

        A = SBL3.PPO('MlpPolicy', dummy_env, n_steps=n_steps, batch_size=n_steps, seed=0)

        A.learn(len(rewards)-1)
        cache_PPO[(train_on, meta)] = A
    else:
        A = cache_PPO[(train_on, meta)]

    action, _ = A.predict(prompt[-1])
    return action

def agent_DQN(prompt, num_legal_actions, num_possible_obs):
    dummy_env.set_meta(num_legal_actions, num_possible_obs)
    meta = (num_legal_actions, num_possible_obs)
    num_observs = (len(prompt)+1)/3
    train_on_len = 3*pow(2, int(log2(num_observs)))-1
    train_on = prompt[:train_on_len]

    if not((train_on, meta) in cache_DQN):
        rewards = [train_on[i+0] for i in range(0,train_on_len,3)]
        observs = [train_on[i+1] for i in range(0,train_on_len,3)]
        dummy_env.set_rewards_and_observs(rewards, observs)
        n_steps = len(rewards)-1

        if n_steps < 4:
            return 0

        A = SBL3.DQN('MlpPolicy', dummy_env, learning_starts=1, seed=0)

        A.learn(n_steps - (n_steps%4))
        cache_DQN[(train_on, meta)] = A
    else:
        A = cache_DQN[(train_on, meta)]

    action, _ = A.predict(prompt[-1])
    return action

agent_DQN.requires_numpy_transl = True

