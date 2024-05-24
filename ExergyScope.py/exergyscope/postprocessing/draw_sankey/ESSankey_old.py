#!/usr/bin/python3
# -*- coding: utf-8 -*-

###############################################################################
## This program has been written by Noé Cornet, UCLouvain, in October 2020
##
## It generates a Sankey Diagram for the specific csv format of the file
##      input2sankey.csv, generated by EnergyScope TD [1].
## The generating function is inpired by [2].
###############################################################################
## Usage:
##      python3 ESSankey.py
##          -> when calling from the 'output/sankey/' directory
##      python3 ESSankey.py -p path/to/sankey/
##          -> when calling frome anywhere else.
##      python3 ESSankey.py -h
##          -> to display the help message.
###############################################################################
## [1] G. Limpens, S . Moret, H. Jeanmart, F. Maréchal (2019).
##      EnergyScope TD: a novel open-source model for regional energy systems.
##      Applied Energy 2019; Volume 255. https://doi.org/10.1016/j.apenergy.2019.113729
## [2] https://medium.com/kenlok/how-to-create-sankey-diagrams-from-dataframes-in-python-e221c1b4d6b0
###############################################################################
## Author: Noé Cornet
## Copyright: Copyright 2020, UCLouvain
## Credits: [2]
## License: public domain
## Version: 1.0.0
## Maintainer: Noé Cornet
## Email: noe.cornet@student.uclouvain.be
## Status: first release
###############################################################################

# Built-in/Generic Imports
import sys, getopt
from pathlib import Path

# Libraries
import pandas as pd
import plotly.graph_objects as go

__helpmsg__ = '''ESSankey help message.
Usage: ESSankey.py [OPTIONS]

\tOPTIONS:
\t\t-h
\t\t\tdisplay this help message.
\t\t-p directory_path, --path=directory_path
\t\t\tindicate the path of the sankey directory. Default is the current directory (\'./\').
\t\t\tSo leave empty only if you are calling this function from the directory where \'input2sankey.csv\' is located.
\t\t-o file, --ofile=file\n\t\t\tindicate the output html (temporary) file. Default is \'directory_path/python_generated_sankey.html\'.
\t\t-n, --no-open
\t\t\tprevent from automatically opening the generated html file in the browser.'''

#def drawSankey(path="./",outputfile='TO_REPLACE',auto_open=True):
def drawSankey(path="./",outputfile='TO_REPLACE',auto_open=True):
    path = Path(path)
    if path.stem == "input2sankey":
        path = path.parent
        print("Warning: you should not include 'input2sankey.csv' in your path, but only the path of the directory containing this file.")
    if outputfile == 'TO_REPLACE':
        outputfile = path / 'python_generated_sankey.html'
    if outputfile.parent.stem == "input2sankey":
        outputfile = outputfile.parent.parent / outputfile.name
    flows = pd.read_csv(path / "input2sankey.csv")
    fig = genSankey(flows,cat_cols=['source','target'],value_cols='realValue',title='Energy',color_col='layerColor')
    fig.write_html(str(outputfile), auto_open=auto_open)
    #fig.show()


def nodify(node_names):
    # uniqe name endings
    #ends = sorted(list(set([e[-1] for e in node_names])))
    nodes_x = []
    nodes_y = []
    EUD = ['Elec', 'Heat HT', 'HVC', 'Methanol', 'H2']
    UT = ['Plug', 'Electrical Motor','Electric Resistance', 'Cooler', 'Light Bulb']
    UD = ['Food Cooling', 'Industrial Cooling', 'Space Cooling', 'Other Elec', 'Residential heat', 'Mechanical Drive', 'Light']
    step1 = 0
    step2 = 0
    step3 = 0
    for i in node_names:
        #if i in EUD:
        #    nodes_x.append(0.65)
        #    nodes_y.append(0.5+ 0.1*step1)
        #    step1+=1
        if i in UT:
            nodes_x.append(0.85)
            nodes_y.append(0.7+ 0.05*step2)
            step2+=1
        #elif i == 'Storage':
        #    nodes_x.append(0.65)
        #    nodes_y.append(0.9)
        #elif i in UD:
        #    nodes_x.append(1)
        #    nodes_y.append(0.002*step3)
        #    step3 += 1
        else :
            nodes_x.append(float('nan'))
            nodes_y.append(float('nan'))
    # intervals
    #steps = 1 / len(ends)
    #
    ## x-values for each unique name ending
    ## for input as node position
    #nodes_x = {}
    #xVal = 0
    #for# e in ends:
    #    nodes_x[str(e)] = xVal
    #    xVal += steps
    #
    ## x and y values in list form
    #x_values = [nodes_x[n[-1]] for n in node_names]
    #y_values = [0.1] * len(x_values)

    #return x_values, y_values
    return(nodes_x,nodes_y)
def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram',color_col=[]):
    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#4B8BBE','#306998','#FFE873','#FFD43B','#646464', '#beb84b']
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp =  list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp
        
    # remove duplicates from labelList
    labelList = list(dict.fromkeys(labelList))
    
    # define colors based on number of level
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]]*colorNum
        
    # transform df into a source-target pair
    for i in range(len(cat_cols)-1):
        if i==0:
            sourceTargetDf = df[[cat_cols[i],cat_cols[i+1],value_cols,color_col]]
            sourceTargetDf.columns = ['source','target','count','color']
        else:
            tempDf = df[[cat_cols[i],cat_cols[i+1],value_cols,color_col]]
            tempDf.columns = ['source','target','count','color']
            sourceTargetDf = pd.concat([sourceTargetDf,tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source','target']).agg({'count':'sum', 'color':'first'}).reset_index()
        
    sourceTargetDf
    # add index for source-target pair
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))

    # creating the sankey diagram
    #nodified = nodify(node_names=labelList)
    data = go.Sankey(
        arrangement='snap',
        valueformat = ".1f",
        valuesuffix = "TWh",
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(
            color = "black",
            width = 0.5
          ),
          label = labelList,
          color = colorList,
           #x = nodified[0],
           # y = nodified[1]
        ),
        link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count'],
          color = sourceTargetDf['color'].apply(lambda h: hexToRGB(h,0.5))
        )
      )
    
    layout =  dict(
        title = title,
        font = dict(
          size = 10
        )
    )

    fig = go.Figure(data=[data], layout=layout)
    return fig

def hexToRGB(hex, alpha):
    hex = hex.lstrip('#')
    r = int(hex[0:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:6], 16)

    if (alpha): 
        return "rgba(%d, %d, %d, %.2f)" % (r,g,b,alpha)
    else:
        return "rgba(%d, %d, %d)" % (r,g,b)

def main(argv):
    path = Path('../')
    outputfile = ''
    auto_open = True
    try:
        opts, args = getopt.getopt(argv,"hp:o:n",["path=","ofile=","no-open"])
    except getopt.GetoptError:
        print(__helpmsg__)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(__helpmsg__)
            sys.exit()
        elif opt in ("-p", "--path"):
            path = Path(arg)
        elif opt in ("-o", "--ofile"):
            outputfile = Path(arg)
        elif opt in ("-n", "--no-open"):
            auto_open = False
    if outputfile == '':
        outputfile = path / 'python_generated_sankey_test2.html'

    drawSankey(path=path,outputfile=outputfile,auto_open=auto_open)


if __name__ == '__main__':
    #print("Executing without argument: assuming that this program file is in the same directory as the 'input2sankey.csv' directory.\nThe default input file is thus './input2sankey.csv'.")
    #print("If this does not work, please open python3 and run:\n\t>>> from ESSankey.py import drawSankey\n\t>>> drawSankey(path='/path/to/sankey/')")
    # main(sys.argv[1:])
    path = '../../../case_studies/2020_exergy_Industry/output/sankey'
    #path = '../case_studies/2020_exergy_Industry/output/sankey'
    drawSankey(path=path, auto_open=True)