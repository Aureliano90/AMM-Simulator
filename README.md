# AMM-Simulator

## Introduction

An asynchronous object-oriented program to simulate constant product AMM LP position on OKEx. An LP position that
satisfies `x*y=k` is equivalent to an infinite grid trading bot. It sells spot when the price rises and buys spot when
the price drops, passively by the help of traders and arbitrageurs. LP on a DEX earns trading fees and liquidity mining
rewards. The trading fees are subject to the fee rate, the volume on the trading pair and the share of pool. On the
other hand, a copy of LP on CEX doesn't earn trading fees. It costs trading fees to mimic the LP on CEX. However, it
generates profit by selling high and buying low. The APR is purely the result of price action and can be used to
deduce the realized volatility.

Chinese and English support, completed with annotations and docstrings.

## Features

* Simulate an AMM LP position on CEX;
* Calculate the APR and realized volatility.

## Installation

Install Python 3.8+ and required packages.

`python setup.py install`
or
`pip install -r requirements.txt`

Install [MongoDB](https://www.mongodb.com/try/download/community).

Paste API keys in `config.py` (use account 3 for demo trading).

Set `language='cn'` for Chinese and `language='en'` for English in `config.py`.

Simply `python main.py`.

## Disclaimer

The author does not assume responsibilities for the use of this program, nor is warranty granted.
