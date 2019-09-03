from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
driver_path = "/home/ahmetturgut/chromedriver"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=driver_path,chrome_options=chrome_options)
elastic_array=[]
elastic_company=[]
elastic_size=[]
elastic_indices=[]
mongodb_array=[]
mongodb_company=[]
mongodb_size=[]
mongodb_indices=[]
output = {}


def login():
    driver.get("https://account.shodan.io/login")
    driver.find_element_by_id("username").send_keys("ahmetturgut97")
    driver.find_element_by_id("password").send_keys("Ahmet100$")
    driver.find_element_by_name("login_submit").click()
def elastic():
    result=driver.find_elements_by_class_name('search-result')
    for i in range(len(result)):
        a = result[i].find_element_by_class_name('ip')
        elastic_array.append(a.text)
        company = result[i].find_element_by_class_name('os')
        elastic_company.append(company.text)
        try:
            companys = result[i].find_element_by_class_name('section-green')
            elastic_size.append(companys.text)
        except:
            elastic_size.append("NULL")
        all_indicex = result[i].text
        indices = all_indicex.split('Elastic Indices:')
        elastic_indices.append(indices[1])

def mongodb():
    result = driver.find_elements_by_class_name('search-result')
    for i in range(len(result)):
        a = result[i].find_element_by_class_name('ip')
        mongodb_array.append(a.text)
        company = result[i].find_element_by_class_name('os')
        mongodb_company.append(company.text)
        try:
            companys = result[i].find_element_by_class_name('section-green')
            mongodb_size.append(companys.text)
        except:
            mongodb_size.append("NULL")
        indices = result[i].find_elements_by_class_name('table')
        b = ""
        for aa in indices:
            b += aa.text
        mongodb_indices.append(b)

def nextpage():
    try:
        next = driver.find_element_by_link_text("Next")
        next.click()
        return 1
    except:
        return 0
def get_elastic():
    driver.get("https://www.shodan.io/search?query=port%3A%229200%22+all%3A%22elastic+indices%22++country%3A%22tr%22")
    while True:
        prelen = len(elastic_array)
        elastic()
        next=nextpage()
        if next == 0:
            break
def get_mongodb():
    driver.get("https://www.shodan.io/search?query=all%3A%22mongodb+server+information%22+all%3A%22metrics%22+country%3A%22tr%22")
    while True:
        prelen = len(mongodb_array)
        mongodb()
        next=nextpage()
        if next == 0:
            break
def write():
    output['ElasticSearch'] = []
    for i in range(len(elastic_array)):
        indices=elastic_indices[i]
        indicesarray=indices.split('\n')
        for j in range(len(indicesarray)):
            indicesarray[j]=indicesarray[j].strip()
        indicesarray.pop(0)
        lastindex=len(indicesarray)
        count = indicesarray[lastindex-1].count("...")
        if count>0:
            indicesarray.pop()
        output['ElasticSearch'].append({
            'ip': elastic_array[i],
            'company': elastic_company[i],
            'size': elastic_size[i]
            #'indices': indicesarray
        })
    output['MongoDb'] = []
    for i in range(len(mongodb_array)):
        indices=mongodb_indices[i]
        indicesarray=indices.split('\n')
        indicesarray.pop(0)
        output['MongoDb'].append({
            'ip': mongodb_array[i],
            'company': mongodb_company[i],
            'size': mongodb_size[i]
            #'indices': indicesarray
        })
    with open('open_DB.json', 'w') as outfile:
        json.dump(output, outfile, indent=4)


def main():
    login()
    get_elastic()
    get_mongodb()
    driver.close()
    write()

if __name__ == '__main__':
    main()
