from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get("https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31")
soup = BeautifulSoup(url_get.content)

div = soup.find("div", attrs={"class","lister-list"})

temp = [] #initiating a tuple

for i in range (50):
#insert the scrapping process here
    
    tab = div.find_all("h3")[i]
    
    judul = tab.find_all("a")[0].text
    judul = judul.strip()

    rating = div.find_all("strong")[i].text

    meta = soup.select(".ratings-bar , .ratings-metascore")
    meta = [title.text for title in meta]
    meta = meta[i].strip()
    meta = meta.replace(meta[:59],"")
    meta = meta[6:8]


    votes = soup.select(".sort-num_votes-visible span:nth-child(2)")
    votes = [title.text for title in votes]
    votes = votes[i].replace(",","")

    temp.append((judul,rating,meta,votes))


temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns = ('Judul',"IMDB Rating","Metascore","Votes"))

#insert data wrangling here
data["Judul"] = data["Judul"].astype("category")
data["IMDB Rating"] = data["IMDB Rating"].astype("float64")
data["Metascore"] = data["Metascore"].replace("",0)
data["Metascore"] = data["Metascore"].astype("float64")
data["Votes"] = data["Votes"].astype("float64")

top_7 = data.sort_values(['IMDB Rating','Votes'], ascending=False).head(7)
top_7 = top_7[::-1]
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'IMDB Rating {top_7["IMDB Rating"].mean().round(2)}'

	# generate plot
	figure(figsize=(13,7))
	plt.plot("IMDB Rating","Judul", data = top_7, marker="*", ls = "--", ds = "steps-mid", c = "red")
	plt.plot("IMDB Rating","Judul", data = top_7, c = "black")
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
