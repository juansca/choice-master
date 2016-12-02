import os
from selenium import webdriver

DRIVERS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', 'drivers'))
def before_all(context):
    msg = os.path.join(DRIVERS_PATH, 'chromedriver') + " doesn't exists"
    assert os.path.exists(os.path.join(DRIVERS_PATH, 'chromedriver')), msg
    context.browser = webdriver.Chrome(
        executable_path=os.path.join(DRIVERS_PATH, 'chromedriver')
    )

def after_all(context):
    context.browser.quit()
