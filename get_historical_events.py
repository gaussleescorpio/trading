"""
Tested on windows 8. not fully tested on Mac OS and Linux. Should work as well
"""


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os, sys
import time
import pandas as pd
print sys.path
sys.path.append('C:\\Users\\gauss\\Downloads\\chromedriver_win32')
driver = webdriver.Chrome('C:\\Users\\gauss\\Downloads\\chromedriver_win32\\chromedriver.exe')
try:
    driver.get("http://www.investing.com/economic-calendar/")
except Exception as e:
    print "Error:cannot open website %s" % str(e)

#select the right time zone
driver.execute_script("window.scrollTo(0, 500);")
time_zone_dropdown = driver.find_element_by_xpath('//*[@id="economicCurrentTime"]')
time_zone_dropdown.click()
time.sleep(1)
sel_time_zone_action = ActionChains(driver)
time_zone_sel = driver.find_element_by_xpath('//*[@id="economicCurrentTimePop"]')
Central_europe = time_zone_sel.find_element_by_xpath('//*[@id="liTz16"]')
sel_time_zone_action.move_to_element(Central_europe)
sel_time_zone_action.click()
sel_time_zone_action.perform()


time.sleep(1)
data_sel_btn = driver.find_element_by_xpath('//*[@id="datePickerToggleBtn"]')
data_sel_btn.click()
driver.implicitly_wait(1)

#find the start_date input and fill in the wanted date
date_fill = driver.find_element_by_xpath('//*[@id="startDate"]')
date_fill.click()
date_fill.clear()
date_fill.send_keys("01/10/2014")
time.sleep(1)
#click the apply button to get all the data
apply_btn = driver.find_element_by_xpath('//*[@id="applyBtn"]')
apply_btn.click()
time.sleep(1)



from datetime import datetime
from datetime import timedelta
while True:
    elements_on_page = driver.find_elements_by_class_name('theDay')
    timestamp_value = int( elements_on_page[-1].get_attribute('id').split('theDay')[1])
    cur_time = datetime.fromtimestamp(timestamp_value)
    print cur_time
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)
    time_now = datetime.utcnow()
    if cur_time >= datetime.utcnow()-timedelta(days=1, hours=time_now.hour,
                                               minutes=time_now.minute, seconds=time_now.second):
        break

event_data = driver.find_element_by_xpath('//*[@id="economicCalendarData"]/tbody')
items = event_data.find_elements_by_class_name('js-event-item')
data = pd.DataFrame(columns=["time","equity","num_of_bulls","event_content", "actual_num", "forecast_num", "prev_num"])
count = 0
for s in items:
    # eventRowId_315153 > td.left.flagCur.noWrap
    event_time = s.get_attribute('data-event-datetime')
    print event_time
    event_id = s.get_attribute('id')
    event_num = event_id.split('_')[1]
    currency_name_elmnt = s.find_element_by_css_selector('#%s > td.left.flagCur.noWrap' % event_id)
    print currency_name_elmnt.text
    bulls_num_elmnt = s.find_element_by_css_selector('#%s > td.left.textNum.sentiment.noWrap' % event_id)
    num_of_bulls = 0
    # eventRowId_315153 > td.left.textNum.sentiment.noWrap > i:nth-child(1)
    # eventRowId_315153 > td.left.textNum.sentiment.noWrap > i:nth-child(2)
    for i in range(0,3):
        bulls_1 = bulls_num_elmnt.find_element_by_css_selector('i:nth-child(%s)'
                                                               % str(i+1))
        class_content = bulls_1.get_attribute("class")
        if class_content == "grayFullBullishIcon":
            num_of_bulls += 1
    print "num of bulls: %d" % num_of_bulls
    event_content_elmnt = s.find_element_by_css_selector('#%s > td.left.event > a' % event_id)
    print event_content_elmnt.text
    # eventActual_315153
    actual_value_elmnt = s.find_element_by_css_selector('#eventActual_%s' % event_num)
    print "actual num:" + actual_value_elmnt.text
    # eventForecast_315153
    forecast_value_elmnt = s.find_element_by_css_selector('#eventForecast_%s' % event_num)
    print "forecast:" + forecast_value_elmnt.text
    prev_value_elmnt = s.find_element_by_css_selector('#eventPrevious_%s > span' % event_num)
    print "prev_value:" + prev_value_elmnt.text
    data.loc[count] = [event_time, currency_name_elmnt.text, num_of_bulls,event_content_elmnt.text, actual_value_elmnt.text,
                       forecast_value_elmnt.text, prev_value_elmnt.text]
    count += 1

data.to_csv("event_historical_data.csv")





