import logging,unittest,time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Constants import NavbarMenu,AccountDetails,LoginDetails,CourseDetails
from NavBarSwitch import NavBar
from selenium.webdriver.common.alert import Alert 
from datetime import date, datetime


class StudentTests(unittest.TestCase):

    def setUp(self):
        # This method will be called before each test case
        # Perform any necessary setup here, such as refreshing the driver
        self.reset_state()

    def __init__(self,driver:WebDriver) -> None:
        self.driver=driver

    @classmethod
    def run_tests(self,driver):
        NavBar.go_to_navbar(driver=driver,navbar_item=NavbarMenu.STUDENTS)
        driver.maximize_window()
        self.accounts = AccountDetails
        self.login = LoginDetails
        self.course = CourseDetails


    """ XPATH of Student Class """

    CREATE_ACCOUNT = "//a[text()='Create Account']"
    LOGIN_BUTTON = "//a[text()='Login Now']"
    LOGOUT = "//a[text()='Logout']"
    LOGOUT_MSG = "//h2[contains(text(),'Logged Out Successfully')]"
    FIRST_NAME_PATH = "//input[@id='id_first_name']"
    LAST_NAME_PATH = "//input[@id='id_last_name']"
    CONTACT_PATH = "//input[@id='id_mobile']"
    ADDRESS_PATH = "//input[@id='id_address']"
    SIGNUP_USERNAME = "//input[@id='id_username']"
    SIGNUP_PASSWORD = "//input[@id='id_password']"
    LOGIN_USERNAME = "//input[@id='username']"
    PASSWORD_PATH = "//input[@id='password']"
    EMAIL_PATH = "//input[@id='id_email']"
    ORG_DROPDOWN = "//select[@id='id_organizationID']"
    ORGANIZATION_NAME= ORG_DROPDOWN + "//option[text()='Techno']"
    SIGNUP_PAGE_TITLE = "//div[text()='Student Signup Form']"
    SUBMIT_FORM = "//button[text()='Sign Up']"
    STUDENT_LOGIN_TITLE= "//div[text()='Student Login Panel']"
    LOGIN = "//input[@value='Login']"
    MANAGE_PROFILE = "//span[text()='Manage Profile']"
    UPDATE_BUTTON = "//input[@value='Update']"
    MANAGE_COURSES = "//span[text()='Manage Courses']"
    VIEW_COURSES = "//h6[contains(text(),'View Courses ')]"
    ACCESS_CODE_SELECTED_COURSE = "//tr//td[1][contains(text(),'{}')]/following-sibling::td[4]/span"
    EXAMINATION = "//span[text()='Examination']"
    MY_MARKS = "//span[text()='My Marks']"
    EXAM_ATTEND = "//tr//td[1][contains(text(),'{}')]/following-sibling::td[2]/a"
    EXAM_ACCESS_CODE_FIELD = "//input[@id='course_access_id']"
    START_EXAM = "//button[text()='Start Exam']"
    ACCESS_CODE_COPY ="//img[@alt='Copy']"
    EXAM_TITLE = "//h2[text()='Course: {}']"
    OPTION_CHECKBOX = "//div[@class='form-check mx-4'][1]//input"
    CLEAR_BUTTON = "//button[text()='Clear']"
    SAVE_BUTTON= "//a[text()='Save']"
    NEXT_BUTTON ="//a[text()='Next']"
    SUBMIT_ANSWER = "//input[@value='Submit Answers']"
    COURSE_MARKS = "//tr//td[1][contains(text(),'{}')]/following-sibling::td[1]/a"
    EXAM_DATE = "//tr//td[1][contains(text(),'{}')]/following-sibling::td[@class='exam_date']"

    """ Common function """

    def wait_for_visibility(self,element):
        return WebDriverWait(self.driver,10).until(EC.visibility_of_element_located((By.XPATH, element)))
        
    def wait_and_click(self,inputPath):
        path= self.wait_for_visibility(inputPath)
        path.click()

    def fill_input_box(self,inputPath,value:str):
        input_box = self.wait_for_visibility(inputPath)
        input_box.click()
        input_box.clear()
        input_box.send_keys(value)
        time.sleep(1)
        print("Details Filled SuccessFuly")

    def dropdown_select(self,inputPath,orgPath):

        self.driver.execute_script("window.scrollBy(0, 500);")
        dropdown_button = self.wait_for_visibility(inputPath)
        self.driver.execute_script("window.scrollBy(0, 500);")
        dropdown_button.click()
        # dynamic_xpath = orgPath.format(org)
        print("After selecting org")
        dropdown_item = self.wait_for_visibility(orgPath)
        dropdown_item.click()
        print("Dropdown Item selected Successfully")

    def profile_change(self,profile_name,username,pwd):
        logout = self.wait_for_visibility(self.LOGOUT)
        logout.click()
        WebDriverWait(self.driver,10).until(EC.visibility_of_element_located((By.XPATH,self.LOGOUT_MSG)))
        time.sleep(2)
        NavBar.go_to_navbar(driver=self.driver,navbar_item=profile_name)
        loginButton= self.wait_for_visibility(self.LOGIN_BUTTON)
        loginButton.click()
        # Login for Respective field to switch like Teacher,Org ,Student etc.
        self.fill_input_box(self.LOGIN_USERNAME, username)
        self.fill_input_box(self.PASSWORD_PATH, pwd)
        login = self.wait_for_visibility(self.LOGIN)
        login.click()
        time.sleep(2)

    """ Test cases"""

    def test_a1_create_account(self):
        print("DEBUG: test_a1_create_account")
        create_account= self.wait_for_visibility(self.CREATE_ACCOUNT)
        try:
            create_account.click()
            self.wait_for_visibility(self.SIGNUP_PAGE_TITLE)

            # Fill details for Creating Account.
            # First Name, Last Name , Address, Username etc.
            self.fill_input_box(self.FIRST_NAME_PATH, self.accounts.STUDENT_FIRST_NAME.value)
            self.fill_input_box(self.LAST_NAME_PATH, self.accounts.STUDENT_LAST_NAME.value)
            self.fill_input_box(self.CONTACT_PATH, self.accounts.CONTACT.value)
            self.fill_input_box(self.ADDRESS_PATH, self.accounts.ADDRESS.value)
            self.fill_input_box(self.SIGNUP_USERNAME, self.accounts.STUDENT_USERNAME.value)
            self.fill_input_box(self.SIGNUP_PASSWORD, self.accounts.STUDENT_PASSWORD.value)
            self.fill_input_box(self.EMAIL_PATH, self.accounts.EMAIL.value)
            # Selecting Required Org from dropdown
            self.dropdown_select(self.ORG_DROPDOWN,self.ORGANIZATION_NAME)
            # Submit to signup
            submit_button = self.wait_for_visibility(self.SUBMIT_FORM)
            submit_button.click()

            # Assert with LoginUp that Student is Signed-Up or not
            self.fill_input_box(self.LOGIN_USERNAME, self.accounts.STUDENT_USERNAME.value)
            self.fill_input_box(self.PASSWORD_PATH, self.accounts.STUDENT_PASSWORD.value)
            login = self.wait_for_visibility(self.LOGIN)
            login.click()
            time.sleep(2)

            # Logout to Home-Page again
            logout = self.wait_for_visibility(self.LOGOUT)
            logout.click()
            WebDriverWait(self.driver,10).until(EC.visibility_of_element_located((By.XPATH,self.LOGOUT_MSG)))
            time.sleep(2)
            print("SUCCESS: test_a1_create_account")

        except Exception as e:
            raise AssertionError("FAILED: ",e)
        
    def test_a2_login_account(self):
        print("DEBUG: test_a2_login_account")
        """ Login with already Saved User Id in DB"""

        NavBar.go_to_navbar(driver=self.driver,navbar_item=NavbarMenu.STUDENTS)
        loginButton = self.wait_for_visibility(self.LOGIN_BUTTON)
        loginButton.click()
        self.wait_for_visibility(self.STUDENT_LOGIN_TITLE)
        try:
            self.fill_input_box(self.LOGIN_USERNAME, self.login.STUDENT_USERNAME.value)
            self.fill_input_box(self.PASSWORD_PATH, self.login.STUDENT_PASSWORD.value)
            login = self.wait_for_visibility(self.LOGIN)
            login.click()
            time.sleep(2)
            print("SUCCESS: test_a2_login_account")
        except Exception as e:
            raise AssertionError("FAILED: ",e)

    def test_a3_student_manage_profile(self):
        print("DEBUG: test_a3_student_manage_profile")
        try:
            manage_profile = self.wait_for_visibility(self.MANAGE_PROFILE)
            manage_profile.click()
            self.fill_input_box(self.FIRST_NAME_PATH,self.accounts.NEW_FIRST_NAME.value)
            self.driver.execute_script("window.scrollBy(0, 700);")
            update_button=self.wait_for_visibility(self.UPDATE_BUTTON)
            update_button.click()
            time.sleep(2)

            # Assert for First Name changed
            changed_name =self.wait_for_visibility("//h4")
            expected_text = changed_name.text
            actual_text = self.accounts.NEW_FIRST_NAME.value
            if actual_text == expected_text: 
                assert True
                print("Profile Updated Successfully")
            else:
                assert False
            print("SUCCESS: test_a3_student_manage_profile")
        except Exception as e:
            raise AssertionError("FAILED: ",e)
        
    """ Note: This test case will work properly if Time & date exacty set accordingly to day of giving exam"""
    # def test_a4_student_exam_entry(self):
    #     print("DEBUG: test_a4_student_exam_attend")
    #     try:
    #        # Nvaigate to Teaher Profile
    #        # Select Access Code for Desires exam selected 
    #        # Navigate back to Student profile to start the exam
    #         self.profile_change(NavbarMenu.TEACHER,self.login.TEACHER_USERNAME.value,self.login.TEACHER_PASSWORD.value)
    #         self.wait_and_click(self.MANAGE_COURSES)
    #         self.wait_and_click(self.VIEW_COURSES)
    #         time.sleep(2)
    #         access_code = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, self.ACCESS_CODE_SELECTED_COURSE.format(self.course.COURSE_NAME.value))))
    #         access_code_value = access_code.text
    #         print("Access Code is Copied")

    #         # # Navigate to Student Profile again to  start exam
    #         self.profile_change(NavbarMenu.STUDENTS,self.login.STUDENT_USERNAME.value,self.login.STUDENT_PASSWORD.value)

    #         self.wait_and_click(self.EXAMINATION)
    #         self.wait_and_click(self.EXAM_ATTEND.format(self.course.COURSE_NAME.value))
    #         time.sleep(2)
    #         self.driver.execute_script("window.scrollBy(0, 500);")
    #         time.sleep(2)
    #         self.fill_input_box(self.EXAM_ACCESS_CODE_FIELD,access_code_value)
    #         self.wait_and_click(self.START_EXAM)

    #         """ Note : At at this stage plz Manually 'Click Allow' Notification Pop up to proceed with exam"""
    #         """ Will Look for suitable selenium method for pop-ups acceptance"""

    #         self.wait_for_visibility(self.EXAM_TITLE.format(self.course.COURSE_NAME.value))

    #         print("SUCCESS: test_a4_student_exam_attend")
    #     except Exception as e:
    #         raise AssertionError("FAILED: ",e)
        
    def test_a5_student_exam_attend(self):
        print("DEBUG: test_a5_student_exam_attend")
        try:
            
            # Check for Clear
            self.wait_and_click(self.OPTION_CHECKBOX)  # Choose Option
            print("Checbox clicked successfully")
            time.sleep(2)
            self.wait_and_click(self.CLEAR_BUTTON)
            print("Clear Button clicked successfully")
            time.sleep(2)

            # Check for Save
            self.wait_and_click(self.OPTION_CHECKBOX)
            self.wait_and_click(self.SAVE_BUTTON)
            print("Save Button clicked successfully")
            time.sleep(3)

            #Check for Next,if available then perform ,else ontinue with submiiting answers
            """ Note: Its currently working for only 2-set of questions"""
            try:
                self.wait_for_visibility(self.NEXT_BUTTON)
                self.wait_and_click(self.NEXT_BUTTON)
                time.sleep(3)
                print("Next Button clicked successfully")
                self.wait_and_click(self.OPTION_CHECKBOX)
            except:
                self.wait_for_visibility(self.SUBMIT_ANSWER)
                print("No more question. Time to Submit")
            # Check for Submit
            
            self.wait_and_click(self.SUBMIT_ANSWER)
            time.sleep(3)
            print("SUCCESS: test_a5_student_exam_attend")
        except Exception as e:
            raise AssertionError("FAILED: ",e)
        
    def test_a6_student_marks_after_exam(self):
        print("DEBUG: test_a6_student_marks_exam_attended")
        try:
            self.wait_and_click(self.MY_MARKS)
            self.wait_and_click(self.COURSE_MARKS.format(self.course.COURSE_NAME.value))
            time.sleep(3)
            exam_marks = self.wait_for_visibility(self.EXAM_DATE.format(self.course.COURSE_NAME.value))
            exam_date = exam_marks.text
            # print(exam_date)
            today = date.today()
            actual_date = today.strftime("%B %d, %Y")

            date_format = "%A, %B %d, %Y at %I:%M %p"
            exam_date = datetime.strptime(exam_date, date_format)
            exam_date_required = exam_date.strftime("%B %d, %Y")

            if exam_date_required == actual_date:
                print("Exam marks found on the Date given")
            else:
                print("Not Found exam marks for Day expected")
            
            print("SUCCESS: test_a6_student_marks_exam_attended")
        except Exception as e:
            raise AssertionError("FAILED: ",e)