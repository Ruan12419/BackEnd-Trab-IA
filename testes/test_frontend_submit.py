from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def test_formulario_predicao():
    driver = webdriver.Chrome()
    driver.get("http://192.168.0.17:5000")

    driver.find_element(By.ID, "studentID").send_keys("101")
    driver.find_element(By.ID, "age").send_keys("16")
    driver.find_element(By.CSS_SELECTOR, 'input[name="gender"][value="0"]').click()
    driver.find_element(By.ID, "ethnicity").send_keys("0")
    driver.find_element(By.ID, "parentalEducation").send_keys("1")
    driver.find_element(By.ID, "studyTimeWeekly").send_keys("5")
    driver.find_element(By.ID, "absences").send_keys("3")
    driver.find_element(By.CSS_SELECTOR, 'input[name="tutoring"][value="1"]').click()
    driver.find_element(By.ID, "parentalSupport").send_keys("2")
    driver.find_element(By.CSS_SELECTOR, 'input[name="extracurricular"][value="0"]').click()
    driver.find_element(By.CSS_SELECTOR, 'input[name="sports"][value="1"]').click()
    driver.find_element(By.CSS_SELECTOR, 'input[name="music"][value="0"]').click()
    driver.find_element(By.CSS_SELECTOR, 'input[name="volunteering"][value="1"]').click()
    driver.find_element(By.ID, "gpa").send_keys("8.0")
    driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]').click()

    time.sleep(3)
    resultado = driver.find_element(By.ID, "p-resultado").text
    assert "Predição" in resultado

    driver.quit()
