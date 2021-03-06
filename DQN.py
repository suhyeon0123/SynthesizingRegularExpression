from queue import PriorityQueue
import math
import numpy as np
from collections import namedtuple
import torch.optim as optim
from util import *
from models import *
from parsetree import *
import configparser
import argparse
from torch.nn.utils.rnn import pad_sequence

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--examples", type=int,
                    help="Example number")
parser.add_argument("-u", "--unambiguous", help="Set ambiguity",
                    action="store_true")
parser.add_argument("-p", "--prioritized", help="Use prioritized replay buffer", action="store_true")
args = parser.parse_args()

from config import *

# GPU를 사용할 경우
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------------


Transition = namedtuple('Transition',
                        ('state', 'pos_example', 'neg_example', 'action', 'next_state', 'reward', 'done'))

from collections import deque


class ReplayBuffer(object):
    def __init__(self, capacity, unusual_sample_factor=0.99):
        self.buffer = deque(maxlen=capacity)
        self.unusual_sample_factor = unusual_sample_factor

    def push(self, *args):
        self.buffer.append(Transition(*args))
        # print(tensor_to_regex(args[0]), args[3][0][0].item(), tensor_to_regex(args[4]), args[5], args[6])

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def prioritized_sample(self, batch_size):
        buffer = sorted(self.buffer, key=lambda replay: abs(replay.reward), reverse=True)
        p = np.array([self.unusual_sample_factor ** i for i in range(len(buffer))])
        p = p / sum(p)
        sample_idxs = np.random.choice(np.arange(len(buffer)), size=batch_size, p=p)
        sample_output = [buffer[idx] for idx in sample_idxs]
        sample_output = np.reshape(sample_output, (batch_size, -1))
        return sample_output

    def __len__(self):
        return len(self.buffer)


class NaivePrioritizedBuffer(object):
    def __init__(self, capacity, prob_alpha=0.6):
        self.prob_alpha = prob_alpha
        self.capacity = capacity
        self.buffer = []
        self.pos = 0
        self.priorities = np.zeros((capacity,), dtype=np.float32)

    def push(self, *args):
        max_prio = self.priorities.max() if self.buffer else 1.0

        if len(self.buffer) < self.capacity:
            self.buffer.append(Transition(*args))
        else:
            self.buffer[self.pos] = Transition(*args)

        self.priorities[self.pos] = max_prio
        self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size, beta=0.4):
        if len(self.buffer) == self.capacity:
            prios = self.priorities
        else:
            prios = self.priorities[:self.pos]

        probs = prios ** self.prob_alpha
        probs /= probs.sum()

        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        samples = [self.buffer[idx] for idx in indices]

        total = len(self.buffer)
        weights = (total * probs[indices]) ** (-beta)
        weights /= weights.max()
        weights = np.array(weights, dtype=np.float32)

        return samples, indices, weights

    def update_priorities(self, batch_indices, batch_priorities):
        for idx, prio in zip(batch_indices, batch_priorities):
            self.priorities[idx] = prio

    def __len__(self):
        return len(self.buffer)


# ----------------------


policy_net = DuelingDQN().to(device)

# policy_net.load_state_dict(torch.load('saved_model/DQN.pth'))

target_net = DuelingDQN().to(device)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters(), lr=0.00025)
# optimizer = optim.Adam(policy_net.parameters(), lr=0.001)


if args.prioritized:
    memory = NaivePrioritizedBuffer(REPALY_MEMORY_SIZE)
else:
    memory = ReplayBuffer(REPALY_MEMORY_SIZE)

steps_done = 0

scanned = set()


# -----------------------------------

def select_action(regex_tensor, pos_tensor, neg_tensor):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
                    math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            a = policy_net(regex_tensor.view(1, -1), pos_tensor.view(1, -1), neg_tensor.view(1, -1))  # (1,6)
            return torch.argmax(a).view(-1, 1)
    else:
        return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long)


# -----------------------------------

beta_start = 0.4
beta_frames = 100000
beta_by_frame = lambda frame_idx: min(1.0, beta_start + frame_idx * (1.0 - beta_start) / beta_frames)


def optimize_model(beta=0.4):
    if len(memory) < REPLAY_INITIAL:
        return torch.FloatTensor([0])

    if args.prioritized:
        transitions, indices, weights = memory.sample(BATCH_SIZE, beta)
    else:
        transitions = memory.sample(BATCH_SIZE)
    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). 이것은 batch-array의 Transitions을 Transition의 batch-arrays로
    # 전환합니다.
    batch = Transition(*zip(*transitions))

    state_batch = pad_sequence(batch.state, batch_first=True)
    pos_example_batch = pad_sequence(batch.pos_example, batch_first=True)
    neg_example_batch = pad_sequence(batch.neg_example, batch_first=True)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)
    done_batch = torch.FloatTensor(batch.done).to(device)
    next_state_batch = pad_sequence(batch.next_state, batch_first=True)

    # Q(s_t, a) 계산 - 모델이 Q(s_t)를 계산하고, 취한 행동의 열을 선택합니다.
    # 이들은 policy_net에 따라 각 배치 상태에 대해 선택된 행동입니다.
    state_action_values = policy_net(state_batch, pos_example_batch, neg_example_batch).view(-1, n_actions).gather(1,
                                                                                                                   action_batch)

    # 모든 다음 상태를 위한 V(s_{t+1}) 계산
    # non_final_next_states의 행동들에 대한 기대값은 "이전" target_net을 기반으로 계산됩니다.
    # max(1)[0]으로 최고의 보상을 선택하십시오.
    # 이것은 마스크를 기반으로 병합되어 기대 상태 값을 갖거나 상태가 최종인 경우 0을 갖습니다.
    next_state_values = target_net(next_state_batch, pos_example_batch, neg_example_batch).view(-1, n_actions).max(1)[
        0].detach()
    # 기대 Q 값 계산
    expected_state_action_values = (next_state_values * GAMMA) * (1 - done_batch) + reward_batch

    if args.prioritized:
        loss = (state_action_values.squeeze(1) - expected_state_action_values.detach()).pow(2) * torch.FloatTensor(
            weights).to(
            device).detach()
        prios = loss + 1e-5
        loss = loss.mean()
    else:
        # Huber 손실 계산
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1).detach())

    if args.prioritized:
        memory.update_priorities(indices, prios.data.cpu().numpy())

    # 모델 최적화
    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()

    return loss


w = PriorityQueue()

scanned = set()

success = False
done = True

num_episodes = 100000

i = 0

start = time.time()

loss = 0
reward_sum = 0
reward_num = 0
traversed = 0

for i_episode in range(num_episodes):

    example_num = random.randint(1, 26)
    examples = Examples(example_num)
    examples = Examples(2)
    # examples = rand_example()

    w.put((RE().cost, RE()))

    while not w.empty():
        if success or i > 5000:
            success = False
            start = time.time()
            w.queue.clear()
            scanned.clear()
            i = 0
            w.put((RE().cost, RE()))

        if done:
            tmp = w.get()
            state = tmp[1]

        if not state.hasHole():
            continue

        chosen_action = select_action(*make_embeded(state, examples))[0][0].item()

        use_queue = chosen_action % 2 == 0
        new_action = chosen_action // 2

        for j, new_elem in enumerate(
                [Character('0'), Character('1'), Or(), Concatenate(), KleenStar(), Question()]):

            k = copy.deepcopy(state)

            if not k.spread(new_elem):
                continue

            if len(repr(k)) > LENGTH_LIMIT:
                continue

            traversed += 1
            if repr(k) in scanned:
                # print("Already scanned?", repr(k))
                # print(list(scanned))
                continue
            else:
                scanned.add(repr(k))

            if is_pdead(k, examples):
                memory.push(*make_embeded(state, examples), torch.LongTensor([[j]]).to(device),
                            make_embeded(k, examples)[0],
                            torch.FloatTensor([-100]).to(device), True)
                # print(repr(k), "is pdead")
                continue

            if is_ndead(k, examples):
                memory.push(*make_embeded(state, examples), torch.LongTensor([[j]]).to(device),
                            make_embeded(k, examples)[0],
                            torch.FloatTensor([-100]).to(device), True)
                # print(repr(k), "is ndead")
                continue

            if is_redundant(k, examples):
                # print(repr(k), "is redundant")
                continue

            if not k.hasHole():
                if is_solution(repr(k), examples, membership):
                    end = time.time()
                    print("Spent computation time:", end - start)
                    print("Iteration:", i, "\tCost:", k.cost, "\tScanned REs:", len(scanned), "\tQueue Size:",
                          w.qsize(), "\tTraversed:", traversed)
                    # print("Result RE:", repr(k), "Verified by FAdo:", is_solution(repr(k), examples, membership2))
                    print("Result RE:", repr(k))

                    reward = 100
                    reward_sum += reward
                    reward_num += 1
                    memory.push(*make_embeded(state, examples), torch.LongTensor([[j]]).to(device),
                                make_embeded(k, examples)[0],
                                torch.FloatTensor([reward]).to(device), done)

                    success = True
                    done = True
                    break
                else:
                    reward = - 100
                    memory.push(*make_embeded(state, examples), torch.LongTensor([[j]]).to(device),
                                make_embeded(k, examples)[0],
                                torch.FloatTensor([reward]).to(device), True)
            else:
                reward = -10
                memory.push(*make_embeded(state, examples), torch.LongTensor([[j]]).to(device),
                            make_embeded(k, examples)[0],
                            torch.FloatTensor([reward]).to(device), done)

            if j != new_action:
                w.put((k.cost, k))

        if success:
            break
        else:
            next_state, reward, done, success = make_next_state(state, new_action, examples)

            if success:
                print("how...")

            reward_sum += reward
            reward_num += 1

        if use_queue and not done:
            done = True

        if done:
            w.put((next_state.cost, next_state))

        state = next_state

        if args.prioritized:
            loss = optimize_model(beta_by_frame(i))
        else:
            loss = optimize_model()

        if i % 100 == 0:
            print("Episode:", i_episode, "\tEx Num:", example_num, "\tIteration:", i, "\tCost:", k.cost,
                  "\tScanned REs:", len(scanned),
                  "\tQueue Size:", w.qsize(), "\tLoss:", format(loss.item(), '.7f'), "\tAvg Reward:",
                  reward_sum / reward_num)
            reward_sum = 0
            reward_num = 0

        i = i + 1

    if i_episode % TARGET_UPDATE == 0:
        if args.prioritized:
            torch.save(policy_net.state_dict(), 'saved_model/Prioritized_DQN.pth')
        else:
            torch.save(policy_net.state_dict(), 'saved_model/DQN.pth')
        target_net.load_state_dict(policy_net.state_dict())

print('Complete')
