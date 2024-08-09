# ############################################################################################################################
# Last Update: July 22nd, 2020
# ############################################################################################################################



# ############################################################################################################################
# IMPORT PACKAGES
# ############################################################################################################################

#import all the necessary packages

import numpy as np #for numerical array data
import pandas as pd #for tabular data
import matplotlib.pyplot as plt #for plotting purposes
import matplotlib.pylab as pl #for plotting purposes

import csv
from datetime import datetime, timedelta

from matplotlib.collections import LineCollection #for plotting purposes
from sklearn import cluster, covariance, manifold #for graphical analysis



# ############################################################################################################################
# LOAD DATASETS
# ############################################################################################################################

# Load dataset for Firms Information
# file_name = 'CleanedData_Weekly.xlsx'
# sheet_name = 'Firms Info'
# firms_info = pd.read_excel(file_name, sheet_name, index_col=0)

# # Load dataset for T-Bill
# df_rf = pd.read_excel('CleanedData_Weekly.xlsx', 'T-Bill', index_col=0)
# df_rf.index=pd.to_datetime(df_rf.index)



# ############################################################################################################################
# FUNCTIONS USED FOR GETTING SUMMARY STATISTICS
# ############################################################################################################################

# #############################################################################
# Function used to find the Annualized Sharpe Ratio of x
def sr_annu(x_old,rf_old):
    index = x_old.index[x_old.apply(np.isnan)]
    x = x_old.drop(index).values
    rf = rf_old.drop(index).values
    
    n = len(x)
    ret_expected = np.sum(x-rf)/n
    std_dev = np.sqrt( np.sum( (x-rf - ret_expected)**2 ) / n )
    annu_ret_expected = (ret_expected+1)**52-1
    annu_std_dev = std_dev * np.sqrt(52)
    return annu_ret_expected/annu_std_dev


# #############################################################################
# Function used to find the Maximum drawdown
def mdd(x):
    #x is a return vector
    wealth = (x+1).cumprod()
    #determine cumulative maximum value
    cummax = wealth.cummax()
    #calculate drawdown vector
    drawdown = wealth/cummax - 1
    return drawdown.min()


# #############################################################################
# Function for getting Summary Statistic information, including:
# total returns, average returns, annualized average return, annualized standard deviation,
# annualized sharpe ratio, and maximum drawdown
# NOTE: it will drop the firms that have missing data during the specified time period
# def getSumStat(data, rf = df_rf['T-Bill'], rounding = 2):
    
#     # Get the Start and End date of the dataset
#     date_obj = data.index[0]
#     start_of_week = date_obj - timedelta(days=date_obj.weekday())
#     start = start_of_week.strftime("%m/%d/%Y")
#     end =  data.index[-1].strftime("%m/%d/%Y")
    
#     print('Summary Statistic Information from ' + start + ' to ' + end + ':')
#     # Check if there is NA in the dataset within the given time period
#     # If yes, then drop those firms before calculating its summary statistics
#     if(data.isnull().values.any()):
#         print('WARNING: Some firms have missing data during this time period!')
#         print('Dropping firms: ')
#         for Xcol_dropped in list(data.columns[data.isna().any()]): print(Xcol_dropped)
#         data = data.dropna(axis='columns')
    
#     sectors = firms_info.Sector
#     ss_temp = pd.DataFrame(sectors, index = data.columns, columns=['Sector'])
#     ss_temp['Total Return(%)'] = np.round((((data+1).cumprod()-1)*100).iloc[-1] , rounding)
#     ss_temp['Ave Return(%)'] = np.round(data.mean()*100, rounding)
#     ss_temp['Annu. Ave Return(%)'] = np.round(((data.mean()+1)**52-1)*100, rounding)
#     ss_temp['Annu. Std(%)'] = np.round(data.std()*np.sqrt(52)*100, rounding)
#     ss_temp['Annu. Sharpe Ratio'] = np.round(data.apply(sr_annu, rf_old=rf), rounding)
#     ss_temp['Max Drawdown(%)'] = np.round(data.apply(mdd)*100, rounding)
#     return(ss_temp)



# ############################################################################################################################
# FUNCTIONS USED FOR GRAPHICAL ANALYSIS
# ############################################################################################################################

# Reference: https://scikit-learn.org/stable/auto_examples/applications/plot_stock_market.html

# #############################################################################
# Function for performing graphical network analysis
# Print clusters information, graphical network information, summary statistics, and plot of individual firm performance
# Return correlation and precision matrix, as well as plotting configuration information
# NOTE: it will drop the firms that have missing data during the specified time period

def graphicalAnalysis(dataset):
    X = dataset
  
    
    # Get the firm names of the dataset
    names = np.array(list(X.columns))
    
    # Show the number of firms examined
    print('Number of assets examined:', X.shape[1])
    
    
    # #############################################################################
    # Learn a graphical structure from the correlations
    
    # Graphical Lasso is used here to estimate the precision matrix    
    edge_model = covariance.GraphicalLassoCV(max_iter=1000)

    # standardize the time series: 
    # using correlations rather than covariance is more efficient for structure recovery
    X_std = X / X.std(axis=0)
    edge_model.fit(X_std)
    
    # #############################################################################
    # Cluster using affinity propagation

    _, labels = cluster.affinity_propagation(edge_model.covariance_)
    n_labels = labels.max()
    
    for i in range(n_labels + 1):
        print('Cluster %i: %s' % ((i + 1), ', '.join(names[labels == i])))

    # #############################################################################
    # Find a low-dimension embedding for visualization: find the best position of
    # the nodes (the stocks) on a 2D plane

    node_position_model = manifold.MDS(n_components=2, random_state=0)
    embedding = node_position_model.fit_transform(X_std.T).T

    # #############################################################################
    # Visualization I
    
    # Specify node colors by cluster labels 
    color_list = pl.cm.jet(np.linspace(0,1,n_labels+1))
    my_colors = [color_list[i] for i in labels]
    
    # Compute the partial correlations
    partial_correlations = edge_model.precision_.copy()
    d = 1 / np.sqrt(np.diag(partial_correlations))
    partial_correlations *= d
    partial_correlations *= d[:, np.newaxis]
    non_zero = (np.abs(np.triu(partial_correlations, k=1)) > 0.02)
    
    # Compute the edge values based on the partial correlations
    values = np.abs(partial_correlations[non_zero])
    val_max = values.max()
    
    # Title of the plot
    title = 'Graphical Network Analysis of Selected Assets over the Period'
    
    # Display the partial correlation graph
    graphicalAnalysis_plot(d, partial_correlations, my_colors,
                           names, labels, embedding, val_max, title)
    
    # The configuration of the plot
    plot_config = [d, partial_correlations, my_colors, names, labels, embedding, val_max, title]
        
    return [edge_model.covariance_, edge_model.precision_], plot_config
# END of WARNING: Some firms have missing data during this time period!')
# print('Dfunction graphicalAnalysis
# #############################################################################


# #############################################################################
# Function Used for plotting the graphical network graph
def graphicalAnalysis_plot(d, partial_correlations, my_colors,
                           names, labels, embedding, val_max, title):
        
    non_zero = (np.abs(np.triu(partial_correlations, k=1)) > 0.02)
    n_labels = labels.max()
    
    #For correlation network graph
    fig = plt.figure(1, facecolor='w', figsize=(15, 7))

    plt.clf()
    ax = plt.axes([0., 0., 1., 1.])
    plt.axis('off')

    # Plot the nodes using the coordinates of our embedding
    plt.scatter(embedding[0], embedding[1], s=500 * d ** 2, c= my_colors)

    # Plot the edges
    start_idx, end_idx = np.where(non_zero)
    # a sequence of (*line0*, *line1*, *line2*), where::
    #            linen = (x0, y0), (x1, y1), ... (xm, ym)
    segments = [[embedding[:, start], embedding[:, stop]]
                for start, stop in zip(start_idx, end_idx)]
    values = np.abs(partial_correlations[non_zero])
    lc = LineCollection(segments,
                        zorder=0, cmap=plt.cm.hot_r, 
                        norm=plt.Normalize(0, .7 * val_max))
    lc.set_array(values)
    temp = (15 * values)
    temp2 = np.repeat(5, len(temp))
    w = np.minimum(temp, temp2)
    lc.set_linewidths(w)
    ax.add_collection(lc)
    axcb = fig.colorbar(lc)
    axcb.set_label('Strength')

    # Add a label to each node. The challenge here is that we want to
    # position the labels to avoid overlap with other labels
    for index, (name, label, (x, y)) in enumerate(
            zip(names, labels, embedding.T)):

        dx = x - embedding[0]
        dx[index] = 1
        dy = y - embedding[1]
        dy[index] = 1
        this_dx = dx[np.argmin(np.abs(dy))]
        this_dy = dy[np.argmin(np.abs(dx))]
        if this_dx > 0:
            horizontalalignment = 'left'
            x = x + .002
        else:
            horizontalalignment = 'right'
            x = x - .002
        if this_dy > 0:
            verticalalignment = 'bottom'
            y = y + .002
        else:
            verticalalignment = 'top'
            y = y - .002
        plt.text(x, y, name, size=10,
                 horizontalalignment=horizontalalignment,
                 verticalalignment=verticalalignment,
                 bbox=dict(facecolor='w',
                           edgecolor=plt.cm.nipy_spectral(label / float(n_labels)),
                           alpha=.6))

    plt.xlim(embedding[0].min() - .15 * embedding[0].ptp(),
             embedding[0].max() + .10 * embedding[0].ptp(),)
    plt.ylim(embedding[1].min() - .03 * embedding[1].ptp(),
             embedding[1].max() + .03 * embedding[1].ptp())
    plt.title(title)
    plt.show()
# END of function graphicalAnalysis_plot
# #############################################################################


# #############################################################################
# Function Used for plotting the graphical network graph for the specified sectors
# Can be used to see more details of the network graph
def graphicalAnalysis_plot_ZOOM_bySector(Sectors_list, plot_config):
    
    d = plot_config[0]
    pc = plot_config[1]
    my_colors = np.array(plot_config[2])
    names = plot_config[3]
    labels = plot_config[4]
    embedding = plot_config[5]
    val_max = plot_config[6]
    title = 'ZOOM IN VIEW: ' + plot_config[7]
    
    if ((not Sectors_list) == False):
        if(all([(s in firms_info.Sector.unique()) for s in Sectors_list])):
            f_in_sector_chosen = []
            for s in Sectors_list:
                f_in_sector_chosen += list(firms_info[firms_info.Sector == s].index)
        else:
            print('ERROR: Revision needed! At Least 1 Sector entered in the \"Sectors_choosen\" option is NOT in the dataset!')
            print('Check your format!')
    else:
        print('Error: Need to enter the sectors you wanted to examine in the \"Sectors_list\" option!')
        return
    
    f_selected = list(set(f_in_sector_chosen).intersection(set(names)))
            
    if(not f_selected):
        print('ERROR: Revision needed! No firms in the selected sectors!')
        print('Check your format!')
        print('Note that the sectors entered in the \"Sectors_list\" option should also be in the \"Sectors_choosen\" option!')
        return
    else:
        ind = np.array([np.where(names == i)[0][0] for i in f_selected])

    graphicalAnalysis_plot(d[ind], pc[ind[:, None], ind], my_colors[ind],
                           names[ind], labels[ind], embedding[:,ind], val_max, title)
# END of function graphicalAnalysis_plot_ZOOM_bySector
# #############################################################################


# #############################################################################
# Function Used for plotting the graphical network graph for the specified firms
# Can be used to see more details of the network graph
def graphicalAnalysis_plot_ZOOM_byFirm(firms_list, plot_config):
    
    d = plot_config[0]
    pc = plot_config[1]
    my_colors = np.array(plot_config[2])
    names = plot_config[3]
    labels = plot_config[4]
    embedding = plot_config[5]
    val_max = plot_config[6]
    title = 'ZOOM IN VIEW: ' + plot_config[7]
    
    if( all([(f in names) for f in firms_list]) ):
        if (not firms_list):
            print('Error: Need to enter the firms you wanted to examine in the \"firms_list\" option!')
            return
        else:
            ind = np.array([np.where(names == i)[0][0] for i in firms_list])
    else:
        print('Error: Revision needed! At Least 1 firm entered in the \"firms_list\" are NOT in the dataset!')
        print('Check your format and also whether the firms are dropped due to missing data!')
        return

    graphicalAnalysis_plot(d[ind], pc[ind[:, None], ind], my_colors[ind],
                           names[ind], labels[ind], embedding[:,ind], val_max, title)
# END of function graphicalAnalysis_plot_ZOOM_byFirm
# #############################################################################
