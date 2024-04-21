from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
import pandas as pd


app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()

users = {
    "admin": "secret",
    "user": "pass"
}

df = pd.read_csv('./area_forecasts.csv', index_col=0)
json_output = df.to_json(orient='index', indent=4)



@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username



@app.route('/stats', methods=['GET'])
@auth.login_required
def stats():
    return json_output

data = pd.read_csv('./cleaned_healthcare_dataset.csv')
dataPiChatrts = pd.read_csv('./cleaned_healthcare_dataset.csv')

data['Date of Admission'] = pd.to_datetime(data['Date of Admission'])

# Filter data for the latest month
latest_month = data['Date of Admission'].dt.to_period("M").max()
filtered_df = data[data['Date of Admission'].dt.to_period("M") == latest_month]

# Pivot the DataFrame
pivot_df = filtered_df.pivot_table(index='Area', columns='Medical Condition', aggfunc='size', fill_value=0)

# Rename the columns to remove spaces
pivot_df.columns = [col.replace(' ', '_') for col in pivot_df.columns]
json_output2 = pivot_df.to_json(orient='index')



@app.route('/past', methods=['GET'])
@auth.login_required
def past():
    return json_output2

dataPiCharts = dataPiCharts[['Area', 'Medical Condition', 'Gender']]
grouped = dataPiCharts.groupby(['Area', 'Medical Condition', 'Gender']).size().reset_index(name='Count')
all_areas = dataPiCharts['Area'].unique()
all_conditions = dataPiCharts['Medical Condition'].unique()
all_genders = ["Male", "Female"]

all_combinations = pd.MultiIndex.from_product([all_areas, all_conditions, all_genders],
                                              names=['Area', 'Medical Condition', 'Gender'])
all_combinations_df = pd.DataFrame(index=all_combinations).reset_index()

# Merge this with the grouped data to ensure all combinations are present
merged_df = pd.merge(all_combinations_df, grouped, on=['Area', 'Medical Condition', 'Gender'], how='left').fillna(0)

# Now pivot the merged DataFrame
pivot_table = merged_df.pivot_table(index=['Area', 'Medical Condition'], columns='Gender', values='Count', fill_value=0)

# Step 5: Pivot the DataFrame to organize counts by 'Area' and 'Medical Condition'
# Step 6: Reformat the pivot table to the desired nested dictionary structure
# This nests the gender counts within each medical condition for each area
json_structure = {}
for (area, condition), genders in pivot_table.iterrows():
    if area not in json_structure:
        json_structure[area] = {}
    json_structure[area][condition] = genders.astype(int).to_dict()

# Step 7: Convert the dictionary to a JSON string with proper formatting
json_output3 = json.dumps(json_structure, indent=4)

@app.route('/picharts', methods = ['GET'])
@auth.login_required
def piCharts():
    return json_output3



    

if __name__ == '__main__':
    app.run()
