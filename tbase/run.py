# -*- coding:utf-8 -*-
"""
1. 提供多进程并环境
2. 根据输入选择：算法，Policy-Net, Value-Net, 优化算法. 然后生成Agent
3. 训练保存模型performance, 参数
"""
from importlib import import_module

import torch

from tbase.agents.td3.agent import Agent
from tbase.common.cmd_util import common_arg_parser, make_env, set_global_seeds
from tbase.common.logger import logger


def opt_fn(params, lr):
    return torch.optim.RMSprop(params, lr)


def get_alg_module(alg, submodule="agent"):
    submodule = submodule or alg
    try:
        # try to import the alg module from tbase
        alg_module = import_module('.'.join(['tbase.agents', alg, submodule]))
    except ImportError:
        module = '.'.join(['tbase.agents', alg, submodule])
        raise Exception("tbase.run get_alg_module error:%s" % module)

    return alg_module


def get_agent(env, args):
    agent_module = get_alg_module(args.alg, submodule="agent")
    return agent_module.Agent(env, args)


def main():
    args = common_arg_parser()
    if args.debug:
        import logging
        logger.setLevel(logging.DEBUG)
    set_global_seeds(args.seed)
    logger.info("tbase.run set global_seeds: %s" % str(args.seed))
    env = make_env(args=args)
    print("\n" + "*" * 80)
    logger.info("Initializing agent by parameters:")
    logger.info(str(args))
    agent = get_agent(env, args)
    logger.info("Training agent")
    agent.learn()
    logger.info("Train finished, see details by run tensorboard --logdir=%s" %
                args.tensorboard_dir)


if __name__ == '__main__':
    main()
