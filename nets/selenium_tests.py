from selenium import selenium
import unittest, time, re

class selenium_tests(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_selenium_tests(self):
        sel = self.selenium
        sel.open("/nets/netinfo/")
        for i in range(60):
            try:
                if sel.is_element_present("link=5"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("link=5")
        sel.click("link=2")
        sel.click("node_shortest_path_button")
        sel.wait_for_page_to_load("3000")
        for i in range(60):
            try:
                if sel.is_element_present("link=5"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("text-decoration: none; font-size: 19px; font-family: Times New Roman; color: rgb(0, 255, 0); position: absolute; text-align: center; left: 224px; top: 212px; width: 24px;", sel.get_attribute("link=5@style"))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
