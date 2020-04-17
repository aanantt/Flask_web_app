from flaskblog import sockett,app
if __name__ == '__main__':
    sockett.run(app, debug=True)
# from selenium import webdriver
# import time
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.action_chains import ActionChains
# # driver = webdriver.Firefox(executable_path="/home/anant/PycharmProjects/Flask/geckodriver")
#
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# import time
#
# # Replace below path with the absolute path
# # to chromedriver in your computer
# driver = webdriver.Firefox(executable_path="/home/anant/PycharmProjects/Flask/geckodriver")
#
# driver.get("https://web.whatsapp.com/")
# wait = WebDriverWait(driver, 600)
#
# # Replace 'Friend's Name' with the name of your friend
# # or the name of a group
# target = '"Meh"'
#
# # Replace the below string with your own message
# string = "Message sent using Python!!!"
#
# x_arg = '//span[contains(@title,' + target + ')]'
# group_title = wait.until(EC.presence_of_element_located((
# 	By.XPATH, x_arg)))
# group_title.click()
# inp_xpath = '//div[@class="input"][@dir="auto"][@data-tab="1"]'
# input_box = wait.until(EC.presence_of_element_located((
# 	By.XPATH, inp_xpath)))
# input_box.send_keys(string + Keys.ENTER)
#
#
#
#
# # action=ActionChains(driver)
# # action.move_to_element(driver.find_element_by_xpath("//div[@id='search-input']"))
# # action.click(driver.find_element_by_xpath("//div[@id='search-input']"))
# # action.send_keys("Donald Trump")
# # action.send_keys(Keys.ENTER)
# # action.perform()
# # wait.until(ec.presence_of_element_located((By.XPATH,"/html/body/div[3]/div[3]/div[4]/div/p[2]")))
# # url = "https://www.accuweather.com/en/in/delhi/202396/weather-forecast/202396"
