from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('tbody')
row = table.find_all('th', attrs={'class':'font-semibold text-center'})
row_length = len(row)
row2 = table.find_all('td', attrs={'class':'text-center'})
row_length2 = len(row2)

temp = [] #initiating a list 

date = []
market_cap = []
volume = []
open = []
close = []

# get date
for i in range(0, row_length):
    Date = table.find_all('th', attrs={'class':'font-semibold text-center'})[i].text
    date.append(Date)
    
# get Market Cap  
for i in range(0, row_length2,4):
    Market_Cap = table.find_all('td', attrs={'class':'text-center'})[i].text
    Market_Cap = Market_Cap.strip()
    market_cap.append(Market_Cap)

# get Volume
for i in range(1, row_length2,4):
    Volume = table.find_all('td', attrs={'class':'text-center'})[i].text
    Volume = Volume.strip()
    volume.append(Volume) 

# get Open
for i in range(2, row_length2,4):
    Open = table.find_all('td', attrs={'class':'text-center'})[i].text
    Open = Open.strip()
    open.append(Open)

# get Close
for i in range(3, row_length2,4):
    Close = table.find_all('td', attrs={'class':'text-center'})[i].text
    Close = Close.strip()
    close.append(Close)

#scrapping process
    temp.append((Date,Market_Cap,Volume,Open,Close))
    
temp = temp[::-1]

table2 = soup.find('div', attrs={'class':'card-block'})
columns = [th.text for th in table2.find('thead').find_all("th")]


#change into dataframe
data = pd.DataFrame({
    columns[0] : Date,
    columns[1] : market_cap,
    columns[2] : volume,
    columns[3] : open,
    columns[4] : close
})
#insert data wrangling here
def delete_dollar(x):
    for i in x:
        xx = i.split('$')
        return int(xx[1].replace(',',''))
    
def delete_dollar_2(x):
    for i in x:
        if i == 'N/A':
            return 'N/A'
        else:
            xx = i.split('$')
            return float(xx[1].replace(',',''))

df2 = pd.DataFrame({
    columns[0] : date,
    columns[2] : volume, 
})

df2['Volume'] = df2[['Volume']].apply(delete_dollar,axis=1)
df2.set_index('Date')
df2['Date']=df2['Date'].astype('object')
df2['Volume']=df2['Volume'].astype('int64')
df2 = df2[::-1]
df2 = df2.set_index('Date')
plt.style.use('seaborn')
df2.plot(kind='line',
        ylabel='Daily ETH Volume',
        xlabel='Day',
        title='\
        Daily ETH Volume Traded 2 September 2022 - 2 October 2022',
        grid=False,
        rot=0)

#end of data wrangling 

@app.route("/")
def index(): 
	
	card_data = f'{data["Volume"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df2.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)