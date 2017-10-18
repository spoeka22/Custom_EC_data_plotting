# -*- coding: utf-8 -*-
"""
Created on Tue Oct  18 19:25:46 2016

@author: Anna

Working part of the data plotting programme, that contains all the functions
"""
import numpy as np
import matplotlib.pyplot as plt

from pandas import DataFrame
import pandas as pd
import itertools
from anna_data_plot_input_original import e_rhe_ref, ph_ref, ph

from EC_MS import Data_Importing as Data_Importing_Scott
from EC_MS import EC as EC_Scott


# def import_data(datatype, filenames, general_info):
#     if datatype == "cv":
#         extract_cv_data(filenames, general_info)
#     else:
#         print("Error: plottype not available. Please check plottype")

def find_deltaI_DLcapacitance(e_vs_rhe, i_mApscm, e_range, file):
    #print(e_vs_rhe.index(max(e_vs_rhe)))

    #divide CV into oxizing and reducing half
    ox_part = DataFrame(data=[e_vs_rhe[:e_vs_rhe.index(max(e_vs_rhe))], i_mApscm[:e_vs_rhe.index(max(e_vs_rhe))]],
                        index=["EvsRHE", "imA/cm^2"]).transpose()
    red_part = DataFrame(data=[e_vs_rhe[e_vs_rhe.index(max(e_vs_rhe)):], i_mApscm[e_vs_rhe.index(max(e_vs_rhe)):]],
                         index=["EvsRHE", "imA/cm^2"]).transpose()

    #find indices corresponding to the selected e-range
    #print(e_range)
    ox_current=[]
    for eachvalue in ox_part.itertuples():
        if e_range[0]<= eachvalue[1] and e_range[1] >= eachvalue[1]:
           ox_current.append(eachvalue[2])
    #print(ox_current)
    red_current=[]
    for eachvalue in red_part.itertuples():
        if e_range[0] <= eachvalue[1] and e_range[1] >= eachvalue[1]:
            red_current.append(eachvalue[2])
    #print(red_current)
    #print(file)
    delta_i=np.mean(ox_current)-np.mean(red_current)
    print(str(file)+": The difference between oxidation and reduction current in the potential region " +str(e_range) + " = " + str(delta_i) +
          " mA/cm2")





def import_data_from(file):
   """opens file and extracts information about the number of header lines as
       given in the second row, then removes headerlines accordingly, and
       returns data as array
   """
   if ".mpt" in file:
       with open(file) as file:
           for line in file:
               if "header" in line:
                   headernumber = int(line[line.find(": ") + 2:])
                   break
           #load the columns containing data and converting them to rows
           data = pd.read_table(file, skiprows=headernumber-3, decimal=',')
   else:
       with open(file) as file:
           data = pd.read_table(file, decimal=',')
   return data

# def import_data_from(file):
#     """opens file by using Scott's set of function from EC-MS package, to make
#     imported data compatible with his functions.
#     file is then converted to form that can be used by standard functions for plotting here.
#     COMMENT:
#     This is probably quite useless because it simply adds some rather useless conversion steps to the data import.
#     Especially, since original data import version is already capable of importing all the data columns / the new functions
#     that handle cycle selection and CO strip integration don't rely on this kind of data import anyway.
#     """
#     DataDict = Data_Importing_Scott.import_data(file)
#     # print(DataDict)
#     data_in_datadict={column: DataDict[column] for column in DataDict['data_cols']}
#     print(sorted(DataDict.keys()))
#     # print(data_in_datadict)
#     # data=DataFrame(DataDict, columns=['mode', 'Ewe/V', '<I</mA'])
#     data = DataFrame(data_in_datadict)
#     #
#     # if ".mpt" in file:
#     #     with open(file) as file:
#     #         for line in file:
#     #             if "header" in line:
#     #                 headernumber = int(line[line.find(": ") + 2:])
#     #                 break
#     #         #load the columns containing data and converting them to rows
#     #         data = pd.read_table(file, skiprows=headernumber-3, decimal=',')
#     # else:
#     #     with open(file) as file:
#     #         data = pd.read_table(file, decimal=',')
#     # print(data)
#     return data




#def function(value):
#        new_value = value+5
#        return new_value


def convert_potential_to_rhe(e_ref):
    """
    Converts potential vs reference electrode to potential vs RHE
    using parameters defined in the settings
    :param e_ref: measured potential from data(frame)
    :return: e_rhe: potential vs RHE
    """
    e_nhe = - e_rhe_ref - 0.059 * ph_ref  # potential vs NHE
    e_rhe = e_ref + e_nhe + 0.059 * ph
    # print("Potential converted to RHE scale at pH=" + str(ph))
    return e_rhe

def ohmicdrop_correct_e(file, ohmicdrop):
    """
    Corrects for the Ohmic drop in the setup
    :param e_rhe: potential vs RHE, ohmicdrop: ohmic resistance of the setup (in Ohms)
    :return: e_rhe_corr
    """
    if 'individual ohmicdrop' in file['settings']:
        ohmic_drop = file['settings']['individual ohmicdrop']
        print(ohmic_drop)
    else:
        print("No individual ohmic drop selected. Using the general settings. ")
        ohmic_drop = ohmicdrop
    # print("Compenstating for R_ohm=" + str(ohmic_drop))
    # print(ohmicdropcorrected_e)
    e_rhe = file['data']['Ewe/V']

    I = file['data']['<I>/mA']
    #print(e_rhe, I)
    #from anna_data_plot_input_original import ohmicdrop
    e_rhe_corr = [e_rhe - I/1000 * ohmic_drop]
    # print(e_rhe_corr)
    ohmicdropcorrected_e = DataFrame(e_rhe_corr, index=['E_corr/V']).T
    # print(ohmicdropcorrected_e)
    print("Ohmic drop correction finished.")
    return ohmicdropcorrected_e


def convert_to_current_density(file, electrode_area_geom, electrode_area_ecsa):
    """
    Converts current into current density using the electrode surface area given in the settings
    :param I: measured current from data(frame)
    :return: current density
    """
#    from anna_data_plot_input_original import electrode_area_geom
    #check if there is individual settings, else use the general settings and creates 2 new columns
    #Data frame that then can be added to the general dataframe.

    if electrode_area_geom or 'electrode area geom' in file['settings']:
        if 'electrode area geom' in file['settings']:
            i_geom = file['data']['<I>/mA']/file['settings']['electrode area geom']
        else:
            i_geom = file['data']['<I>/mA']/electrode_area_geom
    else:
        i_geom=[]


    if electrode_area_ecsa or 'electrode area ecsa' in file['settings']:
        if 'electrode area ecsa' in file['settings']:
            i_ecsa = file['data']['<I>/mA']/file['settings']['electrode area ecsa']
        else:
            i_ecsa = file['data']['<I>/mA'] / electrode_area_ecsa
    else:
        i_ecsa = []


    i_df = DataFrame(data=[i_geom, i_ecsa], index=["i/mAcm^-2_geom", "i/mAcm^-2_ECSA"]).T


    return i_df


def find_scanrate(file):
    """finds scanrate in header and saves in a float
    """
    with open(file) as file:
       for line in file:
           if "dE/dt" in line and not "dE/dt unit" in line:
               scanrate = float(line[line.find("dE/dt")+16:])
               #print(scanrate)
               break
    return scanrate

def find_set_potential(file):
    """finds set potential in header, converts to E vs RHE and saves in a float
    """
    with open(file) as file:
       for line in file:
           if "Ei (V)" in line and not "dE/dt unit" in line:
               e_vs_ref = float(line[line.find("Ei (V)")+14:].replace(',','.'))
               e_vs_rhe = convert_potential_to_rhe(e_vs_ref)
               print(e_vs_ref, e_vs_rhe)
               break
    return e_vs_rhe

def makelabel(file):
    """Creates label from filename or selects label from "settings" part of data dictionary"""
    if 'label' in file['settings'] and file['settings']['label'] is not "":
        plot_label = file['settings']['label']
    else:
        plot_label = file['filename'] #for now
    return plot_label

def EC_plot(datalist, plot_settings, legend_settings, annotation_settings, ohm_drop_corr): #basically all the details that are chosen in the settings part go into this function
    """makes plots, main function of the program
    input: settings from anna_data_plot_settings through doplot function
    output: cv_plot
    """
    # prepare for figure with 2 x-axes
    print('Preparing a figure with 2 x-axes for plotting.')
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    #imports linestyle/colours
    linestyle_list = plot_settings['linestyle']
    color_list = plot_settings['colors']

    #select which data columns to plot
    if plot_settings['x_data']:
        x_data_col = plot_settings['x_data']
    elif plot_settings['plot type'] == "cv":
        if ohm_drop_corr:
            x_data_col = "E_corr_vsRHE/V"
        else:
            x_data_col = "EvsRHE/V"
    elif plot_settings['plot type'] == "ca":
        x_data_col = "time/s"
    else:
        print("Error: Select plot-type or data column for x-axis!")
        x_data_col=""

    if plot_settings['y_data']:
        y_data_col = plot_settings['y_data']
    elif plot_settings['plot type'] == "cv":
        y_data_col = "i/mAcm^-2_geom"
    elif plot_settings['plot type'] == "ca":
        if ohm_drop_corr:
            y_data_col = "E_corr_vsRHE/V"
        else:
            y_data_col = "EvsRHE/V"
    else:
        print("Error: Select plot-type or data column for y-axis!")
        y_data_col = ""

    leg1=[]
    leg2=[]

    for (each_file, color, linestyle) in itertools.zip_longest(datalist, color_list, linestyle_list):
        # print(each_file['data']['EvsRHE/V'])
            plot = ax1.plot(each_file['data'][x_data_col].values.tolist(), each_file['data'][y_data_col].values.tolist(), color=color,
                 linestyle=linestyle, label=makelabel(each_file))
            axis1 = leg1.append(plot)


        # x_data2

    # inserts second y-axis if data column to plot chosen in plot_settings['y_data2']
    if plot_settings['y_data2']:
        ax2 = ax1.twinx()  # adds second y axis with the same x-axis
        y2_data_col = plot_settings['y_data2']
        print(y2_data_col)
        for (each_file, color, linestyle) in itertools.zip_longest(datalist, color_list, linestyle_list):
            plot = ax2.plot(each_file['data'][x_data_col].values.tolist(), each_file['data'][y2_data_col].values.tolist(),
                     color=color, linestyle=linestyle, label=makelabel(each_file) + "(" +y2_data_col + ")")
            axis2= leg2.append(plot)

    if len(color_list) <= len(datalist):
        print("Careful! You are plotting more trances than you assigned colours. Python standard colours are used!")

    if len(linestyle_list) <= len(datalist):
        print("Careful! You are plotting more trances than you assigned linestyles. Style \"-\" is used!")





    # axis labels
    ax1.set_xlabel("E vs. RHE / V")
    ax1.set_ylabel("i / mA cm$^{-2}$")

    #set axis limits according to info given in settings
    ax1.set_xlim(plot_settings['x_lim'])
    ax1.set_ylim(plot_settings['y_lim'])

    #create legend according to settings
    all_axes=axis1+axis2
    labels = [l.get_label() for l in all_axes]
    ax1.legend(all_axes, labels, fontsize=legend_settings["fontsize"], loc=legend_settings["position"], ncol=legend_settings["number_of_cols"])
    # ax2.legend(fontsize=legend_settings["fontsize"], ncol=legend_settings["number_of_cols"])

    #grid
    if plot_settings['grid']:
        ax1.grid(True, color="grey")

     # inserts second x-axis with E vs Ref on top, if selected in settings. only if plot type is not CA
    if plot_settings['second axis'] and not plot_settings['plot type'] == 'ca':
        ax3 = ax1.twiny()
        ax1Ticks = ax1.get_xticks()
        ax3Ticks = ax1Ticks  # here the scaling of ticks could be changed

        def tick_function(e_rhe):
            e_nhe = - e_rhe_ref - 0.059 * ph_ref  # potential vs NHE
            e_ref = e_rhe - e_nhe - 0.059 * ph
            return ["%.2f" % z for z in e_ref]

        ax3.set_xticks(ax3Ticks)
        ax3.set_xbound(ax1.get_xbound())
        ax3.set_xticklabels(tick_function(ax3Ticks))
        ax3.set_xlabel("E vs. Hg/Hg$_2$SO$_4$ / V")

    #defines size of padding, important for legend on top, possibility to change space between subplots once implemented
    lpad = plot_settings['l_pad'] if plot_settings['l_pad'] else 0.15
    rpad = plot_settings['r_pad'] if plot_settings['r_pad'] else 0.15
    tpad = plot_settings['top_pad'] if plot_settings['top_pad'] else 0.10
    bpad = plot_settings['bottom_pad'] if plot_settings['bottom_pad'] else 0.15
    # wspace = pt.wspace[r1] if is_set(pt.wspace[r1]) else 0.12
    # hspace = pt.hspace[r1] if is_set(pt.hspace[r1]) else 0.12

    fig.subplots_adjust(left=lpad, right=1 - rpad, top=1 - tpad, bottom=bpad) # hspace=hspace, wspace=wspace)

    #safes figure as png and pdf
    if plot_settings['safeplot']:
        plt.savefig(plot_settings['plotname']+'.png', dpi=400, bbox_inches='tight')
        plt.savefig(plot_settings['plotname']+'.pdf', dpi=400, bbox_inches='tight')
    plt.show()



def cv_plot(cv_data, plot_settings, legend_settings, annotation_settings): #basically all the details that are chosen in the settings part go into this function
    """plot tuples of current/voltage
    main function of the program
    input: settings from anna_data_plot_settings through doplot function
    output: cv_plot
    """
    #print CV data for check
    #print(cv_data)



    # prepare for figure with 2 x-axes
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    #List of 6 different linestyles to loop through
    # linestyle_list= ['-', (0, (2, 3)), '--', (3, (15, 7.5)) ,'-.',':', '-', (0, (2, 3)), '--', (3, (15, 7.5)),'-.',':',
    #                  '-', (0, (2, 3)), '--', (3, (15, 7.5)), '-.', ':','-', (0, (2, 3)), '--', (3, (15, 7.5)) ,'-.',':']
    # linestyle_list = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
    #linestyle_list = [ ':', ':', ':', ':', ':', '-', '-', '-', '-', '-', '-']
    linestyle_list = plot_settings['linestyle']
    color_list = plot_settings['colors']
    #color_list = ['g', 'orange', 'r', 'b', 'k', 'g', 'orange', 'r', 'b', 'k', 'c', 'm', '0.50',"#538612", '0.75','orange', 'g', 'r', 'b', 'k', 'c', 'm', '0.50',"#538612", '0.75']
    #print(color_list)
    i=-1
    j=-1

    for each_cv in cv_data:
        if i <= 11:
            i = i+1
        else: 
            i = 0
        j = j +1
        x = cv_data[j]['data']['EvsRHE/V'].values.tolist()
        y = cv_data[j]['data']['i/mAcm^-2'].values.tolist()
        #print(x,y)
        print(i)
        plt.plot(x, y, color=color_list[i], linestyle = linestyle_list[i], label=cv_data[j]['label'])
        # find and print the difference in current in the double layer capacitance region
        current_file=cv_data[j]['filename']
        e_range = annotation_settings['e_range']
        find_deltaI_DLcapacitance(e_vs_rhe=x, i_mApscm=y, e_range=e_range, file=current_file)


    #set axis limits according to info given in settings
    ax1.set_xlim(plot_settings['x_lim'])
    ax1.set_ylim(plot_settings['y_lim'])

    #create legend according to settings
    plt.legend(fontsize=legend_settings["fontsize"], loc=legend_settings["position"], ncol=legend_settings["number_of_cols"])

    #grid
    if plot_settings['grid']:
        ax1.grid(True, color="grey")

    #inserts second axis with E vs Ref on top, if selected in settings
    if plot_settings['second axis']:
        ax2 = ax1.twiny()
        ax1Ticks = ax1.get_xticks()
        ax2Ticks = ax1Ticks  # here the scaling of ticks could be changed

        def tick_function(e_rhe):
            e_nhe = - e_rhe_ref - 0.059 * ph_ref  # potential vs NHE
            e_ref = e_rhe - e_nhe - 0.059 * ph
            return ["%.2f" % z for z in e_ref]

        ax2.set_xticks(ax2Ticks)
        ax2.set_xbound(ax1.get_xbound())
        ax2.set_xticklabels(tick_function(ax2Ticks))
        ax2.set_xlabel("E vs. Hg/Hg$_2$SO$_4$ / V")

    #axis labels
    ax1.set_xlabel("E vs. RHE / V")
    ax1.set_ylabel("i / mA cm$^{-2}$")

    #defines size of padding, important for legend on top, possibility to change space between subplots once implemented
    lpad = plot_settings['l_pad'] if plot_settings['l_pad'] else 0.15
    rpad = plot_settings['r_pad'] if plot_settings['r_pad'] else 0.15
    tpad = plot_settings['top_pad'] if plot_settings['top_pad'] else 0.10
    bpad = plot_settings['bottom_pad'] if plot_settings['bottom_pad'] else 0.15
    # wspace = pt.wspace[r1] if is_set(pt.wspace[r1]) else 0.12
    # hspace = pt.hspace[r1] if is_set(pt.hspace[r1]) else 0.12

    fig.subplots_adjust(left=lpad, right=1 - rpad, top=1 - tpad, bottom=bpad) # hspace=hspace, wspace=wspace)

    #safes figure as png and pdf
    if plot_settings['safeplot']:
        plt.savefig(plot_settings['plotname']+'.png', dpi=400, bbox_inches='tight')
        plt.savefig(plot_settings['plotname']+'.pdf', dpi=400, bbox_inches='tight')
    plt.show()

def ca_plot(ca_data, plot_settings, legend_settings, annotation_settings): #basically all the details that are chosen in the settings part go into this function
    """plot tuples of current/time
    input: settings from anna_data_plot_settings through doplot function and ca_data from extract_ca_data function
    output: ca_plot
    """
    # prepare for figure with 2 x-axes, not really necessary, but also opens possibilty for subplots
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    if plot_settings['coplot_evsrhe']:
        ax2 = ax1.twinx() #adds second y axis with the same x-axis

    #List of 6 different linestyles to loop through
    #linestyle_list = ['-', '-', '--','--', '-.','-.', ':', ':', (0, (2, 3)), (0, (2, 3)),  (3, (10, 5)),  (3, (10, 5))]
    #color_list = ['orange', 'orange', 'g', 'g', 'r', 'r', 'b', 'b', 'k', 'k', 'c', 'c']

#    linestyle_list = ['-', '--', '-.', ':', (0, (2, 3)), (3, (10, 5))]
#     linestyle_list = ['-', '-', '-', '-', '-', '-']
#     color_list = ['orange','g', 'r', 'b', 'k', 'c']
    linestyle_list = plot_settings['linestyle']
    color_list = plot_settings['colors']

    i=-1
    j=-1

    for each_ca in ca_data:
        if i <= 10: i = i+1
        else: i=0
        j = j+1

        x = ca_data[j]['data'][['time/s']].values.tolist()
        #x = ca_data[each_ca]['data'][['time/s']].values.tolist()
        y = ca_data[j]['data'][['i/mAcm^-2']].values.tolist()
        #y = ca_data[each_ca]['data'][['i/mAcm^-2']].values.tolist()
        #print(x,y)
        #print(i)
        ax1.plot(x, y, color=color_list[i], linestyle = linestyle_list[i], label=ca_data[j]['label'])
        if plot_settings['coplot_evsrhe']:
            y2 = ca_data[j]['data'][['E_corr/V']].values.tolist()
            ax2.plot(x, y2, color=color_list[i], linestyle=linestyle_list[i+1], label=ca_data[j]['label']+'_E_corr')

    #set axis limits according to info given in settings
    ax1.set_xlim(plot_settings['x_lim'])
    ax1.set_ylim(plot_settings['y_lim'])
    

    #create legend according to settings
    ax1.legend(fontsize=legend_settings["fontsize"], loc=legend_settings["position"], ncol=legend_settings["number_of_cols"])

    #grid
    if plot_settings['grid']:
        ax1.grid(True)

    #axis labels
    ax1.set_xlabel("time / s")
    ax1.set_ylabel("i / mA cm$^{-2}$")
    
    
    #settings for 2nd axis if chosen
    if plot_settings['coplot_evsrhe']:
        ax2.set_ylim(plot_settings['y2_lim'])
        ax2.set_ylabel("E_corr vs. RHE / V")
        

    #defines size of padding, important for legend on top, possibility to change space between subplots once implemented
    lpad = plot_settings['l_pad'] if plot_settings['l_pad'] else 0.15
    rpad = plot_settings['r_pad'] if plot_settings['r_pad'] else 0.15
    tpad = plot_settings['top_pad'] if plot_settings['top_pad'] else 0.10
    bpad = plot_settings['bottom_pad'] if plot_settings['bottom_pad'] else 0.15
    # wspace = pt.wspace[r1] if is_set(pt.wspace[r1]) else 0.12
    # hspace = pt.hspace[r1] if is_set(pt.hspace[r1]) else 0.12

    fig.subplots_adjust(left=lpad, right=1 - rpad, top=1 - tpad, bottom=bpad) # hspace=hspace, wspace=wspace)

    #safes figure as png and pdf
    if plot_settings['safeplot']:
        plt.savefig(plot_settings['plotname']+'.png', dpi=400, bbox_inches='tight')
        plt.savefig(plot_settings['plotname']+'.pdf', dpi=400, bbox_inches='tight')
    plt.show()


def extract_data(folder_path, filenames, folders, filespec_settings):
    """
    imports data from EC_lab file to a DataDict using Scott's function.
    If CV data and cycles selected, then extracts the selected cycles using Scott's
    function to extract cycles, looping through all the files given in "filenames"
    :return: list of dictionaries for each file/loop that was chosen to be plotted, each containing filename(+cycle),
    DataFrame of all extracted data (all data columns), and file specific settings (unaltered) as given in input as "settings".
    """
    data=[]
    # loop
    for folder, files in filenames.items():
        print("Now checking folder: " + folder)
        for filename in files:  # additional for loop to go through list of filenames
            if folder in folders:
                print("Extracting data from: " + filename)
                # filepath = folder
                filepath = folder_path + "/" + folder + "/" + filename
                # import from file
                datadict = Data_Importing_Scott.import_data(filepath)
                # print(filespec_settings[str(filename)].keys())
                if 'cycles to extract' in filespec_settings[str(filename)].keys():
                    for cycle in filespec_settings[str(filename)]['cycles to extract']:
                        data_selected_cycle = EC_Scott.select_cycles(datadict, [cycle]) #extract only the data from selected cycles
                        # print(data_selected_cycle['cycle number'])
                        # convert DataDict to DataFrame
                        data_selected_cycle_frame = DataFrame(convert_datadict_to_dataframe(data_selected_cycle))
                        # print(converted_e_and_i)
                        #collect all the data from different cycles in one big dictionary
                        data.append({'filename': filename + "_cycle_" + str(cycle), 'data': data_selected_cycle_frame, 'settings': filespec_settings[str(filename)]})
                        print("cycle " + str(cycle) +" extracted")
                else:
                    data_current_file = DataFrame(convert_datadict_to_dataframe(datadict))
                    data.append({'filename': filename, 'data': data_current_file, 'settings': filespec_settings[str(filename)]})
                    print("data from " + filename + " extracted")
    # print(data)
    return data

def convert_datadict_to_dataframe(datadict):
    """Converts DataDict output from Scott's import/cycle selection functions to DataFrame that is used by the plotting
    functions"""
    data_in_datadict = {column: datadict[column] for column in datadict['data_cols']}
    # print(sorted(datadict.keys()))
    # print(data_in_datadict)
    data = DataFrame(data_in_datadict)
    return data

