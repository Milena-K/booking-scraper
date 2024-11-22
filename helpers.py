from selenium.webdriver.common.by import By

def get_cards(driver, entries):
    property_cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="property-card"]')

    for card in property_cards:
        name_elem = card.find_element(By.CSS_SELECTOR, 'div[data-testid="title"]')
        link_elem = card.find_element(By.CSS_SELECTOR, 'a[data-testid="title-link"]')
        price_elem = card.find_element(By.CSS_SELECTOR, 'span[data-testid="price-and-discounted-price"]')
        location_elem = card.find_element(By.CSS_SELECTOR, 'span[data-testid="address"]')

        rating = 0
        try:
            rating_elem = card.find_element(By.CSS_SELECTOR, 'div[data-testid="review-score"]')
            rating = rating_elem.text
        except:
            pass

        # Retrieve text or attributes
        name = name_elem.text
        link = link_elem.get_attribute("href")
        price = price_elem.text
        location = location_elem.text
        location_property = [name, link, price, rating, location]

        location = location.lower()
        if location in entries:
            entries[location].append(location_property)
