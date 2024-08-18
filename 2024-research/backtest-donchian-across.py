#%%

import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_ta as ta
import math
from tqdm import tqdm
import gc
import time
import json
import itertools
import optuna
import os
import sys
optuna.logging.set_verbosity(optuna.logging.ERROR)
import argparse

from position_tools import calculate_trades, calculate_positions

#%%

# def main():
    # Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Backtester across assets and resamples.")

parser.add_argument('--resamples', type=int, nargs='+', default=[1,2,4,6,8,12,16,24], help='List of resample periods')
parser.add_argument('--timeframe', type=str, default='1h', help='timeframe data to load')
parser.add_argument('--max_lag', type=int, default='150', help='max_lag')
parser.add_argument('--max_lookback', type=int, default=150, help='max_lookback')
parser.add_argument('--n_trials', type=int, default=200, help='n_trials')
parser.add_argument('--train_ratio', type=float, default=0.5, help='train_ratio')
parser.add_argument('--quote', type=str, default='USDT', help='quote asset')
parser.add_argument('--take_first', type=int, default=-1, help='take first n asset')

args = parser.parse_args()

max_lag=args.max_lag
max_lookback=args.max_lookback
n_trials=args.n_trials
train_ratio = args.train_ratio
resamples = args.resamples
timeframe = args.timeframe
quote = args.quote
take_first = args.take_first

# if __name__ == "__main__":
#     main()
fspec = f'DONCH--q_{quote}--tf_{timeframe}--rsmpl_{"_".join(str(r) for r in resamples)}--ntra_{n_trials}--trra_{train_ratio}--mxlag_{max_lag}--mxlkb_{max_lookback}--fst_{take_first}'
cnt_filename = f'strat_results/{fspec}.cnt'
dump_filename = f'strat_results/{fspec}.txt'
# print(dump_filename)
# sys.exit()
if not os.path.exists('./strat_results'): os.mkdir('./strat_results')


cnt = 0
if not os.path.exists(cnt_filename) : 
    with open(cnt_filename, "w") as file: 
        file.write(str(0))
        file.flush()
        file.close()
with open(cnt_filename, 'r') as file:
    cnt = int(file.read())
print(f'Starting from: {cnt}')
# sys.exit()
#%%

def load_json_candles(fname):
    data = pd.read_json(fname)
    data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data

def load_candles(exchange,base,quote,timeframe):
    fname = f'/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/{exchange}/{base}_{quote}-{timeframe}.json'
    return load_json_candles(fname)

def load_futures_candles(exchange,base,quote,timeframe):
    fname = f'/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/{exchange}/futures/{base}_{quote}_{quote}-{timeframe}-futures.json'
    return load_json_candles(fname)

def load_sp500_stock_candles(ticker):
    fname = f'/media/mu6mula/Data/Crypto-Data-Feed/sp500_data/{ticker}.csv'
    data = pd.read_csv(fname)
    data['Date'] = pd.to_datetime(data.Date)
    data.columns = [c.lower() for c in data.columns]
    data.set_index('date', inplace=True)
    return data

def load_russel2000_candles(ticker):
    fname = f'/media/mu6mula/Data/Crypto-Data-Feed/russell_2000_data/{ticker}.csv'
    data = pd.read_csv(fname)
    data['Date'] = pd.to_datetime(data.Date)
    data.columns = [c.lower() for c in data.columns]
    data.set_index('date', inplace=True)
    return data

#%%


# Define transaction costs and slippage
transaction_cost = 0.001  # 0.1% transaction cost per trade
slippage = 0.003  # 0.1% slippage per trade

itrades = None
    
def backtest(data, params, nhours, short_long=None, xmult=1):
    if short_long is None: short_long = [1,-1]
    
    global itrades
    
    up_lookback = params['up_lookback']
    dn_lookback = params['dn_lookback']
    up_lag = params['up_lag']
    dn_lag = params['dn_lag']
    band_offset = params['band_offset']
    lclose = data['close'].apply(np.log)
    lrets = lclose.diff()

    data['donch_up'] = data['close'].rolling(window=up_lookback).max().shift(up_lag)
    data['donch_dn'] = data['close'].rolling(window=dn_lookback).min().shift(dn_lag)
    # data['donch_mid'] = (data['donch_up'] + data['donch_dn']) / 2
    data['donch_mid'] = (1 - band_offset)*data['donch_up'] + band_offset*data['donch_dn']
    # data['donch_mid_up'] = (1 - band_offset)*data['donch_up'] + band_offset*data['donch_dn']
    # data['donch_mid_dn'] = (1 - band_offset)*data['donch_dn'] + band_offset*data['donch_up']
    
    ind_undefs = data['donch_up'].isna() | data['donch_dn'].isna()
    
    bull = ( 
                    (~ind_undefs) &\
                    (data['close'] > data['donch_up']) #& \
                    # (data['donch_up'] > data['donch_dn'])
    ).astype(int)

    bull_end = ( 
                    (~ind_undefs) &\
                    (data['close'] < data['donch_mid']) #| \
                    # (data['donch_up'] < data['donch_dn'])
    ).astype(int)


    bear = ( 
                    (~ind_undefs) &\
                    (data['close'] < data['donch_dn']) #& \
                    # (data['donch_up'] < data['donch_dn'])
    ).astype(int)
    bear_end = ( 
                    (~ind_undefs) &\
                    (data['close'] > data['donch_mid']) #| \
                    # (data['donch_up'] > data['donch_dn'])
    ).astype(int)

    itrades = calculate_trades(int(1 in short_long)*bull.values, int(1 in short_long)*bull_end.values, int(-1 in short_long)*bear.values, int(-1 in short_long)*bear_end.values)
    # ipositions = calculate_positions(itrades,len(lclose))

    entry_points = data.index[itrades[:,0]]
    exit_points = data.index[itrades[:,1]]
    trade_rets = pd.Series(np.append([0],itrades[:,2]*(lclose.values[itrades[:,1]] - lclose.values[itrades[:,0]])), index=data.index[np.append([0],itrades[:,1])])
    trade_rets *= xmult
    trade_rets -= np.log1p(transaction_cost + slippage)
    trade_pnl = trade_rets.cumsum()
    
    n_trades = len(itrades)
    tot_return = trade_pnl.iloc[-1]
    asset_return = lclose[-1] - lclose[0]
    wins = trade_rets[trade_rets > 0];  
    losses = trade_rets[trade_rets < 0]
    nwins, nlosses = len(wins), len(losses)
    win_ratio = nwins/ (n_trades) if n_trades > 0 else np.nan
    profit_factor = wins.sum() / losses.abs().sum()
    avg_win = wins.mean() if len(wins) > 0 else np.nan
    avg_loss = losses.mean() if len(losses) > 0 else np.nan
    
    trade_running_max = trade_pnl.cummax()
    trade_drawdowns = (trade_pnl - trade_running_max)
    trade_max_drawdown = np.min(trade_drawdowns)
    
    return {'tot_return':tot_return, 'asset_return': asset_return,
            'n_trades': n_trades, 'nwins':nwins, 'nlosses': nlosses, 'win_ratio': win_ratio, 'profit_factor': profit_factor, 
            'entry_points': entry_points, 'exit_points': exit_points, 
            'trade_rets': trade_rets, 'trade_pnl': trade_pnl, 
            'itrades': itrades,
            'avg_win': avg_win, 'avg_loss': avg_loss,
            'trade_max_drawdown': trade_max_drawdown, 'trade_drawdowns': trade_drawdowns,
    }

 

def optimize(data, nhours, backtest_fn = backtest, short_long=None, xmult=1,max_lag=200, max_lookback=100,n_trials=100):
    def objective(trial):
        global data
        up_lookback = trial.suggest_int('up_lookback', 7, max_lookback)
        dn_lookback = trial.suggest_int('dn_lookback', 7, max_lookback)
        up_lag = trial.suggest_int('up_lag', 7, max_lag)
        dn_lag = trial.suggest_int('dn_lag', 7, max_lag)
        band_offset = trial.suggest_float('band_offset', 0, 1)
        params = {
            'up_lookback': up_lookback,
            'dn_lookback': dn_lookback,
            'up_lag': up_lag,
            'dn_lag': dn_lag,
            'band_offset': band_offset
        }
        res = backtest_fn(data,params,nhours,short_long, xmult=xmult)
        return res['tot_return'].mean(), res['trade_drawdowns'].mean()#/ math.cos(number_of_trades)

    # Run the optimization
    study = optuna.create_study(directions=['maximize','maximize'])
    study.optimize(objective, n_trials=n_trials)

    # Get the best parameters
    return study
    
optuna.logging.set_verbosity(optuna.logging.ERROR)

#%%


base_data_dir = "/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data"
# train_ratio = 0.3
short_long = [-1,1]
exchanges = ['binance', 'kucoin', 'bybit', 'bitget']
assets = ['BTC','ETH','XRP','LINK','XTZ','LTC','ADA','TRX','ONT','BCH','NEO','EOS','COMP','YFI','ALGO','DOT','UNI','AAVE','DOGE','BAT','CHZ','MANA','ENJ','SUSHI','SNX','GRT','MKR','ZEC','FIL','KSM','QTUM','XLM','ATOM','LUNAOLD','SOL','AXS','MATIC','SHIB','FTM','DYDX','VPAD','SAND','ALICE','ENS','ANKR','GTC','OCEAN','MASK','USDC','YGG','AGLD','SLP','T','SPELL','TEL','RSR','AMP','POLY','ZRX','TRIBE','LRC','FEI','TUSD','USDP','DAI','C98','1INCH','KNC','DAO','BNT','CRV','UMA','PERP','CAKE','CVX','FXS','GNO','BNB','PAXG','WBTC','DENT','HOT','XYO','MXC','COTI','FET','REN','CTSI','CHR','STORJ','BICO','IMX','RNDR','OMG','LPT','QNT','APE','SOS','MFT','OOKI','VRA','JASMY','CELR','FOR','PEOPLE','ARPA','ORBS','DF','UMEE','TLM','IDEX','RLY','TRU','GALA','OXT','DUSK','BETA','FRONT','SUPER','PSTAKE','DAR','SFP','CVP','PLA','UST','AUDIO','COCOS','VOXEL','POLS','MIR','LOOKS','GHST','LOKA','MBOX','ANC','PORTO','LAZIO','API3','INJ','SANTOS','ALPINE','PYR','METIS','ILV','JOE','ETC','AVAX','DASH','RACA','CRTS','KEY','REEF','STMX','POND','ACH','GTO','SNT','OM','REAP','STPT','TVK','SPA','EPS','NKN','MELOS','RSS3','POLC','CVC','ALPHA','ELF','CLV','ATA','ALPACA','RARE','BSW','DREP','BAKE','TKO','CHESS','PUNDIX','BEL','TWT','GODS','LIT','MTL','QRDO','STG','CTX','ORN','BAND','RAD','ANT','UNFI','ERN','HIGH','BOND','XVS','BAL','AUCTION','TORN','BNXOLD','FARM','QUICKOLD','SHILL','GARI','FIDA','GMT','INS','GMM','RANKER','1EARTH','PERL','QI','RAMP','DNT','ONSTON','LMR','VR','KONO','CRPT','CEEK','UPO','SXP','BBF','STRONG','WAVES','NEAR','KLAY','ASTR','BEND','BLOK','NEST','MDT','TRVL','PHA','TOMO','NYM','GAL','USN','EPX','GST','OGN','BIT','USDD','BUSD','LUNA','LUNC','REVO','OP','CRO','STETH','VGX','NEXO','CEL','LDO','MULTI','SWP','WWY','BRZ','LEVER','TKB','1000VOLT','ETHW','ETHS','CMP','1000BRISE','DC','GMTT','SU','1000VINU','FLUX','JOT','HT','JST','XEN','UTK','NCT','ETHA','POLYX','1000000PIT','FND','APT','RED','THE','PSG','CITY','JUV','ATM','ASR','BAR','GMX','PLCU','GLEEC','HFT','PRMX','WCI','CCX','VRGW','ARG','ING','BPTC','HOOK','ZENI','THETA','RUNE','CELO','AR','LOOT','SKL','LINA','ICP','IOTX','1000BONK','MAGIC','AGIX','KMON','BLUR','SSV','RPL','ACS','PHB','STX','1000FLOKI','CFX','BNX','LQTY','RDNT','DPX','GRAIL','GNS','SYN','HBAR','CKB','RLC','ID','ARB','TOMI','FLR','EDU','SUI','PT','PEPE','TURBO','10000LADYS','ORDI','COMBO','PENDLE','ARKM','QUICK','WLD','FORTH','CYBER','SEI','BLZ','TRB','HIFI','NMR','NTRN','BIGTIME','TIA','MEME','TOKEN','BADGER','KAS','PYTH','JTO','PMG','1000EBPTC','1000SATS','ACE','RATS','ALCX','DEGO','NFP','MOVR','AI','XAI','WIF','MANTA','ONDO','1000TROLL','RAY','ALT','TON','JUP','DEFI','ZETA','RON','DYM','DIA','PIXEL','MAVIA','STRK','GLM','PORTAL','SLN','AXL','TAO','WIN','MYRO','AEVO','IQ','VIB','AST','DEXE','DUEL','ETHFI','VANRY','PENG','BOME','FUN','VIDT','SLERF','NULS','ZKJ','LTO','NGL','WEN','MLN','BODEN','ENA','AERO','FIS','BEAMX','ORCA','MFER','DEGEN','POPCAT','W','CORE','WER','MEW','COS','SAGA','ZEUS','TNSR','MASA','SHDW','ANDY','BRETT','FOXY','PRIME','CREAM','AERGO','KP3R','XDC','OMNI','PRCL','RST','MERL','REZ','MANEKI','SAFE','KMNO','ZERO','FRIEND','BB','NOT','GME','DRIFT','TFUEL','MON','MAGA','TAIKO','ULTI','IO','ATH','LISTA','COOKIE','PIRATE','ZK','ZRO','BLAST','G','BANANA','UXLINK','RENDER','QKC','AVAIL',]

# assets.index('XYO')
# len(assets)
# %%
# tf_assets = itertools.product(assets,resamples)
exch_map = []
# for (asset, timeframe) in tf_assets:
for asset in assets:
    found = None
    for exchange in exchanges:
        if os.path.exists(f'{base_data_dir}/{exchange}/{asset}_{quote}-1h.json'):
            found = exchange
            break
    exch_map.append(found)
# exch_map
# len(assets), len(exch_map)
#%%
def xtract_bt(opt_bt) : 
    return {k:v for (k,v) in opt_bt.items() if not (isinstance(v,pd.Series) or isinstance(v,pd.Index)  or isinstance(v,np.ndarray))}

### Load dumped
lines = []
if os.path.exists(dump_filename):
    with open(dump_filename, 'r') as file:
        # Read all lines into a list
        lines = file.readlines()
btso = [json.loads(l) for l in lines[:-1]]
exist_map = {}
for o in btso[:take_first]:
    if not o['asset'] in exist_map: exist_map[o['asset']] = {}
    exist_map[o['asset']][o['timeframe']] = True


with open(dump_filename, 'a') as file:
    for i,asset in (enumerate(assets)):
        if 'USD' in asset:
            print(f'.. skipping {asset}')
            continue
        if i < cnt : 
            print(f'... skipping asset {i} <= {cnt} - {asset}')
            continue
        if exch_map[i] is None:
            print(f'Missing asset: {i} - {asset}')
            continue
        print(f'processing asset: {i} - {asset} -- {exch_map[i]}')
        if asset in exist_map:
            exist_tfs = sorted(exist_map[asset].keys())
        # data = None
        data = load_candles(exch_map[i],asset,quote,timeframe)
        for nhours in resamples:
            if asset in exist_map:
                if nhours < exist_tfs[-1]:
                    print(f'...Skip Timeframe {nhours}, asset {i} - {asset}')
                    continue
            # if data is None: 
            
            print(f'---processing timeframe {nhours} / asset: {i} - {asset}')
            tfdata = data.resample(f'{nhours}H').agg({'open': 'first','high': 'max','low': 'min','close': 'last','volume': 'sum'})
            data_train = tfdata.iloc[:int(tfdata.shape[0]*train_ratio)]; 
            data_test = tfdata.iloc[data_train.shape[0]:]
            study = optimize(data_train, nhours,backtest_fn=backtest, short_long=short_long,xmult=1,max_lag=max_lag,max_lookback=max_lookback,n_trials=args.n_trials)
            aparams = [t.params for t in reversed(study.best_trials[-10:])]
            for params in aparams:
                res_train = backtest(data_train,params,nhours,short_long, xmult=1)
                res_test = backtest(data_test,params,nhours,short_long, xmult=1)
                print(json.dumps({'asset': asset, 'timeframe': nhours, 'params': params, 'res_train': xtract_bt(res_train), 'res_test': xtract_bt(res_test)}), file=file, flush=True)
                
                print(f"                     train=({np.expm1(res_train['tot_return']):.2f} , {np.expm1(res_train['trade_max_drawdown']):.2f})  test=({np.expm1(res_test['tot_return']):.2f} , {np.expm1(res_test['trade_max_drawdown']):.2f})  #/wr=({res_test['n_trades']}, {res_test['win_ratio']:0.2f})")
                
                time.sleep(1)
        with open(cnt_filename, 'w') as cfile:
            print(i,file=cfile)
        
        print(f'Done asset {i} - {asset}')
        gc.collect()
            
#%%

# fname = "bbtest.cnt"

#%%
#%%