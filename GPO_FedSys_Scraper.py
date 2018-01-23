from bs4 import BeautifulSoup
import requests
import csv
import  os


fedsys_search_url_pt1 = "https://www.gpo.gov/fdsys/search/search.action?sr="
fedsys_search_url_pt2 = "&originalSearch=collection%3aCRPT&st=collection%3aCRPT&ps=100&na=_congressnum&se=_"
fedsys_search_url_pt3 = "true&sb=re&timeFrame=&dateBrowse=&govAuthBrowse=&collection=&historical=true"

def write_data(data, header, writepath):
    ordered_fieldnames = header
    if os.path.exists(writepath):
        with open(writepath, "a") as dataset: 
            writer = csv.writer(dataset, dialect = "excel")
            writer.writerow(data)
    else:
        with open(writepath, "w") as dataset:
            csv.DictWriter(dataset, dialect = "excel", fieldnames = ordered_fieldnames).writeheader()
            writer = csv.writer(dataset, dialect = "excel")
            writer.writerow(data)

downloaded_files = [] 

if os.path.exists('Downloaded_file_links.csv'): 
	with open('Downloaded_file_links.csv', 'rb') as csvfile:
		downloaded_files_reader = csv.reader(csvfile, dialect='excel')
		next(downloaded_files_reader)
		for row in downloaded_files_reader:
			downloaded_files.append(row[0])
else:
	pass

print("Previous downloads loaded")
print(len(downloaded_files))

for congress in (range(104, 115)):
	if not os.path.exists("Reports/" + str(congress)):
		os.makedirs("Reports/" + str(congress))
	else:
		pass
	if not os.path.exists("Meta_data/" + str(congress)):
		os.makedirs("Meta_data/" + str(congress))
	else:
		pass

	more_info_links = []
	for page in range(1,17):
		r  = requests.get(fedsys_search_url_pt1 + str(page) +fedsys_search_url_pt2 + str(congress) + fedsys_search_url_pt3)
		soup = BeautifulSoup(r.text)
		search_results = soup.find("div", {"id":"search-results"})
		items = search_results.find_all("table", {"class": "search-results-item"})
		if len(items) > 0:
			link_lists = [i.find_all(href=True) for i in items]
			for links in link_lists:
				links = [ l.get("href") for l in links]
				more_info = "https://www.gpo.gov" + links[-1].replace("&amp;", "&")
				more_info_links.append(more_info)
			page_mssg = "Links collected from page %s" %page
			print(page_mssg)
		else:
			break

	link_gather_mssg = "Link Collection Completed for %sth Congress" %congress
	print(link_gather_mssg)



	for link in more_info_links:
		if link not in downloaded_files:
			try:
			    r  = requests.get(link)
			    soup = BeautifulSoup(r.text)
			    download_link = soup.find("table", {"class":"page-details-budget-metadata-table"}).find_all(href=True)[0].get("href")
			    details = soup.find("div", {"id":"page-details-right-mask"})
			    metadata = details.find("table", {"id":"page-details-metadata-table"})
			    file_name =  download_link.split("/")[-1]
			    report = requests.get(download_link)
			    with open("Reports/" + str(congress) + "/" + file_name, 'wb') as outfile:
			        outfile.write(report.content)
			        
			    with open("Meta_data/" +file_name + "metadata_table.csv", "w") as f:
			        wr = csv.writer(f)
			        wr.writerows([[td.text.encode("utf-8") for td in row.find_all("td")] for row in metadata.select("tr + tr")])    

				write_data([link, congress], ["URL", "Congress"], "Downloaded_file_links.csv") 
			except:
				write_data([link, congress], ["URL","Congress"], "Not_downloaded_file_links.csv") 

		else:
			pass