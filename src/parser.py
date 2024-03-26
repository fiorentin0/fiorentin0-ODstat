import aiohttp
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup


async def login(username, password):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://rating.chgk.info/login") as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                csrf_token = soup.find('input', {'name': '_csrf_token'})['value']
                print(csrf_token)

        payload = {
            "_username": username,
            "_password": password,
            "_csrf_token": csrf_token,
            "go": "Вход"
        }

        async with session.post("https://rating.chgk.info/login", data=payload) as response:
            if response.status == 200:
                print("Вход выполнен успешно.")
            else:
                print(f"Ошибка входа. Статус код: {response.status}")

            cookies = session.cookie_jar.filter_cookies("https://rating.chgk.info/login")

            return cookies


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def top_10_tounaments(id, t):
    if t == 0:
        data = await fetch_data(f"https://rating.chgk.info/ajax/players/{id}/tournaments")
    else:
        data = await fetch_data(f"https://rating.chgk.info/ajax/teams/{id}/tournaments")

    sorted_data = sorted(data, key=lambda x: x['position']['delta'] if x['position']['delta'] is not None else 0, reverse=True)

    top_10_max_delta = sorted_data[:10]
    ans = []
    for item in top_10_max_delta:
        ans.append([item["tournament"]["name"], datetime.utcfromtimestamp(item['timestamp']).strftime('%d-%m-%Y'), item['position']['delta']])

    return ans


async def get_html_with_session(url, cookies):
    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get(url) as response:
            html = await response.text()
            return html


async def get_graph_command(id, t):
    if t == 0:
        data = await fetch_data(f"https://rating.chgk.info/ajax/players/{id}/tournaments")
    else:
        data = await fetch_data(f"https://rating.chgk.info/ajax/teams/{id}/tournaments")

    months = [datetime.fromtimestamp(entry["timestamp"]).strftime("%m-%Y") for entry in data]

    counts = {}
    for month in months:
        counts[month] = counts.get(month, 0) + 1

    unique_months = sorted(set(months), key=lambda x: (int(x.split('-')[1]), int(x.split('-')[0])))
    return unique_months, [counts[month] for month in unique_months]


async def get_name_of_group(id, cookies):
    data = await get_html_with_session(f"https://rating.chgk.info/teams/{id}", cookies)
    soup = BeautifulSoup(data, 'html.parser')
    return " ".join(str(soup.find('div', class_='team_details_info').h2.contents[1]["data-clipboard-text"]).split()[1:])


async def count_games(id):
    data = await fetch_data(f"https://rating.chgk.info/ajax/players/{id}/tournaments")

    team_id_counts = {}
    for item in data:
        team_id = item["team"]["id"]
        if team_id in team_id_counts:
            team_id_counts[team_id] += 1
        else:
            team_id_counts[team_id] = 1

    cookies = await login("luka.duvanov@gmail.com", "90AS90as")
    tuple_list = [(await get_name_of_group(team_id, cookies),count) for team_id, count in team_id_counts.items()]
    sorted_tuple_list = sorted(tuple_list, key=lambda x: x[1], reverse=True)

    return sorted_tuple_list


async def get_name_and_rating_of_group(id, cookies):
    data = await get_html_with_session(f"https://rating.chgk.info/teams/{id}", cookies)
    soup = BeautifulSoup(data, 'html.parser')
    name = " ".join(str(soup.find('div', class_='team_details_info').h2.contents[1]["data-clipboard-text"]).split()[1:])
    try:
        soup = BeautifulSoup(data, 'html.parser')
        rating = int(soup.find('table').find_all('tr')[1].find_all('td', recursive=False)[1].find('table', id='ratings').find_all('tr')[1].find_all('td', recursive=False)[1].find('span').text.strip())
    except:
        rating = 0
    return name, rating


async def rating_of_commands(id):
    data = await fetch_data(f"https://rating.chgk.info/ajax/players/{id}/tournaments")

    cookies = await login("luka.duvanov@gmail.com", "90AS90as")
    team_ids = list(set([item["team"]["id"] for item in data]))
    teams = [await get_name_and_rating_of_group(i, cookies) for i in team_ids]
    return sorted(teams, key=lambda x: x[1], reverse=True)


async def main():
    # print(await rating_of_commands(41351))
    pass
    # print(await count_games(9260))
    # print(await count_games(30270))
    # data = await login("luka.duvanov@gmail.com", "90AS90as")
    # print(data)
    # data = await fetch_data("https://rating.chgk.info/ajax/teams/49804/tournaments")
    # print(data)

if __name__ == "__main__":
    asyncio.run(main())