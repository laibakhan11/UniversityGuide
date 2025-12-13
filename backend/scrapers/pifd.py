
import requests
from bs4 import BeautifulSoup
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.university import University, Program, Eligibility, Scholarship, EmbeddedDeadline
from models.deadline import Deadline
from config.db import get_db
db = get_db()
url = "https://pifd.edu.pk/admission.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=30, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    print("Page loaded successfully!\n")
except Exception as e:
    print(f"Failed to load page: {e}")
    exit()

# ========================================
# SCRAPE FEE STRUCTURE
# ========================================
print("Scraping Fee Structure...")
table = soup.find('div', id="collapseThree").find('table', class_="semester-breakdown w-100")
rows = table.find_all('tr', class_="semester-text")

first_sem = 0
second_sem = 0
fee_details = []

for row in rows:
    cols = row.find_all('td')
    if len(cols) >= 3:
        desc = cols[0].get_text(strip=True)
        amt1 = cols[1].get_text(strip=True).replace('/-', '').replace(',', '').replace('-', '0').strip()
        amt2 = cols[2].get_text(strip=True).replace('/-', '').replace(',', '').replace('-', '0').strip()
        
        try:
            first_sem += int(amt1)
            second_sem += int(amt2)
            fee_details.append(f"{desc}: Rs. {amt1} (1st sem), Rs. {amt2} (2nd-8th sem)")
        except:
            pass

print(f"   → First Semester: Rs. {first_sem:,}")
print(f"   → Second Semester: Rs. {second_sem:,}")
print(f"   → First Year Total: Rs. {first_sem + second_sem:,}")

# ========================================
# SCRAPE PROGRAMS
# ========================================
print("\nScraping List of Programmes...")
programs = []
heading = soup.find(string=re.compile(r"Degree\s+Programmes", re.I))

if heading:
    parent = heading.find_parent()
    ul = None
    
    for sibling in parent.find_next_siblings():
        if sibling.name in ["ul", "ol"]:
            ul = sibling
            break
        if sibling.find(["ul", "ol"]):
            ul = sibling.find(["ul", "ol"])
            break
    
    if ul:
        items = ul.find_all("li")
        print(f"   → Found {len(items)} programs")
        
        for item in items:
            name = item.get_text(strip=True)
            name = re.sub(r"^\d+[\.\)]\s*", "", name).strip()
            
            if name and len(name) > 5:
                programs.append(Program(
                    name=name,
                    department="Pakistan Institute of Fashion and Design",
                    fee_per_semester=second_sem,
                    total_fee_first_year=first_sem + second_sem,
                    eligibility=Eligibility(
                        min_percentage_matric=45.0,
                        min_percentage_inter=45.0,
                        entry_test="PIFD Entry Test + Interview",
                        notes="2nd Division in Intermediate or equivalent"
                    ),
                    notes=f"Admission Fee: Rs. 18,000 (one-time) | Security Deposits: Rs. 20,000 (refundable) | Hostel available: Rs. 95,000-160,000/semester"
                ))

# ========================================
# SCRAPE DEADLINES
# ========================================
print("\nScraping Deadlines...")
deadlines = []
tables = soup.find('div',id="collapseTwo").find('table',class_="semester-breakdown w-100")
rows=tables.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    if len(cols) >= 2:
        title = cols[0].get_text(strip=True)
        date = cols[1].get_text(strip=True)
        
        if title and date:
            deadlines.append(EmbeddedDeadline(title=title, deadline_date=date))
            print(f"   • {title}: {date}")



# ========================================
# SCRAPE ELIGIBILITY
# ========================================
print("\nScraping Eligibility Criteria...")
eligibility_notes = []
criteria_heading = soup.find(string=re.compile("Eligibility Criteria", re.I))
if criteria_heading:
    container = criteria_heading.find_parent()
    ul = container.find_next_sibling(lambda x: x.name in ["ul", "ol"] or x.find("li"))
    if ul:
        for li in ul.find_all("li"):
            text = li.get_text(strip=True)
            if len(text) > 10:
                eligibility_notes.append(text)

print(f"   → Found {len(eligibility_notes)} eligibility points")

# ========================================
# SCRAPE SCHOLARSHIPS
# ========================================
print("\nScraping Scholarships...")
scholarships = []
data = soup.find('div', id="collapseFour").find('ul', class_="list-style-num")
li = data.find_all('li')
for l in li:
    text = l.get_text(strip=True)
    scholarships.append(Scholarship(name=text, type="need-based", link="https://pifd.edu.pk"))

print(f"   → Found {len(scholarships)} scholarships")

# ========================================
# SAVE TO DATABASE
# ========================================
print("\nSaving to Database...")
pifd = University(
    name="PIFD",
    full_name="Pakistan Institute of Fashion and Design",
    city="Lahore",
    email="info@pifd.edu.pk",
    website="https://pifd.edu.pk",
    admission_link=url,
    programs=programs,
    scholarships=scholarships,
    deadlines=deadlines[:20],
    notes=f"Premier fashion and design institute. Entry test and interview required. First year total fee: Rs. {first_sem + second_sem:,}"
)

standalone_deadlines = []
for d in deadlines:
    deadline_obj = Deadline(
        university_name="PIFD",
        title=d.title,
        deadline_date=d.deadline_date,
        url="https://pifd.edu.pk/admission.html"
    )
    standalone_deadlines.append(deadline_obj)

def save_to_database():
    db = get_db()
    db.universities.delete_many({"name": "PIFD"})
    db.deadlines.delete_many({"university_name": "Pakistan Institute of Fashion and Design"})
    db.universities.insert_one(pifd.dict())
    db.deadlines.insert_many([d.dict() for d in standalone_deadlines])

if __name__ == "__main__":
    save_to_database()
    print("PIFD data saved to database.")





'''
<div id="collapseTwo" class="collapse show" aria-labelledby="headingOne" data-parent="#accordionExample" style="">
                    <div class="card-body page-section">
                        <div class="text-container">
                            <table class="semester-breakdown w-100">
                            <tbody>
                                <tr class="semester-h-col">
                                <th width="622" scope="col"><div align="center">Schedules</div></th>
                                <th width="306" scope="col"><div align="center">Dates</div></th>
                              </tr>
                              <tr class="semester-text">
                                <td>Advertisement</td>
                                <td> <div align=""><strong> 15<sup>th</sup>, 22<sup>nd</sup> June, &amp;  13<sup>th</sup> July, 2025</strong></div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Admissions Open</td>
                                <td><div align=""><strong>16<sup>th</sup> June, 2025</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Last Date For Submission of Applications</td>
                                <td><div align=""><strong>16<sup>th</sup> July, 2025</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Admission Entry / Aptitude Test:
                                    [Lahore, karachi Campus, Islamabad Campus, Peshawar, Quetta and Skardu Campus]</td>
                                
                                <td><div align=""><strong>20<sup>th</sup> July, 2025 at 10:00 AM</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Display of Merit List for Interviews</td>
                                <td><div align=""><strong>22<sup>nd</sup> July, 2025 (Evening)</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Interviews</td>
                                <td><div align=""><strong>24<sup>th</sup>, 25<sup>th</sup>, 26<sup>th</sup>, 28<sup>th</sup>&amp; 29<sup>th</sup>  July, 2025 </strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Display of First Merit List</td>
                                <td><div align=""><strong>30<sup>th</sup> July, 2025</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Last Date for submission of Dues</td>
                                <td><div align=""><strong>08<sup>th</sup> August, 2025</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Display of Second Merit List</td>
                                <td><div align=""><strong>08<sup>th</sup> August, 2025 (Evening)</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Last Date for submission of Dues</td>
                                <td><div align=""><strong>13<sup>th</sup> August, 2025</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Orientation</td>
                                <td><div align=""><strong>18<sup>th</sup> August, 2025</strong> </div></td>
                              </tr>
                              <tr class="semester-text">
                                <td>Commencement of Classes</td>
                                <td><div align=""><strong>18<sup>th</sup> August, 2025</strong> </div></td>
                              </tr>
                            
                            <!-- <tr class="semester-text">
                             <td colspan="2">
                                <table>
                                    <tbody>
                                        <tr class="semester-h-col">
                                            <th width="622" scope="col"><div align="center">Department Name</div></th>
                                            <th width="306" scope="col"><div align="center">Interviews</div></th>
                                            <th width="306" scope="col"><div align="center">1st Merit List</div></th>
                                            <th width="306" scope="col"><div align="center">Last Date for submission of Dues (1st Merit List)</div></th>
                                            <th width="306" scope="col"><div align="center">2nd Merit List</div></th>
                                            <th width="306" scope="col"><div align="center">Last Date for submission of Dues (2nd Merit List)</div></th>
                                        </tr>
                                        <tr>
                                            <td>
                                                Fashion Design
                                            </td>
                                            <td>
                                                <strong>8<sup>th</sup> August, 2024 </strong>
                                            </td>
                                            <td rowspan="3" style="vertical-align: middle;">
                                                <strong>12<sup>th</sup> August, 2024 </strong>
                                            </td>
                                            <td rowspan="3" style="vertical-align: middle;">
                                                <strong>16<sup>th</sup> August, 2024 </strong>
                                            </td>
                                            <td rowspan="3" style="vertical-align: middle;">
                                                <strong>16<sup>th</sup> August, 2024(Evening) </strong>
                                            </td>
                                            <td rowspan="3" style="vertical-align: middle;">
                                                <strong>22<sup>nd</sup> August, 2024 </strong>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Textile Design
                                            </td>
                                            <td>
                                                <strong>9<sup>th</sup> August, 2024 </strong>
                                            </td>
                                
                                            
                                        </tr>
                                        <tr>
                                            <td>
                                                Fashion Marketing and Merchandising
                                            </td>
                                            <td>
                                                <strong>10<sup>th</sup> August, 2024 </strong>
                                            </td>
                                       
                                           
                                        </tr>
                                        <tr>
                                            <td>
                                                Leather Accessories and Footwear
                                            </td>
                                            <td rowspan="2" style="vertical-align: middle;">
                                                <strong>12<sup>th</sup> August, 2024 </strong>
                                            </td>
                                            <td rowspan="5" style="vertical-align: middle;">
                                                <strong>16<sup>th</sup> August, 2024 </strong>
                                            </td>
                                            <td rowspan="5" style="vertical-align: middle;">
                                                <strong>23<sup>rd</sup> August, 2024 </strong>
                                            </td>
                                            <td rowspan="5" style="vertical-align: middle;">
                                                <strong>23<sup>rd</sup> August, 2024(Evening) </strong>
                                            </td>
                                            <td rowspan="5" style="vertical-align: middle;">
                                                <strong>27<sup>th</sup> August, 2024(Evening) </strong>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                Gems and Jewellery Design
                                            </td>                                 
                                            
                                        </tr>
                                        <tr>
                                            <td>
                                                Furniture Design and Manufacture
                                            </td>
                                            <td rowspan="3" style="vertical-align: middle;">
                                                <strong>13<sup>th</sup> August, 2024 </strong>
                                            </td>
                                            
                                        </tr>
                                        <tr>
                                            <td>
                                                Ceramic and Glass Design
                                            </td>
                             
                                            
                                        </tr>
                                        <tr>
                                            <td>
                                                BFA Visual Arts
                                            </td>
                             
                                            
                                        </tr>
           
                                    </tbody>
                                </table>

                             </td>
                            
                           </tr> -->
                              <!-- <tr class="semester-text">
                                <td>Orientation</td>
                                <td><div align=""><strong>15<sup>th</sup> September, 2024</strong> </div></td>
                              </tr> -->
                             
                            </tbody></table>
                            
                        </div>
                    </div>
                </div>
'''