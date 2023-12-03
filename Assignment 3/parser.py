# Name: Jessica Ortega
# Course: CS 4250
# Date: December 2, 2023
# Time Spent: 

from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.web_crawler
pages_collection = db.pages
professors_collection = db.faculty

def parse_faculty_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    faculty_members = soup.find_all('div', class_='clearfix')

    parsed_data = []
    for member in faculty_members:
        name_tag = member.find('h2')
        name = name_tag.get_text().strip() if name_tag else None

        strong_tags = member.find_all('strong')
        title, office, email, website = None, None, None, None

        for tag in strong_tags:
            if 'Title' in tag.get_text():
                title = tag.find_next('br').next_sibling.strip() if tag.find_next('br') else None
            elif 'Office' in tag.get_text():
                office = tag.find_next('br').next_sibling.strip() if tag.find_next('br') else None
            elif 'Email' in tag.get_text():
                email = tag.find_next('a').get_text().strip() if tag.find_next('a') else None
            elif 'Web' in tag.get_text():
                website = tag.find_next('a')['href'].strip() if tag.find_next('a') else None

        faculty_info = {
            'name': name,
            'title': title,
            'office': office,
            'email': email,
            'website': website,
        }

        if any(faculty_info.values()):
            parsed_data.append(faculty_info)

    return parsed_data

def process_pages():
    target_url = 'https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'
    
    document = pages_collection.find_one({'url': target_url})

    if document:
        html = document['html']
        faculty_info = parse_faculty_info(html)
        professors_collection.insert_many(faculty_info)
        print("Successfully stored.")
    else:
        print(f"URL not found: {target_url}")

if __name__ == "__main__":
    process_pages()

    client.close()
