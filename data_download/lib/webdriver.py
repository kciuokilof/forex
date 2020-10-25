from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_user_agent_driver():
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agents = user_agent_rotator.get_user_agents()

    user_agent1 = user_agent_rotator.get_random_user_agent()
    options = Options()
    options.add_argument(f'—-headless')
    options.add_argument(f'—-no-sandbox')
    options.add_argument(f'—-disable-gpu')
    options.add_argument(f'—-window-size=1420,1080')
    options.add_argument(f'user-agent={user_agent1}')
    driver = webdriver.Chrome('../../data/chromedriver.exe', options=options)
    return driver