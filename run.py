from analysis.class_survey_analysis_wizard import preclean, save_new_data, clean1, yoy_condition, yoy_appropriateness, total_trend, total_sum, new_year_war, unit_cost_col, total_cost
import pandas as pd


def run(csv, old_doc, old_df):
	pre = preclean(csv)

	new_data,new_df = save_new_data(pre)

	cleaned = clean1(new_df,old_df)

	yoy_con = yoy_condition(cleaned, new_data)
	yoy_app = yoy_appropriateness(cleaned, new_data)

	con_trend = total_trend(yoy_con)
	app_trend = total_trend(yoy_app)

	old_mean=con_trend.iloc[0:2].mean(axis=0)
	new_mean=con_trend.mean(axis=0)
	mean_delta=(new_mean-old_mean)/old_mean
	means_stats={'old': old_mean, 'new': new_mean,'delta': mean_delta}

	total_sums=total_sum(con_trend,app_trend, means_stats)

	total_war=new_year_war(cleaned,new_data['con_q'], new_data)

	war_cats=pd.DataFrame(columns=['Condition Score','Frequency', 'Condition Score * Frequency','WAR'])
	cat_map={'Q2':'Presentation','Q3':'Lighting','Q4':'Student Seating','Q5':'Instructional Furniture','Q6':'Writing','Q7':'Temperature','Q8':'Finishes','Q9':'Clean'}
	for q in new_data['con_q']:
		qwar=new_year_war(cleaned, q, new_data)
		qwar['Category']=cat_map[q]
		war_cats=war_cats.append(qwar,sort=True)

	space=pd.read_csv('Clean Campus Master.csv', encoding='latin1')
	rooms=pd.read_csv('clean rooms.csv')
	rooms=rooms.iloc[:,1:5]
	rooms.iloc[:,2].astype(int)
	a=1
	space_cats=['NASF','Class_ID']
	slim_space=space[space_cats]
	space_war=pd.merge(left=war_cats,right=slim_space,how='left',left_index=True,right_on='Class_ID')
	rooms_space_war=pd.merge(left=space_war,right=rooms,how='left',left_on='Class_ID',right_on='room_id')
	rooms_space_war
	slim_rooms_space_war=rooms_space_war.drop(['Building','Room Number','room_id'],axis=1)
	slim_rooms_space_war.columns=['Category','Condition Score','Condition Score * Frquency','Frequency','WAR','NASF','Classroom','Capacity']
	new_col_order=['Classroom','Category','Condition Score','Frequency','Condition Score * Frquency','NASF','Capacity','WAR']
	slim_rooms_space_war=slim_rooms_space_war[new_col_order]

	slim_rooms_space_war['Category'].unique()

	unit_costs={'Finishes':3.33,'Student Seating':350,'Instructional Furniture':550,'Writing':300,'Lighting':200,'Presentation':0,'Temperature':0,'Clean':0}

	data_uc=unit_cost_col(slim_rooms_space_war,unit_costs)
	data_uc['NASF'].fillna(0)
	data_uc['Unit Cost'].astype(float)
	a=1

	total_uc=total_cost(data_uc)
	total_uc['WAR/Cost']=(total_uc['WAR']/total_uc['Cost'])*100000
	total_uc.sort_values('WAR/Cost', axis = 0, inplace=True, ascending=False)
	return total_uc