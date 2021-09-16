from scrapy import Selector
import re
from .helpers import extract_integer, extract_number_with_two_decimals, mode_of_array


def get_sellers_rank(response):
    seller_rank_pattern = r'([0-9]{1,3}(?:,[0-9]{0,3})*)\s(?:in|en)\s([a-zA-Z]{3,})'
    best_seller_link_pattern = r'gp/bestsellers/'
    sellers_ranks = []
    conditions = [
        "@id='detail-bullets'",
        "@id='productDetailsTable'",
        "@id='descriptionAndDetails'",
        "@id='prodDetails'",
        "@id='prodDetails' and @class='a-section'",
        "@id='detailBullets_feature_div'"
    ]
    sel = Selector(response)
    for condition in conditions:
        prod_detail_elements = sel.xpath(f"//*[{condition}]")
        if prod_detail_elements:
            best_seller_link_elements = prod_detail_elements[0].xpath(
                './/span').get()
            if best_seller_link_elements:
                prod_detail = prod_detail_elements[0].get()
                prod_detail = prod_detail.replace("\n", " ")
                x = re.search(seller_rank_pattern, prod_detail)
                if x:
                    sellers_rank = extract_integer(x.group().replace(',', ''))
                    return sellers_rank


def get_product_prices_from_product_page(response):
    sel = Selector(response)
    main_prices = []
    shipping_prices = []
    # Main price
    main_price_element_ids = [
        "newBuyBoxPrice",
        "price_inside_buybox",
        "priceblock_dealprice",
        "priceblock_saleprice",
        "priceblock_ourprice",
        "price"
    ]
    for element_id in main_price_element_ids:
        element_text = ' '.join([s.strip() for s in sel.xpath(f"//*[@id='{element_id}']//text()").extract() if s.strip()])
        if element_text:
            element_text = element_text.replace("¥", "")
            element_text = element_text.replace("$", "")
            element_text = element_text.replace("TL", "")
            print(element_text)
            main_price = extract_number_with_two_decimals(element_text)
            if main_price is not None:
                main_prices += [main_price]
    # Shipping price
    shipping_price_element_ids = [
        "shippingMessageInsideBuyBox_feature_div",
        "dealprice_shippingmessage",
        "saleprice_shippingmessage",
        "ourprice_shippingmessage",
        "deliveryMessageMirId",
        "priceblock_ourprice_ifdmsg",
        "desktop_qualifiedBuyBox",
    ]
    for element_id in shipping_price_element_ids:
        element_text = ' '.join([s.strip() for s in sel.xpath(f"//*[@id='{element_id}']//text()").extract() if s.strip()])
        if element_text:
            element_text = element_text.replace(",", "")
            if re.search(r"free delivery|free shipping|free return", element_text, re.IGNORECASE):
                shipping_price = 0
            else:
                shipping_price = extract_number_with_two_decimals(element_text)
            if shipping_price is not None:
                shipping_prices += [shipping_price]
    # Take mode of both as actual prices
    main_price = mode_of_array(main_prices)
    shipping_price = mode_of_array(shipping_prices)
    if main_price is not None and shipping_price is not None:
        return [float(main_price), float(shipping_price)]
    else:
        total_price_element_ids = [
            "amazonGlobal_feature_div",
            "exports_desktop_qualifiedBuybox_tlc_feature_div"
        ]
        for element_id in total_price_element_ids:
            element = sel.xpath(f"//*[@id='{element_id}']/text()").get()
            element_text = element.replace(",", "")
            if '+' in element_text or not 'shipping' in element_text:
                # This is a scenario for shown only shipping price and not main price
                # That's why shouldn't be taken as total price
                element_text = element_text.replace("¥", "")
                element_text = element_text.replace("$", "")
                element_text = element_text.replace("TL", "")
                total_price = extract_number_with_two_decimals(element_text)
                return [total_price, 0]



def get_lowest_product_prices_from_tr_sellers_page(response):
    sel = Selector(response)
    # Main and Shipping prices for lowest seller
    pinned_offer_elements = sel.xpath("//*[@id='aod-sticky-pinned-offer']")
    other_offer_elements = sel.xpath("//*[@id='aod-offer']")
    offer_elements = pinned_offer_elements + other_offer_elements
    for offer_element in offer_elements:
        track_message_element = offer_element.xpath(".//*[@id='fast-track-message']")
        if not track_message_element:
            track_message_element = offer_element.xpath(".//*[@class='a-fixed-right-grid-col aod-padding-right-10 a-col-left']")
        if track_message_element:
            cannot_be_shipped_element = track_message_element.xpath(".//*[contains(., 'cannot be shipped') or @class='a-color-error']")
            if cannot_be_shipped_element:
                continue
            else:
                # Whole
                whole_price_text = offer_element.xpath(".//*[@class='a-price-whole']/text()").get()
                whole_price_text = whole_price_text.replace(".", "")
                whole_price_text = whole_price_text.replace("TL", "")
                whole_price_text = whole_price_text.replace(",", ".")
                price_whole_part = float(whole_price_text)
                # Fraction
                fraction_price_text = offer_element.xpath(".//*[@class='a-price-fraction']/text()").get().strip()
                if fraction_price_text:
                    price_fraction_part = float(fraction_price_text)
                else:
                    price_fraction_part = 0
                main_price = price_whole_part + (price_fraction_part/100)
                # Shipping
                shipping_price_element_texts_1 = offer_element.xpath(".//*[@id='dynamicDeliveryMessage' or contains(@class,'aod-delivery-promise')]//text()").extract()
                shipping_price_element_text_1 = ' '.join([s.strip() for s in shipping_price_element_texts_1 if s.strip()])
                shipping_price_element_texts_2 = offer_element.xpath(".//*[contains(@class, 'aod-ship-charge')]//text()").extract()
                shipping_price_element_text_2 = ' '.join([s.strip() for s in shipping_price_element_texts_2 if s.strip()])
                shipping_price_element_text = shipping_price_element_text_1 + shipping_price_element_text_2
                shipping_price_element_text = shipping_price_element_text.replace(".","")
                shipping_price_element_text = shipping_price_element_text.replace("TL","")
                shipping_price_element_text = shipping_price_element_text.replace(",",".")
                if re.search(r"kargo bedava", shipping_price_element_text, re.IGNORECASE):
                    shipping_price = 0
                else:
                    shipping_price = extract_number_with_two_decimals(shipping_price_element_text)
                if shipping_price is not None:
                    return [float(main_price), float(shipping_price)]


def cannot_be_shipped_from_us_product_page(response):
    sel = Selector(response)
    out_of_stock_elems = sel.xpath("//*[@id='outOfStock']")
    if out_of_stock_elems:
        return True
    else:
        return False


def has_no_buybox_in_us_product_page(response):
    sel = Selector(response)
    see_buying_options_button = sel.xpath("//*[@id='buybox-see-all-buying-choices']")
    if see_buying_options_button:
        return True
    else:
        return False
