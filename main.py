from bs4 import BeautifulSoup
import requests

base_url = "https://www.jonasaden.com/sample-packs/?product-page="

def get_page(page):
    html = requests.get(f"{base_url}{page}").text
    soup = BeautifulSoup(html, 'lxml')
    downloads = parse_page(soup)
    return downloads

def parse_page(soup):
    downloads = []
    forms = soup.findAll('form',class_=['somdn-download-single-form','somdn-archive-download-form','somdn-download-form'])
    for form in forms:
        try:
            key,action,product = [item.get('value') for item in form.findAll('input')]
            post_data = {'somdn_download_key':key,
                         'action':action,
                         'somdn_product':product}
        except:
            key,action,product,total_files = [item.get('value') for item in form.findAll('input')]
            post_data = {'somdn_download_key':key,
                         'action':action,
                         'somdn_product':product,
                         'somdn_totalfiles':total_files}
        url = form.get('action')
        print(url)
        downloads.append([url,post_data])
    return downloads

def download_sample(post):
    try:
        url = post[0]
        post_data = post[1]
        file_res = requests.post(url, data=post_data)
        header = file_res.headers
        file_name = header.get('Content-Disposition').split('="')[1][:-2]
        print(f"Downloaded: {file_name} {int(header.get('Content-Length'))/(1024**2)}MB")
        with open(file_name, 'wb') as file:
            file.write(file_res.content)
    except:
        print(f"Download Failed: Retrying")
        download_sample(post)

downloads = []
page_results = True
page = 1
while page_results:
    page_results = get_page(page)
    downloads.extend(page_results)
    page += 1

print(f"Downloading {len(downloads)} sample packs.")

for download in downloads:
    download_sample(download)

print("Done.")
