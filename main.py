from bs4 import BeautifulSoup
import requests
import re
from mongoengine import connect
from mongoengine.errors import NotUniqueError
from models import School, StudentSubjectResults

#initiate Database
connect("necta_results", host="localhost", port=27017)


url = "https://onlinesys.necta.go.tz/results/2022/acsee/index.htm"

#subjects available
DB_FIELD_TO_MODEL_FIELD = {
    "G/STUDIES": "g_studies",
    "GEOGR": "geography",
    "CHEMISTRY": "chemistry",
    "BIOLOGY": "biology",
    "BAM": "bam",
    "ADV/MATHS": "adv_math",
    "ECONOMICS": "economics",
    "HISTORY": "history",
    "KISWAHILI": "kiswahili",
    "ENGLISH": "english",
    "PHYSICS": "physics",
    "COMMERCE": "commerce",
    "ACCOUNTANCY": "accountancy",
    "DIVINITY": "divinity",
    "ARABIC": "arabic",
    "FRENCH": "french",
    "AGRICULTURE": "agriculture",
    "IS/KNOWLEDGE": "is_knowledge",
    "EDUCATION": "education",
    "COMP STUD": "comp_stud",
    "COMP/SCIENCE": "comp_science",
    "HN  NUTRITION": "hn_nutrition",
    "PHY EDU": "phy_edu",
    "FINE ART": "fine_art",
}


try:
    homepage = requests.get(url)
except requests.exceptions.RequestException as e: 
    raise Exception("Something went wrong with the request:") from e

if homepage.status_code == 200:
    response = homepage.text
    soup = BeautifulSoup(response, "html.parser")
    
    #extracting schools links
    links = []
    returned_links = soup.find_all("a")
    
    for link in returned_links:
        link_href = link.get("href")
        if link_href.split('/')[0] == "results":
            links.append(link_href)
    
    #visit every school to get the required informations
    student_subjects = {}
    
    for school in links:
        url = f"https://onlinesys.necta.go.tz/results/2022/acsee/{school}"

        try:
            school_page = requests.get(url)
        except requests.exceptions.RequestException as e:  
            raise Exception("Something went wrong with the request:") from e
        
        if school_page.status_code == 200:
            response = school_page.text
            soup = BeautifulSoup(response, "html.parser")
            
            #targeting only the potential tag
            datas = soup.find_all('p', attrs={'align': 'LEFT'})
            
            #checking the school details andsave it
            school_name = datas[1].contents[0].split(" ")
            school_index = school_name.pop(0)
            school_name = " ".join(word for word in school_name)
            
            try:
                School.objects.get(school_name=school_name)
            except:
                school = School(school_name=school_name, school_index=school_index.strip())
                school.save()
                
                data_index = 0
                for data in datas:
                    data_index+=1
                    student_subjects = {}
                    content = data.contents[0]
                    
                    if "-" in content:
                        matches = re.findall(r"([\w/ ]+)\s+-\s+'([A-Z])'", content)
                        if len(matches) > 0:
                            for subject, grade in matches:
                                subject = DB_FIELD_TO_MODEL_FIELD[subject.strip()]
                                student_subjects[subject] = grade
                            
                            #store the student data into the database
                            student_subjects_results = StudentSubjectResults(school=school, data_index=data_index, **student_subjects)
                            
                            try:
                                student_subjects_results.save()
                            except NotUniqueError:
                                raise NotUniqueError("A result with this data_index already exists for this school.")
            
            #informing that one school has passed successfully
            print(f"{school_name}: DONE")
                                
                            