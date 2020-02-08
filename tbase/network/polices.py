# -*- coding:utf-8 -*-

import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable

from tbase.common.random_process import OrnsteinUhlenbeckProcess
from tbase.common.torch_utils import fc, lstm
from tbase.network.base import BasePolicy


class LSTM_MLP(BasePolicy):
    def __init__(self, seq_len=11, input_size=10, hidden_size=300,
                 output_size=4, num_layers=1, dropout=0.0, learning_rate=0.01,
                 fc_size=200, activation=None, ou_theta=0.15,
                 ou_sigma=0.2, ou_mu=0):
        super(LSTM_MLP, self).__init__()
        self.seq_len = seq_len
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.num_layers = num_layers
        self.dropout = dropout
        # learning rate
        self.learning_rate = learning_rate
        # 定义和初始化网络
        self.rnn = lstm(input_size, hidden_size, num_layers, dropout)
        self.fc1 = fc(hidden_size, fc_size)
        self.fc2 = fc(fc_size, output_size)
        if activation is None:
            self.activation = nn.LeakyReLU(0.01)
        else:
            self.activation = activation
        self.random_process = OrnsteinUhlenbeckProcess(
            size=output_size, theta=ou_theta, mu=ou_mu, sigma=ou_sigma)

    def init_hidden(self, batch_size):
        h_0 = Variable(torch.randn(self.num_layers, batch_size,
                       self.hidden_size)).to(self.device, torch.float)
        c_0 = Variable(torch.randn(self.num_layers, batch_size,
                       self.hidden_size)).to(self.device, torch.float)
        return h_0, c_0

    def action(self, obs, with_reg=False):
        # obs: seq_len, batch_size, input_size
        h_0, c_0 = self.init_hidden(obs.shape[1])
        output, _ = self.rnn(obs, (h_0, c_0))
        output = self.activation(output)
        encoded = self.activation(self.fc1(output[-1, :, :]))
        action = self.activation(self.fc2(encoded))
        if with_reg:
            return action, encoded
        return action

    def select_action(self, obs):
        # obs: seq_len, batch_size, input_size
        action = self.action(obs, with_reg=False)
        action = action.detach().cpu()[0].numpy()
        # TODO: 确定随机过程写法是否正确
        action += self.random_process.sample()
        action = np.clip(action, self.action_low, self.action_high)
        return action