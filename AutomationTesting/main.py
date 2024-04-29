import threading
import time
from selenium import webdriver
from students import StudentTests
from teachers import TeacherTests
from Driver import InitDriver


ALL_THREADS_TEST = [
    StudentTests,
    #TeacherTests,
    #~ OrganizationTests
]

def run_tests(test_class):
    # Initialize the webdriver
    driver = webdriver.Chrome()
    init_obj = InitDriver(driver)  # Initialize driver setup
    init_obj.get_driver() # Run setup method from InitDriver
    init_obj.openUrl()

    try:
        # Initialized the test class instance
        test_instance = test_class(driver)
        # To run initial setup method
        test_instance.run_tests(driver)
        
        # Run the test cases
        test_methods = [getattr(test_instance, method_name) for method_name in dir(test_instance) if method_name.startswith('test_')]
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"Test case {test_method.__name__} failed: {str(e)}") 
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        threads = []
        for test_class in ALL_THREADS_TEST:
            thread = threading.Thread(target=run_tests, args=(test_class,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        raise AssertionError(e)
