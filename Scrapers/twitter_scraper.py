from Scrapers.scraper import Scraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys


class TwitterScraper(Scraper):
    _URL = r"https:twitter.com/home"

    def __init__(self, username=None, password=None):
        super(TwitterScraper, self).__init__()
        self.username = username
        self.password = password

    def wait_to_find(self, by_variable, attribute):
        """
        :param by_variable: variable to look for
        :param attribute: attribute of the variable
        Wait until the page is loaded to find the element required.
        Raise an exception in case the element is not found or if the program takes to much time
        """
        try:
            WebDriverWait(self.driver, 20).until(lambda x: x.find_element(by=by_variable, value=attribute))
        except (NoSuchElementException, TimeoutException):
            print(f'{by_variable} {attribute} have not been found in the web page.')
            self.driver.quit()

    def connection(self):
        """
        Open connection to a tweeter account.
        """
        super(TwitterScraper, self).connection()

        # wait until page has loaded
        self.wait_to_find('name', "username")

        # get element for email and post the username
        email = self.driver.find_element(by='name', value='username')
        if self.username is None:
            self.username = input("Please enter your Twitter e-mail address:")
        email.send_keys(self.username, Keys.ENTER)

        # wait for the page to actualise
        self.wait_to_find('name', "password")

        # get element for password and post the password
        password = self.driver.find_element(by='name', value='password')
        if self.password is None:
            self.password = input("Please enter your Twitter e-mail address:")
        password.send_keys(self.password, Keys.ENTER)


if __name__ == "__main__":
    scraper = TwitterScraper()
    scraper.connection()
