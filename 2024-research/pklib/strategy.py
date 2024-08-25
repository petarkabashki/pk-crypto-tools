
import pandas as pd
import numpy as np
import position_tools  # Import the C extension module
import optuna


def backtest(data, params, indicators, signals, enable_long=True, enable_short=True, xmult=1, transaction_cost=0.001, slippage=0.003, precision=3, period_costs=None):
    lclose = data['close'].apply(np.log)

    # Calculate indicators using params
    for indicator in indicators:
        indicator['function'](data, params)

    # Generate signals using params
    signal_arrays = {name: signal['function'](data, params) for name, signal in signals.items()}

    # Initialize empty signals if long/short is disabled
    if not enable_long:
        signal_arrays['bull'] = np.zeros(len(data))
        signal_arrays['bull_end'] = np.zeros(len(data))
    
    if not enable_short:
        signal_arrays['bear'] = np.zeros(len(data))
        signal_arrays['bear_end'] = np.zeros(len(data))

    # Use the position_tools C extension for trade calculation
    itrades = position_tools.calculate_trades(
        signal_arrays['bull'].values if enable_long else np.zeros(data.shape[0]),
        signal_arrays['bull_end'].values if enable_long else np.zeros(data.shape[0]),
        signal_arrays['bear'].values if enable_short else np.zeros(data.shape[0]),
        signal_arrays['bear_end'].values if enable_short else np.zeros(data.shape[0])
    )

    if len(itrades) == 0 or not itrades.any():
        print('No trades found.')
        return {}

    # Calculate trade returns using log prices
    trade_rets = pd.Series(
        itrades[:, 2] * (lclose.iloc[itrades[:, 1]].values - lclose.iloc[itrades[:, 0]].values),
        index=itrades[:, 1]
    )
    trade_rets *= xmult
    trade_rets -= np.log1p(transaction_cost + slippage)

    # Apply period costs if provided
    if period_costs is not None:
        if isinstance(period_costs, (int, float)):
            trade_rets -= period_costs * (itrades[:, 1] - itrades[:, 0] + 1)
        elif isinstance(period_costs, (np.ndarray, pd.Series)):
            cost_array = pd.Series(period_costs, index=data.index)
            trade_rets -= cost_array.reindex(itrades[:, 1]).fillna(0) * (itrades[:, 1] - itrades[:, 0] + 1)
        else:
            raise ValueError("period_costs should be either a single number or an array-like structure.")

    # Use the C extension to calculate positions
    strat_pnl = pd.Series(position_tools.calculate_positions(itrades, lclose.values, precision, slippage, transaction_cost), index=data.index)

    # Calculate metrics
    long_metrics = calculate_metrics(itrades[itrades[:, 2] == 1], trade_rets)
    short_metrics = calculate_metrics(itrades[itrades[:, 2] == -1], trade_rets)
    overall_metrics = calculate_metrics(itrades, trade_rets)

    return {
        'long_metrics': long_metrics,
        'short_metrics': short_metrics,
        'overall_metrics': overall_metrics,
        'itrades': itrades,
        'strat_pnl_pct': strat_pnl,
        'entry_points': data.index[itrades[:, 0]],
        'exit_points': data.index[itrades[:, 1]],
        'long_returns': long_metrics['returns'],
        'short_returns': short_metrics['returns'],
        'overall_returns': overall_metrics['returns'],
        'long_cum_returns': long_metrics['cum_returns'],
        'short_cum_returns': short_metrics['cum_returns'],
        'overall_cum_returns': overall_metrics['cum_returns'],
    }


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

def calculate_metrics(trades, trade_rets):
    if len(trades) == 0:
        return {metric: 0 for metric in [
            'tot_return', 'avg_return', 'avg_win', 'avg_loss',
            'win_ratio', 'profit_factor', 'n_trades', 'n_wins',
            'n_losses', 'max_drawdown', 'avg_drawdown', 'sharpe_ratio', 'sortino_ratio',
            'max_win', 'max_loss', 'sum_periods_in_wins', 'sum_periods_in_losses',
            'avg_periods_in_wins', 'avg_periods_in_losses', 'total_periods_in_trades',
            'avg_periods_in_trades', 'returns', 'cum_returns'
        ]}

    rets = trade_rets.reindex(trades[:, 1]).dropna()

    total_return = rets.sum()
    avg_return = rets.mean()

    wins = rets[rets > 0]
    losses = rets[rets <= 0]

    avg_win = wins.mean() if len(wins) > 0 else 0
    avg_loss = losses.mean() if len(losses) > 0 else 0
    max_win = wins.max() if len(wins) > 0 else 0
    max_loss = losses.min() if len(losses) > 0 else 0

    win_ratio = len(wins) / len(rets) if len(rets) > 0 else 0
    profit_factor = wins.sum() / abs(losses.sum()) if abs(losses.sum()) > 0 else np.nan
    n_trades = int(len(rets))
    n_wins = int(len(wins))
    n_losses = int(len(losses))

    # Calculate cumulative returns and drawdowns
    cum_rets = rets.cumsum()
    running_max = cum_rets.cummax()
    drawdowns = cum_rets - running_max
    max_drawdown = drawdowns.min()
    avg_drawdown = drawdowns.mean()

    # Calculate the number of periods for each trade
    periods_in_trades = trades[:, 1] - trades[:, 0] + 1  # periods in each trade

    # Calculate periods metrics
    win_indices = wins.index.values
    loss_indices = losses.index.values

    # Safely handle periods in trades by using valid indices
    win_period_indices = [i for i, end_idx in enumerate(trades[:, 1]) if end_idx in win_indices]
    loss_period_indices = [i for i, end_idx in enumerate(trades[:, 1]) if end_idx in loss_indices]

    sum_periods_in_wins = np.sum(periods_in_trades[win_period_indices]) if len(win_period_indices) > 0 else 0
    sum_periods_in_losses = np.sum(periods_in_trades[loss_period_indices]) if len(loss_period_indices) > 0 else 0
    avg_periods_in_wins = np.mean(periods_in_trades[win_period_indices]) if len(win_period_indices) > 0 else 0
    avg_periods_in_losses = np.mean(periods_in_trades[loss_period_indices]) if len(loss_period_indices) > 0 else 0
    total_periods_in_trades = np.sum(periods_in_trades)
    avg_periods_in_trades = np.mean(periods_in_trades)

    sharpe_ratio = calculate_sharpe_ratio(rets)
    sortino_ratio = calculate_sortino_ratio(rets)

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
        'sum_periods_in_wins': sum_periods_in_wins,
        'sum_periods_in_losses': sum_periods_in_losses,
        'avg_periods_in_wins': avg_periods_in_wins,
        'avg_periods_in_losses': avg_periods_in_losses,
        'total_periods_in_trades': total_periods_in_trades,
        'avg_periods_in_trades': avg_periods_in_trades,
        'returns': rets,
        'cum_returns': cum_rets,
    }

def print_metrics_table(metrics, convert_to_pct=False):
    headers = ["Metric", "Overall", "Long Positions", "Short Positions"]
    metrics_list = [
        'tot_return', 'max_drawdown', 'n_trades', 'sharpe_ratio', 'sortino_ratio', 
        'avg_return', 'max_win', 'max_loss', 'avg_win', 'avg_loss',
        'win_ratio', 'profit_factor', 'n_wins',
        'n_losses', 'avg_drawdown',
        'sum_periods_in_wins', 'sum_periods_in_losses', 'avg_periods_in_wins', 'avg_periods_in_losses',
        'total_periods_in_trades', 'avg_periods_in_trades'
    ]
    
    # Helper function to convert log returns and drawdowns to percentages
    def convert_log_to_pct(value):
        return (np.exp(value) - 1) if convert_to_pct else value

    # Metrics that should be converted to percentage if `convert_to_pct` is True
    conversion_metrics = {
        'tot_return', 'avg_return', 'max_win', 'max_loss', 'avg_win', 'avg_loss', 
        'max_drawdown', 'avg_drawdown'
    }

    # Print headers
    print(f"{headers[0]:<25} | {headers[1]:>15} | {headers[2]:>15} | {headers[3]:>15}")
    print("-" * 80)
    
    # Print each row dynamically
    for metric in metrics_list:
        if metric in conversion_metrics:
            overall_value = convert_log_to_pct(metrics['overall_metrics'].get(metric, 0))
            long_value = convert_log_to_pct(metrics['long_metrics'].get(metric, 0))
            short_value = convert_log_to_pct(metrics['short_metrics'].get(metric, 0))
        else:
            overall_value = metrics['overall_metrics'].get(metric, 0)
            long_value = metrics['long_metrics'].get(metric, 0)
            short_value = metrics['short_metrics'].get(metric, 0)

        print(f"{metric.replace('_', ' ').title():<25} | {overall_value:>15.4f} | {long_value:>15.4f} | {short_value:>15.4f}")


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

def optimize(data, param_defs, indicators, signals, enable_long=True, enable_short=True, xmult=1, n_trials=100, 
             optimize_metrics=None, directions=None):
    
    # Define default directions for each metric
    default_directions = {
        'sharpe_ratio': 'maximize',
        'sortino_ratio': 'maximize',
        'max_drawdown': 'minimize',
        'tot_return': 'maximize',
        'avg_drawdown': 'minimize',
        'avg_win': 'maximize',
        'avg_loss': 'minimize',
        'win_ratio': 'maximize',
        'profit_factor': 'maximize',
        'n_trades': 'maximize',  # Depending on the context, some may want to minimize this
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
        # metrics = backtest_fn(data, nhours, params, short_long=short_long, xmult=xmult)
        metrics = backtest(data, params, indicators=indicators, signals=signals, enable_long=True, enable_short=True)
        
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


def plot_performance(data, asset, params, indicators, signals, enable_long=True, enable_short=True, reset_index=False, title='', btkwargs={}):
    if reset_index:
        data = data.copy().reset_index(drop=True)
    
    # Run backtest with the provided parameters and keyword arguments
    metrics = backtest(data, params, indicators, signals, enable_long=enable_long, enable_short=enable_short)
    
    # Print the metrics table
    # print_metrics_table(metrics, convert_to_pct=True)
    itrades = metrics['itrades']

    if itrades is None or len(itrades) == 0:
        print("No trades found.")
        return None, metrics
    
    # Extract the trade exit points' indices
    trade_exit_indices = itrades[:, 1]
    
    # Separate the indices for long and short trades
    long_trade_indices = trade_exit_indices[itrades[:, 2] == 1]
    short_trade_indices = trade_exit_indices[itrades[:, 2] == -1]

    # Calculate cumulative returns for overall, long, and short positions
    overall_cum_returns = metrics['overall_cum_returns']
    long_cum_returns = metrics['long_cum_returns']
    short_cum_returns = metrics['short_cum_returns']

    # Align the cumulative returns with the trade exit indices
    combined_pnl_pct = pd.Series(np.exp(overall_cum_returns)).subtract(1).set_axis(data.index[trade_exit_indices])

    if len(long_trade_indices) > 0:
        long_pnl_pct = pd.Series(np.exp(long_cum_returns)).subtract(1).set_axis(data.index[long_trade_indices])
    else:
        long_pnl_pct = pd.Series([0] * len(data)).subtract(1).set_axis(data.index)

    if len(short_trade_indices) > 0:
        short_pnl_pct = pd.Series(np.exp(short_cum_returns)).subtract(1).set_axis(data.index[short_trade_indices])
    else:
        short_pnl_pct = pd.Series([0] * len(data)).subtract(1).set_axis(data.index)

    # Plot the results with the best parameters
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    fig.suptitle(f'{title} / {asset} ', fontsize=16)

    # Plot the indicators
    # plot_indicators(ax1, data)

    # Plot PnL as percentage for long, short, and combined
    ax2.axhline(0, color='black', lw=1)  # Baseline for percentage returns
    ax2.plot(combined_pnl_pct.index, combined_pnl_pct, label='Combined PNL %', color='teal', alpha=0.8, lw=2)
    if len(long_trade_indices) > 0:
        ax2.plot(long_pnl_pct.index, long_pnl_pct, label='Long PNL %', color='green', alpha=0.8, lw=2)
    if len(short_trade_indices) > 0:
        ax2.plot(short_pnl_pct.index, short_pnl_pct, label='Short PNL %', color='red', alpha=0.8, lw=2)
    
    ax2.set_yscale('log', base=2)
    ax2.legend(loc='best')

    # Plot entry and exit points
    for x in metrics['entry_points'].values: 
        ax1.axvline(x, color='blue', lw=1, alpha=0.2)
        ax2.axvline(x, color='blue', lw=1, alpha=0.2)
    for xx in metrics['exit_points'].values:
        ax1.axvline(xx, color='red', lw=1, alpha=0.2)
        ax2.axvline(xx, color='red', lw=1, alpha=0.2)
    for i in range(len(itrades)):
        color = ['red', 'green'][(itrades[i, 2] + 1) // 2]
        ax1.axvspan(xmin=data.index[itrades[i, 0]], xmax=data.index[itrades[i, 1]], color=color, alpha=0.1)
        ax2.axvspan(xmin=data.index[itrades[i, 0]], xmax=data.index[itrades[i, 1]], color=color, alpha=0.1)
    
    ax2.grid(axis='y')
    # plt.show()
    return fig, metrics
