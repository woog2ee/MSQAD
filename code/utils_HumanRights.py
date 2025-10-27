from selenium.webdriver.common.by import By
import re


topic_num_dic = {"Arms": 9681,
                 "Children's Rights": 9683,
                 "Crisis and Conflict": 9861,
                 "Disability Rights": 9685,
                 "Economic Justice and Rights": 9682,
                 "Environment and Human Rights": 9686,
                 "Free Speech": 9688,
                 "Health": 9689,
                 "LGBT Rights": 9691,
                 "Refugees and Migrants": 9693,
                 "Rights of Older People": 9813,
                 "International Justice": 9690,
                 "Technology and Rights": 9762,
                 "Terrorism / Counterterrorism": 9684,
                 "Torture": 9696,
                 "United Nations": 9697,
                 "Women's Rights": 9698}

topic_maxpage_dic = {"Arms": 79,
                     "Children's Rights": 193,
                     "Crisis and Conflict": 24,
                     "Disability Rights": 51,
                     "Economic Justice and Rights": 87,
                     "Environment and Human Rights": 45,
                     "Free Speech": 240,
                     "Health": 120,
                     "LGBT Rights": 119,
                     "Refugees and Migrants": 156,
                     "Rights of Older People": 9,
                     "International Justice": 152,
                     "Technology and Rights": 62,
                     "Terrorism / Counterterrorism": 98,
                     "Torture": 69,
                     "United Nations": 176,
                     "Women's Rights": 195}


def get_url(driver, article_num):
    try:
        url = driver.find_element(By.XPATH,
          f'//*[@id="block-hrw-design-content"]/div/div/div[1]/div/div[1]/div/div/div/div/div[{article_num}]/article/div[1]/h3/a').get_attribute('href')
        case = False
    except:
        # for an only one article per page
        if article_num != 1:
            return None, False
        
        url = driver.find_element(By.XPATH,
           '//*[@id="block-hrw-design-content"]/div/div/div[1]/div/div[1]/div/div/div/div/div/article/div/h3/a').get_attribute('href')
        case = True
    return url, case


def get_category(driver, article_num, case):
    try:
        if not case:
            category = driver.find_element(By.XPATH,
               f'/html/body/div[1]/div[1]/main/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div[{article_num}]/article/div[1]/div/span[2]').text
        else:
            # for an only one article per page
            category = driver.find_element(By.XPATH,
               '/html/body/div[1]/div[1]/main/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div/article/div/div/span[2]').text
    except:
        category = ''
    return category


def get_title(driver, article_num, case):
    try:
        if not case:
            title = driver.find_element(By.XPATH,
               f'/html/body/div[1]/div[1]/main/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div[{article_num}]/article/div[1]/h3/a/span').text
        else:
            # for an only one article per page
            title = driver.find_element(By.XPATH,
               '/html/body/div[1]/div[1]/main/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div/article/div/h3/a/span').text
    except:
        title = ''
    return title


def get_subtitle(driver, article_num, case):
    try:
        if not case:
            subtitle = driver.find_element(By.XPATH,
               f'/html/body/div[1]/div[1]/main/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div[{article_num}]/article/div[1]/p').text
        else:
            # for an only one article per page
            subtitle = driver.find_element(By.XPATH,
               '/html/body/div[1]/div[1]/main/div[2]/div[2]/div/div/div[1]/div/div[1]/div/div/div/div/div/article/div/p').text
    except:
        subtitle = ''
    return subtitle
    

# def get_title(driver):
#     try:
#         title = driver.find_element(By.XPATH,
#             '/html/body/div[1]/div[1]/main/div[2]/div[2]/article/div/div[1]/div/div[1]/header/div[2]/h1').text
#     except:  # for 'report'
#         try:
#             title = driver.find_element(By.XPATH,
#                 '/html/body/div[1]/div[1]/main/div[2]/div[2]/article/div/div[1]/div/div[1]/header/div/div[1]/div/div/h1')
#         except:
#             title = ''
#     return title


# def get_subtitle(driver):
#     try:
#         subtitle = driver.find_element(By.XPATH,
#             '/html/body/div[1]/div[1]/main/div[2]/div[2]/article/div/div[1]/div/div[1]/header/div[2]/p').text
#     except:  # for 'report'
#         try:
#             subtitle = driver.find_element(By.XPATH,
#                 '/html/body/div[1]/div[1]/main/div[2]/div[2]/article/div/div[1]/div/div[1]/header/div/div[1]/div/div/p')
#         except:
#             subtitle = ''
#     return subtitle


def get_first_paragraph(driver):
    try:
        first_paragraph = driver.find_element(By.XPATH,
            '//*[@id="block-hrw-design-content"]/article/div/div[2]/div/div[1]/div/div[1]/div/div/p[1]').text
    except:  # for 'report'
        try:
            first_paragraph = driver.find_element(By.XPATH,
                '/html/body/div[1]/div[1]/main/div[2]/div[2]/article/div/div[2]/div/div[1]/div/div/p[2]')
        except:
            first_paragraph = ''
    return first_paragraph
    
    
def url2date(url):
    info = re.findall(r'[0-9]{4}/[0-9]{2}/[0-9]{2}', url)
    try: return info[0]
    except: return 'No_Date'