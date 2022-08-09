from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
import time
import pandas as pd
from datetime import datetime,timedelta
import re
locations = ["Qatar","United Kingdom","France","Turkey"]
#locations = ["Qatar"]
def get_jobs(keyword, num_jobs, verbose,path):
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    # Initializing the webdriver
    global jobs_for_country
    jobs_for_country = []
    global jobs_for_countries
    jobs_for_countries = []
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.set_window_size(1120, 1000)
    for country in locations:
        jobs_for_country=[]
        url='https://www.glassdoor.com/Search/results.htm?keyword={}&locT=C&locName={}'.format(keyword.replace(' ','%20'),country)
        time.sleep(5)
        driver.get(url)
        # Let the page load. Change this number based on your internet speed.
        # Maybe add extra sleeping at the steps you need for more loading time. 
        time.sleep(5)
        #click on button search depends on job_title and city 
        try:
            driver.find_element_by_xpath('//span[@class="SVGInline d-flex white"]').click()
        except:
            pass
        #after loding the page we are clicking on "see all the jobs " button 
        time.sleep(2)
        try:
            driver.find_element_by_xpath('//span[@class="SVGInline css-1mgba7 css-1hjgaef"]').click()
        except:
            pass
        # Click on the first job & Test for the "Sign Up" prompt and get rid of it.
        try:
            driver.find_element_by_xpath("//*[@id='MainCol']/div[1]/ul/li[1]").click()
        except:
            pass
        
        time.sleep(5)
        # Clicking on the Close X button to close the "Sign Up" prompt.
        try:
            driver.find_element_by_xpath('//*[@id="JAModal"]/div/div[2]/span').click()
        except NoSuchElementException:
            pass
        time.sleep(5)
        while len(jobs_for_country) < num_jobs:
            # Going through each job in this page
            job_buttons = driver.find_elements_by_xpath("//*[@id='MainCol']/div[1]/ul/li")
            # Going through each job url in this page
            job_buttons_href = driver.find_elements_by_xpath('//*[@id="MainCol"]/div[1]/ul/li/div[2]/a')
            number_of_all_page=driver.find_element_by_class_name("paginationFooter").text
            print("Now we in {} ".format(number_of_all_page))
                        
            for job in range( len(job_buttons)): 
                print("Progress: {}".format("" + str(len(jobs_for_country)) + "/" + str(num_jobs)))
                if len(jobs_for_country) >= num_jobs:
                    # When the number of jobs collected has reached the number we set. 
                    break
                job_buttons[job].click()  
                time.sleep(5)
                collected_successfully = False
                               
                while not collected_successfully:
                    try:
                        time.sleep(5)
                        company_name = driver.find_element_by_xpath('//div[@class="css-xuk5ye e1tk4kwz5"]').text
                        location = driver.find_element_by_xpath('.//div[@class="css-56kyx5 e1tk4kwz1"]').text
                        job_title = driver.find_element_by_xpath('.//div[@class="css-1j389vi e1tk4kwz2"]').text
                        job_id = job_buttons[job].get_attribute("data-id")
                        job_url= job_buttons_href[job].get_attribute("href")
                        job_description = driver.find_element_by_xpath('.//div[@class="jobDescriptionContent desc"]').text
                        collected_successfully = True
                    except:
                        collected_successfully = True
                                        
                try:
                    driver.find_element_by_xpath('//div[@class="css-t3xrds e856ufb2"]').click()
                except NoSuchElementException:
                    pass   
                job_description_full = driver.find_element_by_xpath('.//div[@class="jobDescriptionContent desc"]').text
                try:
                    Posted_Date=driver.find_element_by_xpath('//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[3]/div[2]/div[2]'.format(job+1)).text
                except NoSuchElementException:
                    Posted_Date=driver.find_element_by_xpath('//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[2]/div/div[2]'.format(job+1)).text
                    pass
                now = datetime.now()
                print("yesssssssssssssssssss =",type(Posted_Date))
                try:
                    exdate= [int(x) for x in re.findall(r'-?\d+\.?\d*',Posted_Date)][0]
                    Posted_Data_N=now.date() - timedelta(days=exdate)
                except:
                    Posted_Data_N=now.date()
                #Extract job title from job description full 
                lines=job_description_full.splitlines()
                t=False
                for line in lines:
                    if re.search('Job Types',line):
                        job_type = line.split(':')[1]
                        t=True
                if (t == False):
                    job_type='N/A'
                #print("the job is =",job_type)       
                try:
                    salary_estimate = driver.find_element_by_xpath('//*[@id="MainCol"]/div[1]/ul/li[{}]/div[2]/div[3]/div[1]/span'.format(job+1)).text
                except NoSuchElementException:
                    # You need to set a "not found value. It's important."
                    salary_estimate = 'N/A'
                print("the salary is =",salary_estimate) 
                try: 
                    rating = driver.find_element_by_xpath('//*[@id="employerStats"]/div[1]/div[1]').text
                except NoSuchElementException:
                    # You need to set a "not found value. It's important."
                    rating = 'N/A'
                print("the Rating = ",rating)
               
                #Extract Current Date Collection from a Datetime Object
                now = datetime.now()
                current_date = now.date()
                jobs_for_country.append({
                "Country" : country,
                "City" : location,
                "JobId" :job_id,
                "Source":"Glassdoor",
                "CollectedDate":current_date,
                "JobTitle" : job_title,
                "CompanyName" : company_name,
                "RatingNumber" : rating,
                "PostedDate":Posted_Date,
                "Salary" : salary_estimate,
                "jobType" :job_type,
                "JobURL" : job_url,
                "ShortDiscribtion" : job_description,
                "fullJobDescribtion":job_description_full,
                "Posted_Date_N":Posted_Data_N,
                })
            # Clicking on the "next page" button
            try:
                driver.find_element_by_css_selector('[alt="next-icon"]').click()
                time.sleep(10)
            except NoSuchElementException:
                print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs_for_country)))
                break
        for i in jobs_for_country:
            jobs_for_countries.append(i) 
    #This line converts the dictionary object into a pandas DataFrame.                
    return pd.DataFrame(jobs_for_countries)                    
path='chromedriver.exe'  
df=get_jobs('data', 3,False,path)
df.to_csv("data_final.csv",index=True)
     