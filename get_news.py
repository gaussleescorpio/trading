from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os, sys
import time
import pandas as pd
from datetime import datetime
from datetime import timedelta


class NewsFetcher(object):
    def __init__(self):
        sys.path.append('C:\\Users\\gauss\\Downloads\\chromedriver_win32')
        self.driver = webdriver.Chrome('C:\\Users\\gauss\\Downloads\\chromedriver_win32\\chromedriver.exe')
        try:
            self.driver.get("http://www.investing.com/economic-calendar/")
        except Exception as e:
            print "Error:cannot open website %s" % str(e)
        self.data = pd.DataFrame(columns=["time","equity","num_of_bulls","event_content", "actual_num", "forecast_num", "prev_num"])

    def select_european_time_zone(self):
        #select the right time zone
        self.driver.execute_script("window.scrollTo(0, 500);")
        time_zone_dropdown = self.driver.find_element_by_xpath('//*[@id="economicCurrentTime"]')
        time_zone_dropdown.click()
        time.sleep(1)
        sel_time_zone_action = ActionChains(self.driver)
        time_zone_sel = self.driver.find_element_by_xpath('//*[@id="economicCurrentTimePop"]')
        Central_europe = time_zone_sel.find_element_by_xpath('//*[@id="liTz16"]')
        sel_time_zone_action.move_to_element(Central_europe)
        sel_time_zone_action.click()
        sel_time_zone_action.perform()
        time.sleep(0.5)

    def select_data_from_time(self, start_date, end_date):
        data_sel_btn = self.driver.find_element_by_xpath('//*[@id="datePickerToggleBtn"]')
        data_sel_btn.click()
        # find the start_date input and fill in the wanted date
        date_fill_start = self.driver.find_element_by_xpath('//*[@id="startDate"]')
        date_fill_start.click()
        date_fill_start.clear()
        date_fill_start.send_keys(start_date)
        date_fill_end = self.driver.find_element_by_xpath('//*[@id="endDate"]')
        date_fill_end.click()
        date_fill_end.clear()
        date_fill_end.send_keys(end_date)
        time.sleep(0.5)
        # click the apply button to get all the data
        apply_btn = self.driver.find_element_by_xpath('//*[@id="applyBtn"]')
        apply_btn.click()
        time.sleep(0.5)

    def get_news_data(self):
        event_data = self.driver.find_element_by_xpath('//*[@id="economicCalendarData"]/tbody')
        items = event_data.find_elements_by_class_name('js-event-item')
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
            for i in range(0, 3):
                bulls_1 = bulls_num_elmnt.find_element_by_css_selector('i:nth-child(%s)'
                                                                       % str(i + 1))
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
            self.data.loc[count] = [event_time,currency_name_elmnt.text ,num_of_bulls, event_content_elmnt.text,
                               actual_value_elmnt.text,
                               forecast_value_elmnt.text, prev_value_elmnt.text]
            count += 1


if __name__ == "__main__":
    news_handler = NewsFetcher()
    news_handler.select_european_time_zone()
    date = (datetime.now()+timedelta(days=1)).strftime("%m/%d/%Y")
    news_handler.select_data_from_time(start_date=date, end_date=date)
    news_handler.get_news_data()
    print news_handler.data