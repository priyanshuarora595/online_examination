
import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Constants import NavbarMenu
from NavBarSwitch import NavBar
import time

class TeacherTests:
    
    def __init__(self,driver) -> None:
        self.driver=driver

    @classmethod
    def run_tests(self,driver):
        self.logger= logging.getLogger(name=__name__)
        NavBar.go_to_navbar(self,driver=driver,navbar_item=NavbarMenu.STUDENTS)

    def test_a1_login(self):
        print("TEACHERS PAGE")
        
