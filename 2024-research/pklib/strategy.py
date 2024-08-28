
import pandas as pd
import numpy as np
import optuna
import os
import sys
import matplotlib.pyplot as plt

# Dynamically add the current module's directory to sys.path
module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, module_dir)

import position_tools


def backtest(log_price, enter_sigs, exit_sigs, skip_first, xmult, transaction_cost=0.001, slippage=0.003, precision=3, period_costs=None):
 
    # Use the position_tools C extension for trade calculation
    
    entry_indices, exit_indices = position_tools.enumerate_trades(enter_sigs.values, exit_sigs.values, skip_first)

    if len(entry_indices) == 0:
        # print('No trades found.')
        return [], [], {}

    # Calculate trade returns using log prices
    trade_rets = pd.Series(
        xmult * (log_price.iloc[exit_indices].values - log_price.iloc[entry_indices].values),
        index=log_price.index[exit_indices]
    )
    trade_rets *= xmult
    trade_rets -= np.log1p(2*transaction_cost + slippage)

    metrics = calculate_metrics(trade_rets)

    return entry_indices, exit_indices, metrics
    # return {
    #     'metrics': metrics,
    #     'itrades': itrades,
    #     # 'strat_pnl_pct': strat_pnl,
    #     # 'entry_points': log_price.index[itrades[:, 0]],
    #     # 'exit_points': log_price.index[itrades[:, 1]],
    #     # 'returns': metrics['returns'],
    #     # 'cum_returns': metrics['cum_returns'],
    # }


# Define helper functions for calculating metrics
def calculate_drawdown(pnl):
    running_max = pnl.cummax()
    drawdown = pnl - running_max
    max_drawdown = drawdown.min()
    return max_drawdown

def calculate_sharpe_ratio(rets):
    return rets.mean() / rets.std() if rets.std() > 0 else 0

def calculate_sortino_ratio(rets):
    downside_rets = rets[rets < 0]
    return rets.mean() / downside_rets.std() if downside_rets.std() > 0 else 0

def calculate_metrics(trade_rets):
    if len(trade_rets) == 0:
        return {metric: 0 for metric in [
            'tot_return', 'avg_return', 'avg_win', 'avg_loss',
            'win_ratio', 'profit_factor', 'n_trades', 'n_wins',
            'n_losses', 'max_drawdown', 'avg_drawdown', 'sharpe_ratio', 'sortino_ratio',
            'max_win', 'max_loss', 'sum_periods_in_wins', 'sum_periods_in_losses',
            'avg_periods_in_wins', 'avg_periods_in_losses', 'total_periods_in_trades',
            'avg_periods_in_trades', 'returns', 'cum_returns'
        ]}

    # rets = trade_rets.reindex(trades[:, 1]).dropna()

    total_return = trade_rets.sum()
    avg_return = trade_rets.mean()

    wins = trade_rets[trade_rets > 0]
    losses = trade_rets[trade_rets <= 0]

    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = losses.mean() if len(losses) > 0 else 0
    max_win = wins.max() if len(wins) > 0 else 0
    max_loss = losses.min() if len(losses) > 0 else 0

    win_ratio = len(wins) / len(trade_rets) if len(trade_rets) > 0 else 0
    profit_factor = wins.sum() / abs(losses.sum()) if abs(losses.sum()) > 0 else np.nan
    n_trades = int(len(trade_rets))
    n_wins = int(len(wins))
    n_losses = int(len(losses))

    # Calculate cumulative returns and drawdowns
    cum_rets = trade_rets.cumsum()
    running_max = cum_rets.cummax()
    drawdowns = cum_rets - running_max
    max_drawdown = drawdowns.min()
    avg_drawdown = drawdowns.mean()

    # Calculate the number of periods for each trade
    # periods_in_trades = trades[:, 1] - trades[:, 0] + 1  # periods in each trade

    # Calculate periods metrics
    # win_indices = wins.index.values
    # loss_indices = losses.index.values

    # Safely handle periods in trades by using valid indices
    # win_period_indices = [i for i, end_idx in enumerate(trades[:, 1]) if end_idx in win_indices]
    # loss_period_indices = [i for i, end_idx in enumerate(trades[:, 1]) if end_idx in loss_indices]

    # sum_periods_in_wins = np.sum(periods_in_trades[win_period_indices]) if len(win_period_indices) > 0 else 0
    # sum_periods_in_losses = np.sum(periods_in_trades[loss_period_indices]) if len(loss_period_indices) > 0 else 0
    # avg_periods_in_wins = np.mean(periods_in_trades[win_period_indices]) if len(win_period_indices) > 0 else 0
    # avg_periods_in_losses = np.mean(periods_in_trades[loss_period_indices]) if len(loss_period_indices) > 0 else 0
    # total_periods_in_trades = np.sum(periods_in_trades)
    # avg_periods_in_trades = np.mean(periods_in_trades)

    sharpe_ratio = calculate_sharpe_ratio(trade_rets)
    sortino_ratio = calculate_sortino_ratio(trade_rets)

    return {
        'tot_return': total_return,
        'avg_return': avg_return,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'win_ratio': win_ratio,
        'profit_factor': profit_factor,
        'n_trades': n_trades,
        'n_wins': n_wins,
        'n_losses': n_losses,
        'max_drawdown': max_drawdown,
        'avg_drawdown': avg_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_win': max_win,
        'max_loss': max_loss,
        # 'sum_periods_in_wins': sum_periods_in_wins,
        # 'sum_periods_in_losses': sum_periods_in_losses,
        # 'avg_periods_in_wins': avg_periods_in_wins,
        # 'avg_periods_in_losses': avg_periods_in_losses,
        # 'total_periods_in_trades': total_periods_in_trades,
        # 'avg_periods_in_trades': avg_periods_in_trades,
        'returns': trade_rets,
        'cum_returns': cum_rets,
    }

def print_metrics_table(metrics, convert_to_pct=False):
    headers = ["Metric", "Value"]
    metrics_list = [
        'tot_return', 'max_drawdown', 'n_trades', 'sharpe_ratio', 'sortino_ratio', 
        'avg_return', 'max_win', 'max_loss', 'avg_win', 'avg_loss',
        'win_ratio', 'profit_factor', 'n_wins',
        'n_losses', 'avg_drawdown',
        # The following metrics are commented out because they aren't currently calculated
        # 'sum_periods_in_wins', 'sum_periods_in_losses', 'avg_periods_in_wins', 'avg_periods_in_losses',
        # 'total_periods_in_trades', 'avg_periods_in_trades'
    ]
    
    # Helper function to convert log returns and drawdowns to percentages
    def convert_log_to_pct(value):
        return (np.exp(value)-1) if convert_to_pct else value

    # Metrics that should be converted to percentage if `convert_to_pct` is True
    conversion_metrics = {
        'tot_return', 'avg_return', 'max_win', 'max_loss', 'avg_win', 'avg_loss', 
        'max_drawdown', 'avg_drawdown'
    }

    # Print headers
    print(f"{headers[0]:<25} | {headers[1]:>15}")
    print("-" * 45)
    
    # Print each row dynamically
    for metric in metrics_list:
        if metric in conversion_metrics:
            value = convert_log_to_pct(metrics.get(metric, 0))
        else:
            value = metrics.get(metric, 0)

        print(f"{metric.replace('_', ' ').title():<25} | {value:>15.4f}")


def suggest_params(trial, param_defs):
    params = {}
    unresolved_params = param_defs.copy()
    
    while unresolved_params:
        resolved_in_this_pass = []
        
        for param_name, param_config in unresolved_params.items():
            # Check for min and max dependencies
            can_resolve = True
            if 'min_depends_on' in param_config:
                dep_param = param_config['min_depends_on']['param']
                if dep_param not in params:
                    can_resolve = False
            if 'max_depends_on' in param_config:
                dep_param = param_config['max_depends_on']['param']
                if dep_param not in params:
                    can_resolve = False
            
            if can_resolve:
                method_name = param_config.get('method', 'suggest_int')
                
                # Ensure the method exists on the trial object
                if not hasattr(trial, method_name):
                    raise ValueError(f"Method '{method_name}' not found in Optuna's trial object.")
                
                method = getattr(trial, method_name)
                
                # Resolve min and max values
                min_value = param_config['min']
                max_value = param_config['max']
                
                if 'min_depends_on' in param_config:
                    min_dep_param = param_config['min_depends_on']['param']
                    min_value = param_config['min_depends_on'].get('adjust_min', lambda v: v)(params[min_dep_param])
                
                if 'max_depends_on' in param_config:
                    max_dep_param = param_config['max_depends_on']['param']
                    max_value = param_config['max_depends_on'].get('adjust_max', lambda v: v)(params[max_dep_param])
                
                # Collect additional arguments if any
                additional_args = {k: v for k, v in param_config.items() if k not in ['method', 'min', 'max', 'min_depends_on', 'max_depends_on']}
                
                # Suggest the parameter value
                params[param_name] = method(param_name, min_value, max_value, **additional_args)
                resolved_in_this_pass.append(param_name)
        
        # Remove resolved parameters from the unresolved list
        for param_name in resolved_in_this_pass:
            unresolved_params.pop(param_name)
        
        # Check if no parameters were resolved in this pass (circular dependency or missing dependency)
        if not resolved_in_this_pass:
            unresolved_keys = list(unresolved_params.keys())
            raise ValueError(f"Circular or unresolved dependencies detected in parameters: {unresolved_keys}")
    
    return params


def get_nested_metric(metrics, path):
    """
    Efficiently fetches the value from a nested dictionary using a dot-separated string path.
    
    Args:
    - metrics (dict): The dictionary to traverse.
    - path (str): The dot-separated string path (e.g., "overall_metrics.sharpe_ratio").
    
    Returns:
    - The value at the end of the path, or None if the path is invalid.
    """
    keys = path.split('.')
    value = metrics
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def generate_indicators(data,params,indicators):
    
    # Calculate indicators using params
    for indicator in indicators:
        indicator['function'](data, params)
        
def optimize(data, param_defs, indicators, signals_generator, btargs, xmult=1, n_trials=100, 
             optimize_metrics=None, directions=None):
    
    # Define default directions for each metric
    default_directions = {
        'sharpe_ratio': 'maximize',
        'sortino_ratio': 'maximize',
        'max_drawdown': 'maximize',
        'tot_return': 'maximize',
        'avg_drawdown': 'minimize',
        'avg_win': 'maximize',
        'avg_loss': 'minimize',
        'win_ratio': 'maximize',
        'profit_factor': 'maximize',
        'n_trades': 'minimize',  # Depending on the context, some may want to minimize this
        'max_win': 'maximize',
        'max_loss': 'minimize',
    }
    
    # Set default metrics if none provided
    if optimize_metrics is None:
        optimize_metrics = ['sharpe_ratio']  # Default metric
    
    # Apply default directions if none are provided
    if directions is None:
        directions = [default_directions.get(metric.split('.')[-1], 'maximize') for metric in optimize_metrics]
    
    # Check for mismatched lengths
    if len(optimize_metrics) != len(directions):
        raise ValueError("The number of optimize metrics must match the number of directions.")
    
    def objective(trial):
        params = suggest_params(trial, param_defs)
        skip_first = max(params['up_lookback']+params['up_lag'], params['dn_lookback']+params['dn_lag'])
        generate_indicators(data,params,indicators)
        enter_sigs, exit_sigs, xmult = signals_generator(data, params)
        entry_indices, exit_indices, metrics = backtest(data.log_price, enter_sigs, exit_sigs, skip_first, xmult, **btargs)
        
        if not metrics:
            return [float('-inf') if d == 'maximize' else float('inf') for d in directions]
        
        results = []
        for metric, direction in zip(optimize_metrics, directions):
            value = None

            # Check if metric is a function
            if callable(metric):
                value = metric(metrics)
            else:
                value = get_nested_metric(metrics, metric)

            # Apply default value if metric not found
            if value is None or np.isnan(value):
                value = float('-inf') if direction == 'maximize' else float('inf')

            results.append(value)
        
        return results

    # Set up the study with the correct directions for multiple objectives
    study = optuna.create_study(directions=directions)
    study.optimize(objective, n_trials=n_trials)
    return study


def comp_backtest(data,params,indicators,generate_indicators,generate_signals):
    generate_indicators(data,params,indicators)
    enter_sigs, exit_sigs, xmult = generate_signals(data,params)
    skip_first = max(params['up_lookback']+params['up_lag'], params['dn_lookback']+params['dn_lag'])    
    if skip_first >= len(data):
        return None,None,None
    entry_indices, exit_indices, metrics = backtest(data.log_price, enter_sigs, exit_sigs, skip_first, xmult, transaction_cost=0.001, slippage=0.003, precision=3, period_costs=None)
    return entry_indices, exit_indices, metrics


def plot_strategy(data,metrics,entry_indices,exit_indices,plot_indicators):
    if len(entry_indices) > 0:
        print_metrics_table(metrics, convert_to_pct=True)
        fig_train = plot_performance(entry_indices, exit_indices, metrics,data)
        # if not fig_train is None:
        plot_indicators(fig_train.get_axes()[0], data)
        plt.show()
    else:
        print('No Trades.')
        
        
def plot_performance(entry_indices, exit_indices, metrics, data):
    
    
    # itrades = backtest_result['itrades']

    if len(entry_indices) == 0:
        print("No trades found.")
        return None
        
    cum_returns = metrics['cum_returns']

    # Align the cumulative returns with the trade exit indices
    pnl_pct = pd.Series(np.exp(cum_returns)).subtract(0).set_axis(data.index[exit_indices])

    # if len(long_trade_indices) > 0:
    #     long_pnl_pct = pd.Series(np.exp(long_cum_returns)).subtract(1).set_axis(data.index[long_trade_indices])
    # else:
    #     long_pnl_pct = pd.Series([0] * len(data)).subtract(1).set_axis(data.index)

    # if len(short_trade_indices) > 0:
    #     short_pnl_pct = pd.Series(np.exp(short_cum_returns)).subtract(1).set_axis(data.index[short_trade_indices])
    # else:
    #     short_pnl_pct = pd.Series([0] * len(data)).subtract(1).set_axis(data.index)

    # Plot the results with the best parameters

    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), sharex=True, height_ratios=[2,1])

    # Plot PnL as percentage for long, short, and combined
    ax2.axhline(0, color='black', lw=1)  # Baseline for percentage returns
    ax2.plot(pnl_pct.index, pnl_pct, label='Combined PNL %', color='teal', alpha=0.8, lw=2)
    if len(pnl_pct) > 0:
        ax2.plot(pnl_pct.index, pnl_pct, label='PNL %', color='green', alpha=0.8, lw=2)
    # if len(short_trade_indices) > 0:
    #     ax2.plot(short_pnl_pct.index, short_pnl_pct, label='Short PNL %', color='red', alpha=0.8, lw=2)
    
    ax2.set_yscale('log', base=2)
    ax2.legend(loc='best')

    # Plot entry and exit points
    for x in data.index[entry_indices]: 
        ax1.axvline(x, color='blue', lw=1, alpha=0.2)
        ax2.axvline(x, color='blue', lw=1, alpha=0.2)
    for xx in data.index[exit_indices]:
        ax1.axvline(xx, color='green', lw=1, alpha=0.2)
        ax2.axvline(xx, color='green', lw=1, alpha=0.2)
    for i in range(len(entry_indices)):
        # color = ['red', 'green'][list((metrics['returns'].values < 0).astype(int))]
        # color = [['green','red'][i] for i in (metrics['returns'] < 0.0).values.astype(int)]
        color = 'gray'
        ax1.axvspan(xmin=data.index[entry_indices[i]], xmax=data.index[exit_indices[i]], color=color, alpha=0.1)
        ax2.axvspan(xmin=data.index[entry_indices[i]], xmax=data.index[exit_indices[i]], color=color, alpha=0.1)
    
    ax2.grid(axis='y')
    # plt.show()
    return fig
