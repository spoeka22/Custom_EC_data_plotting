# -*- coding: utf-8 -*-
"""
Created on Tue Oct  18 19:25:46 2016

@author: Anna

Working part of the data plotting programme, that contains all the functions
"""
import numpy as np

import matplotlib
matplotlib.use('qt4agg')
import matplotlib.pyplot as plt


from pandas import DataFrame
import pandas as pd
import itertools
import os

from EC_MS import Data_Importing as Data_Importing_Scott
from EC_MS import EC as EC_Scott


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

def integrate_CV(dataline, Vspan, ox_red):
    """
    Determines the charge passed between the potential values specified in V_span.
    :param dataline:Data of a specific cycle.
    :param type: Either "CO_strip" or "oxide_red" for predefined Vspan and ox_red. If None, give individual values
    :param Vspan: Potential interval, potential vs RHE!!!
    :return: dQ: "integrated" potential (i.e. charge difference) in the selected region
    """
    #Test if dataline only contains one cycle, else ERROR MESSAGE!!
    # print(dataline)

    #check if ohmic drop correction was done and choose which column to use
    if "E_corr_vsRHE/V" in dataline['data']:  #THIS IS NOT WORKING FOR SOME REASON
        V_col="E_corr_vsRHE/V"
    else:
        V_col= "EvsRHE/V"

    #find (Q-Q0) in the V range given by V span and oxidation/reduction sweep according to ox_red
    data_keep_index=[]

    for (potential, oxred) in zip(dataline['data'][V_col].iteritems(), dataline['data']["ox/red"].iteritems()):
        # print(potential, oxred)
        # eachline_frame=DataFrame([eachline])
        # print(eachline_frame)
        if Vspan[0] < potential[1] < Vspan[1] and oxred[1] == ox_red:
            data_keep_index.append(potential[0])

    # print(data_keep_index)
    index_firstrow=data_keep_index[0]
    index_lastrow=data_keep_index[-1]
    data_keep=dataline['data'][index_firstrow:index_lastrow+1]
    # print(data_keep)

    # print(str(index_firstrow) + " stuff " + str(index_lastrow))

    #Calculate the difference in charge passed between beginning and end of selected peak
    dQ = data_keep.loc[index_lastrow, '(Q-Qo)/C'] - data_keep.loc[index_firstrow,'(Q-Qo)/C']
    #
    print("The total charge in the selected potential region is " + str(dQ) + " C.")
    #print(dataline['data'])
    # print(len(dataline['data']))
    # print(len(data_keep))
    return dQ

def find_ave_current(dataline, Vspan=0, ox_red = 0, tspan=0, I_col="<I>/mA"):
    """Calculates the average current in a given region(Vspan) (for example the current in the the DL region """

    #check if ohmic drop correction was done and choose which column to use

    # print("Function find_ave_current now active.")
    if "E_corr_vsRHE/V" in dataline['data']:  #THIS IS NOT WORKING FOR SOME REASON
        V_col="E_corr_vsRHE/V"
    else:
        V_col= "EvsRHE/V"

    data_keep_index = []

    if Vspan is not 0:
        for (potential, oxred) in zip(dataline['data'][V_col].iteritems(), dataline['data']["ox/red"].iteritems()):
            # print(potential, oxred)
            # eachline_frame=DataFrame([eachline])
            # print(eachline_frame)
            if Vspan[0] < potential[1] < Vspan[1] and oxred[1] == ox_red:
                data_keep_index.append(potential[0])


    elif tspan is not 0:
        # print("work based on tspan")
        for time in dataline['data']['time/s'].iteritems():
            # eachline_frame=DataFrame([eachline])
            # print(eachline_frame)
            if tspan[0] < time[1] < tspan[1]:
                data_keep_index.append(time[0])

    index_firstrow = data_keep_index[0]
    index_lastrow = data_keep_index[-1]
    data_keep = dataline['data'][index_firstrow:index_lastrow + 1]
    # print(data_keep)

    ave_current = np.mean(data_keep[I_col])
    if I_col == "<I>/mA":
        print("The average current is: " + str(ave_current) + "mA")
    # else:
        # print("The average current value of column " + I_col + "  is " + str(ave_current))
    return ave_current

def find_pot_at_time(dataline, time):
    ''' finds potential vs RHE at a given time.'''
    for timecounter in dataline['data']['time/s'].iteritems():
        if timecounter[1] > time - 1 and timecounter[1] <= time :
           # print(timecounter)
           time_index = timecounter[0]
        continue
    # print("timecounter: " + str(timecounter) )
    # potential = dataline['data'][time_index]
    potential = dataline['data'].ix[time_index, 'EvsRHE/V']
    print(time_index, potential)
    return potential



def current_at_time_plot(datalist, times, I_col):
    """finds current at certain time (adds +/-5s and finds average current in that window) and plots
    this against time -> get a different view on CAs
    HARDCODED plotsettings - suboptimal but enough for now
    """
    # prepare a figure
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    #prepare a dataframe to save the extracted data
    VI_data = pd.DataFrame({"filename": 0, "EvsRHE/V": 0, I_col: 0}, index=[0])
    for time in times:
        timespan=[time - 5, time + 5]
        print(time, timespan)
        # print(type(time))

        for dataline in datalist:
            print("Now extracting current at " + str(time) + "s from file "  + dataline['filename'])
            current = find_ave_current(dataline, tspan=timespan, I_col= I_col)
            potential = find_pot_at_time(dataline, time=timespan[1])
            VI_data_dataline = pd.DataFrame({"filename":[dataline['filename']],"EvsRHE/V": [potential], I_col: [current]}, index=[time])
            VI_data = VI_data.append(VI_data_dataline)
            # print(VI_data_dataline)
            # print(VI_data)
            # print("current and potential are {0} and {1}".format(str(current), str(potential)))
        print(VI_data.ix[time, 'EvsRHE/V'].values.tolist())
        print(VI_data.ix[time, I_col].values.tolist())
        ax1.plot(VI_data.ix[time, 'EvsRHE/V'].values.tolist(),VI_data.ix[time, I_col].values.tolist(), label=str(time) + " s", marker="o",
                 ls="")
    # print(VI_data)

    # axis labels
    if "ECSA" in I_col:
        ax1.set_ylabel('i / $\mu$A cm$^{-2}$$_{ECSA}$')
    else:
        ax1.set_ylabel(I_col)
    ax1.set_xlabel('E vs. RHE / V')

    # set axis limits
    # ax1.set_ylim(0,1)
    ax1.set_xlim(0.6, 1.3)

    #add legend
    ax1.legend()
    # plotname = input("Enter a name for saving the plot:")
    # plt.savefig("output_files/" + plotname + '.png')

    plt.show()

    # safe the VI data as csv file (comma separated)

    # data_filename = input("Enter a name for the datafile")
    # VI_data.to_csv("output_files/" + data_filename + '.csv', na_rep='NULL')


def calc_esca(datalines,  type="CO_strip", scanrate=50, Vspan=[], ox_red=[], charge_p_area=1):
    """ Input: list of 2 dictionaries containing data (file in datalist), one with surface area specific peak,
    one with reference peak. Calls integrate_CV function to evaluate charge difference in selected Vspan.
    calculates absolute difference between these charge differences & multiplies with a selected factor
    (or given one if type & metal chosen. returns & prints ECSA."""

    print(type)

    if type == "CO_strip":
        Vspan=[0.6, 1.2] #V vs. RHE, taken from Mittermeier et.al 2017
        ox_red = 1
    elif type == "oxide_red":
        Vspan=[0.4, 0.9] #V vs. RHE, taken from Mittermeier et.al 2017
        ox_red = 0

    #Integrate CV in selected area (using the charge calculated already by EC lab) for the first 2 CVs in the
    #list of data (datalines) only
    dQ=[]
    esca = None
    esca_co = None

    if type == "oxide_red":
        deltaQ=[]
        for dataline in datalines:
            reduction_charge = abs(integrate_CV(dataline, Vspan=Vspan, ox_red=ox_red))
            dQ.append(reduction_charge)
            #correction: subtraction of double layer charge calculated by finding current in DL region,
            #and multiplying that with time found from potential difference (Vspan) multiplied with scanrate to get correct units
            reduction_peak_time = (Vspan[1]-Vspan[0])*scanrate*0.001 #time in s from start to end of integration area
            reduction_charge_corr = reduction_charge - abs(find_ave_current(dataline, Vspan=[0.37, 0.46], ox_red=ox_red))*0.001 * reduction_peak_time
            deltaQ.append(reduction_charge_corr)

            print("The oxide reduction charge for file: " + str(dataline['filename']) +
              " has been calculated to " + str(reduction_charge_corr) + " C.")
            # print("You need to find some reference for the relation between surface area and oxide reduction "
            #       "current before I can calulate the ECSA for you.")

    else:  #compares two consecutive cycles (meant for CO-strip)
        for dataline in datalines:
            dQ.append(integrate_CV(dataline, Vspan=Vspan, ox_red=ox_red))
            if len(dQ) > 2:
                break

        #calculate the difference in dQ between the 2 first CVs in datalines
        deltaQ = abs(dQ[0]-dQ[1])
        print("The charge difference between following CVs: (" +str(datalines[0]['filename']) + " and " +
            str(datalines[1]['filename']) + ") is " + str(deltaQ) + " C.")
        #calculate ECSA
        if type == "CO_strip":
            esca_co = deltaQ * 1000000 / (2*205)  #taken from Mittermeier et.al 2017, only valid for Pd!!
            print("An ECSA of " + str(esca_co) + " cm^2 was estimated based on CO-stripping on Pd.")
        else:
            esca=deltaQ/charge_p_area
            print("An ECSA of " + str(esca) + "cm^2 was estimated based on the value you entered for charge per area.")

    esca_data=[deltaQ, esca_co, esca]

    # return deltaQ, esca_co, esca
    return  esca_data





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


def convert_potential_to_rhe(e_ref, e_rhe_ref, ph_ref, ph):
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
            i_ecsa = file['data']['<I>/mA']/file['settings']['electrode area ecsa'] *1000
        else:
            i_ecsa = file['data']['<I>/mA'] / electrode_area_ecsa *1000
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

def find_axis_label(data_col):
    """Finds the appropriate axis label for different kinds of plotted data."""
    axis_label = None
    if "E" in data_col and not "mA" in data_col:
        if data_col == "EvsRHE/V" or data_col =="E_corr_vsRHE/V":
            axis_label = "E vs. RHE / V"
        elif data_col == "Ewe/V" or data_col == "E_corr/V":
            axis_label = "E vs. Ref / V"
        else:
            print("Something wrong with potential axis labelling.")
    elif data_col == "time/s":
        axis_label = "Time / s"
    elif "i" in data_col or "I" in data_col:
        if data_col == "i/mAcm^-2_geom":
            axis_label = "i / mA cm$^{-2}$$_{geom.}$"
        elif data_col == "i/mAcm^-2_ECSA":
            axis_label = "i / $\mu$A cm$^{-2}$$_{ECSA}$"
        elif data_col == "<I>/mA":
            axis_label = "I / mA"
        else:
            print("Something wrong with current density axis labelling.")
    else:
        axis_label = "Charge / C"  #This might not be the smartest way to deal with it, but ok for now.
    print("Label for " + str(data_col) + " is: " + str(axis_label))
    return axis_label


def EC_plot(datalist, plot_settings, legend_settings, annotation_settings, ohm_drop_corr, esca_data): #basically all the details that are chosen in the settings part go into this function
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
    linestyle_list2 = plot_settings['linestyle2']
    color_list2 = plot_settings['colors2']

    #select which data columns to plot
    if not plot_settings['x_data'] == "":
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

    if not plot_settings['y_data'] == "":
        y_data_col = plot_settings['y_data']
    elif plot_settings['plot type'] == "cv":
        y_data_col = "i/mAcm^-2_geom"
    elif plot_settings['plot type'] == "ca":
        y_data_col = "i/mAcm^-2_geom"
        # if ohm_drop_corr:
        #     y_data_col = "E_corr_vsRHE/V"
        # else:
        #     y_data_col = "EvsRHE/V"
    else:
        print("Error: Select plot-type or data column for y-axis!")
        y_data_col = ""


    for (each_file, color, linestyle) in itertools.zip_longest(datalist, color_list, linestyle_list):
        # print(each_file['data']['i/mAcm^-2_geom'])
        # print(each_file['data'][x_data_col])
        # x=each_file['data'][x_data_col]
        #.values.tolist()
        # y=each_file['data'][y_data_col] #.values.tolist()
        # ax1.plot(x,y)
        try:
            ax1.plot(each_file['data'][x_data_col].values.tolist(), each_file['data'][y_data_col].values.tolist(), color=color,
                 linestyle=linestyle, label=makelabel(each_file))
        except TypeError:
            if len(datalist) < len(color_list) or len(datalist) < len(linestyle_list):
                continue
            else:
                print("Problem plotting datalist...")

    #color the integrated are in the CO CVs grey if calculation of esca is done
    #This doesnt work, probably because the two cycles dont have the same number of points.

    # if esca_data:
    #     x=datalist[0]['data'][x_data_col].values.tolist()
    #     y1=datalist[0]['data'][y_data_col].values.tolist()
    #     y2=datalist[1]['data'][y_data_col].values.tolist()
    #     print(str(x))
    #     print(str(y1))
    #     print(str(y2))
    #     ax1.fill_between(x, y1, y2)
    #             # facecolor='b', interpolate=True)


    # x_data2

    # inserts second y-axis if data column to plot chosen in plot_settings['y_data2']
    if plot_settings['y_data2']:
        ax2 = ax1.twinx()  # adds second y axis with the same x-axis
        y2_data_col = plot_settings['y_data2']
        print(y2_data_col)
        for (each_file, color, linestyle) in itertools.zip_longest(datalist, color_list2, linestyle_list2):
            try:
                ax2.plot(each_file['data'][x_data_col].values.tolist(), each_file['data'][y2_data_col].values.tolist(),
                         color=color, linestyle=linestyle, label=makelabel(each_file) + "(" +y2_data_col + ")")
            except TypeError:
                if len(datalist) < len(color_list2) or len(datalist) < len(linestyle_list2):
                    continue
                else:
                    print("Problem plotting datalist (2nd y axis)...")

    if len(color_list) < len(datalist):
        print("Careful! You are plotting more traces than you assigned colours. Python standard colours are used!")

    if len(linestyle_list) < len(datalist):
        print("Careful! You are plotting more traces than you assigned linestyles. Style \"-\" is used!")


    # axis labels
    ax1.set_xlabel(find_axis_label(x_data_col))
    ax1.set_ylabel(find_axis_label(y_data_col))
    if not plot_settings['y_data2'] == "":
        ax2.set_ylabel(find_axis_label(y2_data_col))

    #set axis limits according to info given in settings
    ax1.set_xlim(plot_settings['x_lim'])
    ax1.set_ylim(plot_settings['y_lim'])
    if not plot_settings['y_data2'] == "":
        ax2.set_ylim(plot_settings['y2_lim'])

    #create legend according to settings

    ax1.legend(fontsize=legend_settings["fontsize"], loc=legend_settings["position1"], ncol=legend_settings["number_of_cols"])
    if not plot_settings['y_data2'] == "":
        ax2.legend(fontsize=legend_settings["fontsize"], loc=legend_settings["position2"], ncol=legend_settings["number_of_cols"])

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

    #annotations
    if esca_data:
        # print(esca_data[0], esca_data[1])
        # anno_esca="$\Delta$Q ="+ str(esca_data[0]) + "C \n ESCA$_{CO}$= " + str(esca_data[1]) + "cm$^2$"

        if type(esca_data[0]) is list:
            anno_esca = []
            for (datafile, esca_charge) in itertools.zip_longest(datalist,esca_data[0]):
                anno_esca.append(datafile['settings']['label'] + ': $\Delta$Q = {:.2e} C'.format(esca_charge))
            anno_esca.sort()
            anno_print="\n".join(anno_esca)
            ax1.annotate(anno_print, xy=(0.45, 0.05), xycoords="axes fraction")
        else:
            print("notlist")
            anno_esca = '$\Delta$Q = {:.2e} C'.format(esca_data[0]) + '\n ECSA$_{CO}$ = ' + '{:.2e} cm$^2$'.format(
                esca_data[1])
            ax1.annotate(anno_esca, xy=(0.6, 0.05), xycoords="axes fraction")

    #safes figure as png and pdf
    if plot_settings['safeplot']:
        if os.path.exists("output_files/" + plot_settings['plotname']+'.png'):
            overwrite = input("Do you want to overwrite an existing plot? (y/n)")
            if overwrite == "y" or overwrite == "yes":
                print("Overwriting file.")
            else:
                plot_settings['plotname'] = input("Enter new filename:")

        plt.savefig("output_files/" + plot_settings['plotname']+'.png', dpi=400, bbox_inches='tight')
        plt.savefig("output_files/" + plot_settings['plotname']+'.pdf', dpi=400, bbox_inches='tight')
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
                # print(filespec_settings.keys())
                # print(filespec_settings[str(filename)].keys())
                if str(filename) in filespec_settings.keys():
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
                        data.append({'filename': filename, 'data': data_current_file,
                                     'settings': filespec_settings[str(filename)]})
                        print("data from " + filename + " extracted using settings specified for file.")
                else:
                    data_current_file = DataFrame(convert_datadict_to_dataframe(datadict))
                    data.append({'filename': filename, 'data': data_current_file, 'settings': []})
                    print("data from " + filename + " extracted using standard settings.")
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

