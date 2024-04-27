from selenium import webdriver

class InitDriver:
    """ Set Up for Driver"""
    driver=None

    def __init__(self,driver):
        self.driver=driver

    def get_driver(cls):
        if not cls.driver:
            cls.set_driver()
        return cls.driver
    
    def openUrl(cls):
        if cls.driver:
            cls.driver.get("http://127.0.0.1:8000/")

    def set_driver():
        driver=webdriver.Chrome()
        return driver
    
    def tear_down(self):
        print("Student Page")
        self.driver.quit()

