from Constants import NavbarMenu
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

class NavBar:
    """ XPAATH for Students Page"""
    # STUDENT_MENUBAR_XPATH="//a[text()='Student']"
    # STUDENT_ENTRY= "//h1[text()='Hello Student,']"
    
    def __init__(self,driver):
        self.driver=driver

    def go_to_navbar(driver,navbar_item:NavbarMenu,timeout:int=20):
        """ Swtching of UI Navbar"""
        actions= ActionChains(driver=driver)
        if "STUDENTS" in navbar_item.name:
            studentBar= WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//a[text()='Student']")))
            actions.move_to_element(to_element=studentBar).perform()
            time.sleep(1)
            studentBar.click()
            WebDriverWait(driver,timeout).until(EC.visibility_of_element_located((By.XPATH,"//h1[contains(text(),'Hello Student')]")))
        elif "TEACHER" in navbar_item.name:
            teacherBar= WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//a[text()='Teacher']")))
            actions.move_to_element(to_element=teacherBar).perform()
            time.sleep(1)
            teacherBar.click()
            WebDriverWait(driver,timeout).until(EC.visibility_of_element_located((By.XPATH,"//h1[contains(text(),'Hello Teacher')]")))