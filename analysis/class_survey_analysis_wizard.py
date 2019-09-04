#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

def preclean (csv):
    raw=pd.read_csv(csv, encoding='latin1')
    raw=raw.drop(raw.columns[[2,6,7,8,17,23]],axis=1)
    raw.columns=['ClassRoom','Course','First Name','Last Name','AcademicYear','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9','Q11','Q12','Q13','Q14','Q15']
    raw['Faculty']=raw['First Name'] +' '+ raw['Last Name']
    new_order=['AcademicYear','ClassRoom','Course','Faculty','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9','Q11','Q12','Q13','Q14','Q15']
    raw=raw[new_order]
    return raw

def save_new_data (data):
    store={}
    year_col=data['AcademicYear']
    store['year']=year_col.iloc[1]
    store['con_q']=['Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9'] #creates and stores a list of condition questions
    store['app_q']=['Q11','Q12','Q13','Q14','Q15'] #creates and stores a list of appropriateness questions
    return store,data

def clean1 (data,old_class):
       
    #Remove dashes and spaces in classroom column, make new column "dept"
    #which takes the dept code from the course column i.e.'econ'
    
    dept=data['Course'].str.split(pat='-',n=1,expand=True)#begin clean and reformatting
    data['Dept']=dept[0]
    data['ClassRoom']=(data['ClassRoom']
                            .str.replace('-','')
                            .str.replace(' ','')
                           )
    data=data.drop('Course',axis=1,inplace=False)
    
    #Change qualitative responses to numeric value 1-4, Missing values=0, set all numeric values to int data type
    
    data=(data
     .replace('Very dissatisfied',1)
     .replace('Dissatisfied',2)
     .replace('Satisfied',3)
     .replace('Very satisfied',4)
     .replace('Not at all ideal',1)
     .replace('Not ideal but functional',2)
     .replace('Functional',3)
     .replace('Ideal',4)
     .replace('D/A',0)
     .replace('No opinion',0)
     .replace('',0)
     .replace('Very Satisfied',4)
     .replace('1',1)
     .replace('2',2)
     .replace('3',3)
     .replace('4',4)
     .replace('nan',0)
     .replace('0',0)     
     .fillna(0)
         )#replace qualitative responses with numberic values 0-4
    
    data['ClassRoom']=(data['ClassRoom']
                       .str.replace('PFA','PF')
                       .str.replace('PFUD','PFAUD')
                      )
    data.iloc[:,3:15]=data.iloc[:,3:15].astype('int',copy=False)#change data types of numberic values to int
    
    #Merge old combined sheet with new sheet
    
    new_combined=old_class.append(data,sort=True)
    #new_combined.rename({"Unnamed: 0":"a"}, axis="columns", inplace=True)
    #new_combined=new_combined.drop('a',axis=1)   
    return new_combined   

def yoy_condition (clean, new_data):
    pivot=clean.pivot_table(values=new_data['con_q'],index='ClassRoom',columns='AcademicYear')
    means=pivot.mean(level=1,axis=1)
    return means


def yoy_appropriateness (clean, new_data):
    pivot=clean.pivot_table(values=new_data['app_q'],index='ClassRoom',columns='AcademicYear')
    means=pivot.mean(level=1,axis=1)
    return means


def total_trend (data):   
    means=data.mean(axis=0)#take means of every classroom for each year
    return means


def total_sum(c_trend, a_trend, means_stats):
    con_old_mean=c_trend.iloc[0:2].mean(axis=0)
    con_new_mean=c_trend.mean(axis=0)
    con_mean_delta=(con_new_mean-con_old_mean)/means_stats['old']
    app_old_mean=a_trend.iloc[0:2].mean(axis=0)
    app_new_mean=a_trend.mean(axis=0)
    app_mean_delta=(app_new_mean-app_old_mean)/means_stats['old']
    mean_sum=pd.DataFrame([[con_old_mean,con_new_mean,con_mean_delta],[app_old_mean,app_new_mean,app_mean_delta]],index=['Condition Score','Appropriateness Score'],columns=['Old','New','Percent Change'])
    return mean_sum


def new_year_war (clean, questions, new_data):
    academic_year_bool=clean['AcademicYear']==new_data['year'] #create bool for academic year of new year
    year_df=clean[academic_year_bool] #dataframe of condition scores from the new year
    pivot=year_df.pivot_table(values=questions,index='ClassRoom') #create pivot table of questions and dataframe of conditions scores from the year. 
    means=pivot.mean(level=0,axis=1) #combines each classroom value into one classroom value which represents the mean of all the values for that classroom
    means_means=means.mean(axis=1) #combines scores of each question to give one mean condition score for each class room 
    con_19=pd.DataFrame(data=means_means) #converts above into a dataframe
    freq=year_df['ClassRoom'].value_counts() #creates a dataframe "freq" which counts the frequency each classroom is found in the year_df
    war_df=pd.concat([con_19,freq],axis=1,sort=True) #concats condition score df and frequency into the war_df
    war_df.columns=['Condition Score','Frequency'] #renames columns in war_df
    war_df['Condition Score * Frequency']=war_df['Condition Score']*war_df['Frequency'] #creates condition*frequency column
    war_df['WAR']=(((war_df['Condition Score * Frequency'].sum(axis=0))-war_df['Condition Score * Frequency']+(war_df['Frequency']*4))/(war_df['Frequency'].sum(axis=0)))-((war_df['Condition Score * Frequency'].sum(axis=0)/war_df['Frequency'].sum(axis=0))) #calculates WAR stat
    return war_df


def unit_cost_col (data,map1):
    data['Unit Cost']=data['Category'].map(map1)
    return data


def total_cost (data):
    finishes_bool=data["Category"] == 'Finishes'
    data.loc[finishes_bool,'Cost']=data['Unit Cost']*data['NASF']
    student_seating_bool=data['Category']=='Student Seating'
    data.loc[student_seating_bool,'Cost']=data['Unit Cost']*data['Capacity']
    presentation_bool=data['Category']=='Presentation'
    data.loc[presentation_bool,'Cost']
    small_bool=data['Capacity']<=12
    medium_bool1=data['Capacity']>=13 
    medium_bool2=data['Capacity']<=30
    medium_bool=medium_bool1 & medium_bool2
    large_bool=data['Capacity']>30
    zero_bool=data['Capacity']==0
    small_presentation=presentation_bool & small_bool
    medium_presentation=presentation_bool & medium_bool
    large_presentation=presentation_bool & large_bool
    zero_presentation=presentation_bool & zero_bool
    data.loc[small_presentation,'Cost']=8000
    data.loc[medium_presentation,'Cost']=15000
    data.loc[large_presentation,'Cost']=30000
    data.loc[zero_presentation,'Cost']='N/A'
    same_bool1=data['Category']=='Instructional Furniture'
    same_bool2=data['Category']=='Writing' 
    same_bool3=data['Category']=='Lighting'
    same_bool=same_bool1 | same_bool2 | same_bool3
    data.loc[same_bool,'Cost']=data['Unit Cost']
    return data



