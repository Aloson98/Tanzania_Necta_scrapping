from bs4 import BeautifulSoup
import requests
import re
from mongoengine import connect
from mongoengine.errors import NotUniqueError
from models import School, StudentSubjectResults, SchoolGPA, SubjectPerformance
import json
import difflib

def main():
    # initiate Database
    connect("necta_database_test", host="localhost", port=27017)

    url = "https://onlinesys.necta.go.tz/results/2024/acsee/index.htm"

    # subjects available
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
        "CHINESE": "chinese",
    }
    
    def get_closest_subject(subject_name, mapping):
        subject_name = subject_name.upper()
        keys = list(mapping.keys())
        closest_match = difflib.get_close_matches(subject_name, keys, n=1, cutoff=0.4)
        return mapping[closest_match[0]] if closest_match else None

    #clonning the schools from the latest published year (2024)
    try:
        homepage = requests.get(url)
    except requests.exceptions.RequestException as e: 
        raise Exception("Something went wrong with the request:") from e

    if homepage.status_code == 200:
        print("""
              Successfully connected to the NECTA website.
              Now lets clone our Data into the database.
              _______________________________________________
              """)
        
        response = homepage.text
        soup = BeautifulSoup(response, "html.parser")
        
        # extracting schools links
        links = []
        returned_links = soup.find_all("a")
        
        for link in returned_links:
            link_href = link.get("href")
            if link_href.split('/')[0] == "results":
                links.append(link_href)
                
            if link_href.split('\\')[0] == "results" and link_href not in links:
                cleaned_link = link_href.split("\\")[1]
                links.append(f"results/{cleaned_link}")
        
        # visit every school to get the required informations
        student_subjects = {}
        
        for item in list(reversed(links)):
        
            years = [2024, 2023, 2022, 2021, 2020]
            
            print(f"Starting School: {item}")
            for year in years:
    
                try:
                    url = f"https://onlinesys.necta.go.tz/results/{year}/acsee/{item}"
                    school_page = requests.get(url, timeout=10)
                except requests.exceptions.RequestException as e:  
                    print(f"request failed or timed out: {str(e)}")
                    continue
                
                if school_page.status_code != 200:
                    print(f"No data available for {year} - {item}")
                    continue  # Skip to the next year
                
                try:
                    response = school_page.text
                    soup = BeautifulSoup(response, "html.parser")
                    
                    # targeting only the potential tag
                    datas = soup.find_all('p', attrs={'align': 'LEFT'})
                    all_paragraphs = soup.find_all('p')
                    
                    if not datas or len(datas) < 2:
                        print(f"Skipping {year} - No valid data found.")
                        continue
                    
                    # checking the school details and save it
                    school_name = datas[1].contents[0].split(" ")
                    school_index = school_name.pop(0)
                    school_name = " ".join(word for word in school_name)
                except Exception as e:
                    print(f"Error extracting data for {year} - {school}: {e}")
                    continue  # Skip to the next year
                
                try:
                    school = School.objects.get(school_name=school_name.strip())
                    SchoolGPA.objects.get(school=school, result_year=year)
                except Exception as e:
                    print(f"working on year: {year} - {school_name}")
                    
                    school = School.objects(school_name=school_name.strip(), school_index=school_index.strip()).modify(
                        upsert=True, 
                        new=True, 
                        set__school_name=school_name.strip(), 
                        set__school_index=school_index.strip()
                    )
                    
                    
                    data_index = 0
                    valid_grades = {'A', 'B', 'C', 'D', 'E', 'F', 'S', 'X'}
                    
                    for data in datas:
                        data_index += 1
                        student_subjects = {}
                        content = data.contents[0]
                        
                        if "-" in content:
                            matches = re.findall(r"([\w/ ]+)\s+-\s+'([A-Z])'", content)
                            if len(matches) > 0:
                                for subject, grade in matches:
                                    subject = DB_FIELD_TO_MODEL_FIELD[subject.strip()]
                                    student_subjects[subject] = grade
                                
                                if subject and grade in valid_grades:  
                                    student_subjects[subject] = grade
                                
                                
                                # store the student data into the database and ignore if it already exists
                                if student_subjects: 
                                    student_subjects_results = StudentSubjectResults(
                                        school=school, 
                                        data_index=data_index, 
                                        result_year=year, 
                                        **student_subjects
                                    )
                                    try:
                                        student_subjects_results.save()
                                    except:
                                        pass
                        
                        # Saving the overall performance of the school
                        if "EXAMINATION CENTRE RANKING" in data.get_text() or "EXAMINATION CENTRE OVERALL PERFORMANCE" in data.get_text():
                            table_index = datas.index(data)
                            examination_centre_region = datas[table_index+2].contents[0].strip()
                            total_passed_candidate = int(datas[table_index+4].contents[0].strip()) if datas[table_index+4].contents[0].strip() != "-" else 0
                            school_GPA = float(datas[table_index+6].contents[0].strip()) if datas[table_index+6].contents[0].strip() != "-" else 0
                            
                            school.school_region = examination_centre_region
                            school.save()
                            
                            gpa = SchoolGPA(school=school, result_year=year, year_gpa=school_GPA, total_passed=total_passed_candidate)
                            gpa.save()
                            
                        if "EXAMINATION CENTRE SUBJECTS PERFORMANCE" in data.get_text():
                            overall_position = [all_paragraphs.index(value) for value in all_paragraphs if "EXAMINATION CENTRE SUBJECTS PERFORMANCE" in value.get_text()][0]
                            table_index = datas.index(data)  # Get the index where the table starts
                            last_data_index = table_index
                            
                            if year > 2022:
                                last_overall_position = overall_position + 10
                    
                                while True:  # Ensure we don't go out of bounds
                                    data_index = last_data_index + 1
                                    
                                    subject_code = int(datas[data_index].get_text().strip())
                                    subject_name = datas[data_index + 1].get_text().strip()
                                    
                                    if all_paragraphs[last_overall_position+9].get_text().strip() == '-':
                                        subject_gpa = 0
                                    else:
                                        try:
                                            subject_gpa = float(all_paragraphs[last_overall_position+9].get_text().strip())
                                        except:
                                            subject_gpa = int(all_paragraphs[last_overall_position+9].get_text().strip())
                                        
                                    subject = get_closest_subject(subject_name, DB_FIELD_TO_MODEL_FIELD)
                                    
                                    subject_performance = SubjectPerformance(school=school, result_year=year, subject_name=subject_name, subject_gpa=subject_gpa, subject_code=subject_code)
                                    subject_performance.save()
                                    
                                    last_data_index += 3  # Move to the next set
                                    last_overall_position += 10
                                    
                                    # Check if we still have data to process
                                    if last_data_index + 1 >= len(datas):
                                        break
                            else:
                                last_overall_position = overall_position + 11
                                
                                while True:  # Ensure we don't go out of bounds
                                    data_index = last_data_index + 1
                                    
                                    subject_code = int(datas[data_index].get_text().strip())
                                    subject_name = datas[data_index + 1].get_text().strip()
                                    
                                    if all_paragraphs[last_overall_position+9].get_text().strip() == '-':
                                        pass
                                    else:
                                        try:
                                            subject_gpa = float(all_paragraphs[last_overall_position+9].get_text().strip())
                                        except:
                                            subject_gpa = int(all_paragraphs[last_overall_position+9].get_text().strip())
                                        
                                    
                                    
                                    subject_performance = SubjectPerformance(school=school, result_year=year, subject_name=subject_name, subject_gpa=subject_gpa, subject_code=subject_code)
                                    subject_performance.save()
                                    
                                    last_data_index += 2  # Move to the next set
                                    last_overall_position += 11
                                    
                                    # Check if we still have data to process
                                    if last_data_index + 1 >= len(datas):
                                        break
                print(f"✅ Successfully processed {year} - {school_name}")
            # informing that one school has passed successfully
            print(f"{school_name}: DONE")
        print("All schools have been successfully cloned into the database.")

if __name__     == '__main__':
    main()    