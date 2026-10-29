from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class HealingAgent:

    @staticmethod
    def find_element(driver, locator):

        by, value = locator

        print(f"[HEALER] Original locator failed: {locator}")

        if by == By.ID:

            healed_locator = (
                By.XPATH,
                f"//*[contains(@id,'{value}')]"
            )

        elif by == By.NAME:

            healed_locator = (
                By.XPATH,
                f"//*[contains(@name,'{value}')]"
            )

        else:

            raise NoSuchElementException(
                f"No healing strategy available for {by}"
            )

        print(
            f"[HEALER] Trying healed locator: {healed_locator}"
        )

        return driver.find_element(
            healed_locator[0],
            healed_locator[1]
        )