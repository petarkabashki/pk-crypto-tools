#%%
# https://signals.boulderinvestment.tech/#map
# https://pypi.org/project/lppls/

from lppls import lppls
import numpy as np
import pandas as pd
from datetime import datetime as dt
from matplotlib import pyplot as plt
from tqdm import tqdm
from time import sleep

#%%

# PAIR = 'ALGO_USDT'
# TIMEFRAME = '1w'
# EXCHANGE = 'binance'

#%%

def process_lppls(PAIR, TIMEFRAME, EXCHANGE):
        
    odf = pd.read_json(f'/media/mu6mula/Data/Crypto-Data-Feed/freq-user-data/data/{EXCHANGE}/{PAIR}-{TIMEFRAME}.json'
    ).dropna().set_axis(['timestamp', 'open', 'high', 'low', 'close', 'volume'], axis=1
    # ).assign(dtime=lambda x: pd.to_datetime(x['timestamp'], unit='ms', utc=False)
    # ).drop('timestamp'
    )#.set_index('dtime').sort_index()

    """
    Fit Model
    Fit your data to the LPPL model
    """

    dtime = pd.to_datetime(odf['timestamp'], unit='ms', utc=False)
    time = [pd.Timestamp.toordinal(d) for d in dtime]
    price = np.log(odf['close'].values)
    observations = np.array([time, price])
    MAX_SEARCHES = 25
    lppls_model = lppls.LPPLS(observations=observations)
    tc, m, w, a, b, c, c1, c2, O, D = lppls_model.fit(MAX_SEARCHES)

    """
    Compute Confidence Indicator
    Run computations for lppl and compute the confidence indicator
    """

    res = lppls_model.mp_compute_nested_fits(
    workers=8,
    window_size=120, 
    smallest_window_size=30, 
    outer_increment=1, 
    inner_increment=5, 
    max_searches=25
    )

    """
    Save Confidence Indicator
    Run computations for lppl
    """

    res_df = lppls_model.compute_indicators(res)
    # res_df[['time', 'price', 'pos_conf', 'neg_conf']].to_csv(f"./res_df/{PAIR}-{TIMEFRAME}.png")
    res_df.to_csv(f"./res_df/{PAIR}-{TIMEFRAME}.csv")

    """
    Save Fit
    Save and show your fitted results
    """

    time_ord = [pd.Timestamp.fromordinal(d) for d in lppls_model.observations[0, :].astype('int32')]

    t_obs = lppls_model.observations[0, :]
    lppls_fit = [lppls_model.lppls(t, tc, m, w, a, b, c1, c2) for t in t_obs]
    price = lppls_model.observations[1, :]

    first = t_obs[0]
    last = t_obs[-1]

    ord = res_df['time'].astype('int32')
    ts = [pd.Timestamp.fromordinal(d) for d in ord]

    fig, (ax1) = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(14, 8))

    ax1.plot(time_ord, price, label='price', color='black', linewidth=0.75)
    ax1.plot(time_ord, lppls_fit, label='lppls fit', color='blue', alpha=0.5)
    ax1.grid(which='major', axis='both', linestyle='--')
    ax1.set_ylabel('ln(p)')
    ax1.legend(loc=2)

    plt.xticks(rotation=45)
    plt.savefig(f"./images/fitting/{PAIR}-{TIMEFRAME}.png")
    plt.clf()

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(18, 10))

    # plot pos bubbles
    ax1_0 = ax1.twinx()
    ax1.plot(ts, res_df['price'], color='black', linewidth=0.75)
    ax1_0.plot(ts, res_df['pos_conf'], label='bubble indicator (pos)', color='red', alpha=0.5)

    # plot neg bubbles
    ax2_0 = ax2.twinx()
    ax2.plot(ts, res_df['price'], color='black', linewidth=0.75)
    ax2_0.plot(ts, res_df['neg_conf'], label='bubble indicator (neg)', color='green', alpha=0.5)

    # set grids
    ax1.grid(which='major', axis='both', linestyle='--')
    ax2.grid(which='major', axis='both', linestyle='--')

    # set labels
    ax1.set_ylabel('ln(p)')
    ax2.set_ylabel('ln(p)')

    ax1_0.set_ylabel('bubble indicator (pos)')
    ax2_0.set_ylabel('bubble indicator (neg)')

    ax1_0.legend(loc=2)
    ax2_0.legend(loc=2)

    plt.xticks(rotation=45)
    plt.savefig(f"./images/confidence/{PAIR}-{TIMEFRAME}.png")
    plt.clf()

#%%

binance1d = ["1000SATS","1INCH","AAVE","ACA","ACE","ACH","ACM","ADA","ADX","AERGO","AEUR","AEVO","AGIX","AGLD","AI","AKRO","ALCX","ALGO","ALICE","ALPACA","ALPHA","ALPINE","ALT","AMB","AMP","ANKR","APE","API3","APT","ARB","ARDR","ARKM","ARK","ARPA","AR","ASR","ASTR","AST","ATA","ATM","ATOM","AUCTION","AUDIO","AVA","AVAX","AXL","AXS","BADGER","BAKE","BAL","BAND","BAR","BAT","BB","BCH","BEAMX","BEL","BETA","BICO","BIFI","BLUR","BLZ","BNB","BNT","BNX","BOME","BOND","BONK","BSW","BTC","BTTC","BURGER","C98","CAKE","CELO","CELR","CFX","CHESS","CHR","CHZ","CITY","CKB","CLV","COMBO","COMP","COS","COTI","CREAM","CRV","CTK","CTSI","CTXC","CVC","CVP","CVX","CYBER","DAR","DASH","DATA","DCR","DEGO","DENT","DEXE","DF","DGB","DIA","DOCK","DODO","DOGE","DOT","DUSK","DYDX","DYM","EDU","EGLD","ELF","ENA","ENJ","ENS","EOS","EPX","ERN","ETC","ETHFI","ETH","EUR","FARM","FDUSD","FET","FIDA","FIL","FIO","FIRO","FIS","FLM","FLOKI","FLOW","FLUX","FORTH","FOR","FRONT","FTM","FTT","FUN","FXS","GALA","GAL","GAS","GFT","GHST","GLMR","GLM","GMT","GMX","GNO","GNS","GRT","GTC","HARD","HBAR","HFT","HIFI","HIGH","HIVE","HOOK","HOT","ICP","ICX","IDEX","ID","ILV","IMX","INJ","IOST","IOTA","IOTX","IQ","IRIS","JASMY","JOE","JST","JTO","JUP","JUV","KAVA","KDA","KEY","KLAY","KMD","KNC","KP3R","KSM","LAZIO","LDO","LEVER","LINA","LINK","LIT","LOKA","LOOM","LPT","LQTY","LRC","LSK","LTC","LTO","LUNA","LUNC","MAGIC","MANA","MANTA","MASK","MATIC","MAV","MBL","MBOX","MDT","MDX","MEME","METIS","MINA","MKR","MLN","MOVR","MTL","NEAR","NEO","NEXO","NFP","NKN","NMR","NOT","NTRN","NULS","OAX","OCEAN","OGN","OG","OMG","OMNI","OM","ONE","ONG","ONT","OOKI","OP","ORDI","ORN","OSMO","OXT","PAXG","PDA","PENDLE","PEOPLE","PEPE","PERP","PHA","PHB","PIVX","PIXEL","POLS","POLYX","POND","PORTAL","PORTO","POWR","PROM","PROS","PSG","PUNDIX","PYR","PYTH","QI","QKC","QNT","QTUM","QUICK","RAD","RARE","RAY","RDNT","REEF","REI","REN","REQ","REZ","RIF","RLC","RNDR","RONIN","ROSE","RPL","RSR","RUNE","RVN","SAGA","SAND","SANTOS","SCRT","SC","SEI","SFP","SHIB","SKL","SLP","SNT","SNX","SOL","SPELL","SSV","STEEM","STG","STMX","STORJ","STPT","STRAX","STRK","STX","SUI","SUN","SUPER","SUSHI","SXP","SYN","SYS","TAO","TFUEL","THETA","TIA","TKO","TLM","TNSR","TRB","TROY","TRU","TRX","T","TUSD","TWT","UFT","UMA","UNFI","UNI","USDC","USDP","USTC","UTK","VANRY","VET","VGX","VIB","VIC","VIDT","VITE","VOXEL","VTHO","WAN","WAVES","WAXP","WBETH","WBTC","WIF","WING","WIN","WLD","WNXM","WOO","WRX","W","XAI","XEC","XEM","XLM","XNO","XRP","XTZ","XVG","XVS","YFI","YGG","ZEC","ZEN","ZIL","ZRX"]

# %%

TIMEFRAMES = ['1w', '8h', '4h']
EXCHANGE = 'binance'
for ASSET in tqdm(binance1d):
    for TIMEFRAME in TIMEFRAMES:
        PAIR = f'{ASSET}_USDT'
        print(PAIR)
        process_lppls(PAIR, TIMEFRAME, EXCHANGE)
    
# %%

TIMEFRAMES = ['1w', '8h', '4h']
EXCHANGE = 'binance'
for ASSET in tqdm(binance1d):
    for TIMEFRAME in TIMEFRAMES:
        PAIR = f'{ASSET}_USDT'
        print(PAIR)
        process_lppls(PAIR, TIMEFRAME, EXCHANGE)
# %%
