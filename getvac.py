import requests, json, time
import click
import pandas as pd


def add_params(url, **kwargs):
    for key, value in kwargs.items():
        url += f'{key}={str(value)}&'
    return url

@click.command()
@click.option('--texts', '-t')
@click.option('--mode', '-m')
@click.option('--filepath', '-p')
def main(texts, mode, filepath=r'.\vacancies.csv'):
    URL = 'https://api.hh.ru/vacancies?clusters=true&enable_snippets=true&st=searchVacancy&only_with_salary=true&per_page=100&area=1&'
    experiences = ['noExperience', 'between1And3', 'between3And6', 'moreThan6']
    texts = texts.lower().split('|')

    vacancies = []
    for text in texts:
        for experience in experiences:
            url = add_params(URL, text=text,
                            experience=experience)
            html_text = requests.get(url).text
            time.sleep(0.1)
            
            data = json.loads(html_text)
            pages = data['pages']
            for page in range(pages):
                url = add_params(URL, text=text,
                                experience=experience,
                                page=page)
                html_text = requests.get(url).text
                data = json.loads(html_text)
                for vacancy in data['items']:
                    if vacancy['address'] != None:
                        lat = vacancy['address']['lat']
                        lon = vacancy['address']['lng']
                    else:
                        lat = None
                        lon = None
                        
                    vacancy_info = {'Id':  vacancy['id'],
                                    'Text': text,
                                    'TitleName': vacancy['name'].lower(),
                                    'PublishedAt': vacancy['published_at'].split('T')[0],
                                    'Experience': experience,
                                    'Currency': vacancy['salary']['currency'],
                                    'SalaryFrom': vacancy['salary']['from'],
                                    'SalaryTo': vacancy['salary']['to'],
                                    'Schedule': vacancy['schedule']['id'],
                                    'Url': vacancy['alternate_url'],
                                    'Employer': vacancy['employer']['name'],
                                    'Lat': lat,
                                    'Lon': lon,
                                    }
                    vacancies.append(vacancy_info)
                    
                time.sleep(0.1)
            
    df = pd.DataFrame(vacancies)
    if mode == 'w':
        header = True
    else:
        header = False
    df.to_csv(filepath, sep=';', mode=mode, index=False, header=header)
    
if __name__ ==  "__main__":
    main()
