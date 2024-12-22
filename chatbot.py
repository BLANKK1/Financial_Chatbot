from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import sys

app = Flask(__name__)

def load_company_data():
    df = pd.read_csv('Data_of_Comapny.csv')
    return df

def clean_column_name(column):
    return column.lower().strip().replace(' ', '')

def get_metric_from_query(query, df):
    metric_mapping = {
        'revenue': 'Total Revenue',
        'totalrevenue': 'Total Revenue',
        'netincome': ' Net Income',
        'income': ' Net Income',
        'assets': 'Total Assets',
        'totalassets': 'Total Assets',
        'liabilities': 'Total Liabilities',
        'totalliabilities': 'Total Liabilities',
        'cashflow': 'Cash Flow from Operating Activities',
        'operatingcashflow': 'Cash Flow from Operating Activities',
        'revenuegrowth': 'Revenue Growth (%)',
        'assetgrowth': 'asset Growth (%)',
        'cashflowgrowth': 'cash flow from operation Growth (%)',
        'liabilitiesgrowth': 'Liabilities Growth (%)',
        'incomegrowth': 'Net Income Growth (%)'
    }
    
    query_terms = query.lower().replace(' ', '')
    for key, value in metric_mapping.items():
        if key in query_terms:
            return value
    return None

def get_response(query):
    query = query.lower().strip()
    
    if query == 'exit':
        return "exit_chat"  # Special return value for exit command
    
    if query in ['hello', 'hi', 'hey']:
        return ("Hi there! You can ask me about company financials. Try questions like:\n"
                "- What is the total revenue of Apple in 2022?\n"
                "- Show me the net income of Microsoft in 2021\n"
                "- What are the total assets of Google in 2020?")
    
    if query == 'help':
        return ("Available metrics you can ask about:\n"
                "- Total Revenue\n"
                "-  Net Income\n"
                "- Total Assets\n"
                "- Total Liabilities\n"
                "- Cash Flow from Operating Activities\n"
                "- Revenue Growth (%)\n"
                "- Asset Growth (%)\n"
                "- Cash Flow Growth (%)\n"
                "- Liabilities Growth (%)\n"
                "- Net Income Growth (%)")

    if query in ['thanks', 'thankyou']:
        return("You're welcome! Let me know if you need any help")
        
    try:
        df = load_company_data()
        
        metric = get_metric_from_query(query, df)
        if not metric:
            return "Sorry, I can only provide information on predefined queries. Type 'help' to see available queries."
        
        company = next((company for company in df['Company'].unique() 
                       if company.lower() in query.lower()), None)
        if not company:
            return "I couldn't identify the company in your query. Please specify a company name."
        
        year = next((str(year) for year in df['Year'].unique() 
                    if str(year) in query), None)
        if not year:
            return "I couldn't identify the year in your query. Please specify a year."
        
        result = df[(df['Company'].str.lower() == company.lower()) & 
                    (df['Year'] == int(year))][metric].values
        
        if len(result) > 0:
            if 'Growth' in metric:
                formatted_value = f"{result[0]:.2f}%"
            else:
                formatted_value = "${:,}".format(int(result[0]))
            
            return f"The {metric.lower()} of {company} in {year} was {formatted_value}"
        else:
            return f"No data found for {company} in {year}"
            
    except Exception as e:
        return f"Error processing query: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_message = request.json.get('message', '')
    response = get_response(user_message)
    
    if response == "exit_chat":
        return jsonify({
            'response': "Goodbye! Chat session ended.",
            'exit': True
        })
    
    return jsonify({
        'response': response,
        'exit': False
    })

@app.route('/exit')
def exit_app():
    # Shutdown the server
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug=True)