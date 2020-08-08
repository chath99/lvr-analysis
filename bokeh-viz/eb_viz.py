# import libraries
from bokeh.plotting import figure
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, HoverTool, Panel
from bokeh.models.widgets import Tabs

import pandas as pd
import numpy as np
import math

# define html output file
output_file("eb_viz.html", title="Equity Builder Analysis")

# assumptions - make interactive later!
annual_rate = 0.039
monthly_rate = ((1+annual_rate)**(1/12))-1

total_invested = 10000

max_monthly_investment = 3000

def amortise(principal, rate, repayment):
    remaining = principal
    months = 0
    interest_paid = 0
    while remaining > 0:
        if remaining < repayment:
            principal_paid = repayment - remaining
            remaining = remaining - principal_paid
            months = months + 1
        else:
            interest_paid = interest_paid + remaining*monthly_rate
            principal_paid = repayment - remaining*monthly_rate
            remaining = remaining - principal_paid
            months = months + 1
            
    amortisation_output = {}
    for variable in ["months", "interest_paid"]:
        amortisation_output[variable] = eval(variable)
    
    return amortisation_output

def random_returns(months):
    mean_return = 0.07/12
    sd_return = ((1+0.1689)**(1/12))-1
    
    returns = np.random.normal(loc=mean_return, scale=sd_return, size=months)
    
    return returns

def equity_builder(invested_amount):
    months = amortise(invested_amount, monthly_rate, max_monthly_investment)['months']
    interest_paid = amortise(invested_amount, monthly_rate, max_monthly_investment)['interest_paid']
    returns = random_returns(months)
    revenue = sum(returns*invested_amount)
    profit = revenue - interest_paid
    
    equity_builder_output = {}
    for variable in ["months", "profit"]:
        equity_builder_output[variable] = eval(variable)
    
    return equity_builder_output

def no_LVR(invested_amount):
    months = math.ceil(invested_amount/max_monthly_investment)
    returns = random_returns(months)
    month_list = np.array(range(1, months+1))
    profit = (invested_amount/months)*sum(returns*month_list)
    
    no_LVR_output = {}
    for variable in ["months", "profit"]:
        no_LVR_output[variable] = eval(variable)
    
    return no_LVR_output

def compare(invested_amount):
    months_eb = amortise(invested_amount, monthly_rate, max_monthly_investment)['months']
    months_noLVR = math.ceil(invested_amount/max_monthly_investment)
    months = max(months_eb, months_noLVR)
    
    returns = random_returns(months)
    
    # equity builder
    interest_paid = amortise(invested_amount, monthly_rate, max_monthly_investment)['interest_paid']
    revenue_eb = sum(returns[:months]*invested_amount)
    profit_eb = revenue_eb - interest_paid
    
    # no LVR
    month_list = np.array(range(1, months+1))
    profit_noLVR = (invested_amount/months)*sum(returns[:months]*month_list)
    
    compare_output = {}
    for variable in ["months", "returns", "profit_eb", "profit_noLVR"]:
        compare_output[variable] = eval(variable)
    
    return compare_output

def monte_carlo(invested_amount, draws):
    results = pd.DataFrame(columns = ["Invested", "Equity_Builder", "No_LVR"])
    
    for sim in range(0,draws):
        Invested = invested_amount
        comp = compare(invested_amount)
        Equity_Builder = comp['profit_eb']
        No_LVR = comp['profit_noLVR']
        sim_output = {}
        for variable in ["Invested", "Equity_Builder", "No_LVR"]:
            sim_output[variable] = eval(variable)
        
        sim_output = pd.DataFrame([sim_output])
        results = results.append(sim_output, sort=False)
    
    results.reset_index(drop=False, inplace=True)
        
    return(results)

def create_hist(data, bins):
    hist, edges = np.histogram(data, bins=bins)
    
    hist_df = pd.DataFrame({"column": hist,
                            "left": edges[:-1],
                            "right": edges[1:]})
    hist_df["interval"] = ["%d to %d" % (left, right) for left,
                           right in zip(hist_df["left"], hist_df["right"])]
    
    return hist_df

def visualise_MC(total_invested, draws, instrument, show_plot):
    sim = monte_carlo(total_invested, draws)
    index = sim.index
    eb = sim['Equity_Builder']
    nL = sim['No_LVR']
    
    sims = {}
    for variable in ["eb", "nL"]:
        sims[variable] = ColumnDataSource(create_hist(eval(variable), bins=100))
    
    mc_plot = figure(plot_width = 800, plot_height = 600,
                  title = "Expected profit",
                  x_axis_label = 'Expected profit', y_axis_label = 'Count')
    
    mc_plot.quad(bottom = 0, top = "column",
                 left = "left", right = "right",
                 source = sims[instrument],
                 fill_color = 'red', line_color = 'black', fill_alpha = 0.7,
                 hover_fill_alpha = 1.0, hover_fill_color = 'white')
    
    hover = HoverTool(tooltips = [('Expected profit', '$@interval'),
                                  ('Count', '@column')])
    mc_plot.add_tools(hover)
    
    if show_plot == True:
        show(mc_plot)
    else:
        return mc_plot
    

def histotabs(total_invested, draws, instruments):
    hists = []
    for i in instruments:
        h = visualise_MC(total_invested, draws, i, False)
        p = Panel(child=h, title=i)
        hists.append(p)
    
    t = Tabs(tabs=hists)
    show(t)

instruments = ["eb", "nL"]
histotabs(total_invested, 1000, instruments)
  



'''Tutorial - simple plot

# create a blank figure with labels
p = figure(plot_width = 600, plot_height = 600,
           title = "Example Glyphs",
           x_axis_label = 'X', y_axis_label = 'Y')

# example data
squares_x = [1, 3, 4, 5, 8]
squares_y = [8, 7, 3, 1, 10]
circles_x = [9, 12, 4, 3, 15]
circles_y = [8, 4, 11, 6, 10]

# add squares glyph
p.square(squares_x, squares_y, size = 12, color = 'navy', alpha = 0.6)

# add circles glyph
p.circle(circles_x, circles_y, size = 12, color = 'red')
'''






