import flask
from flask import request, jsonify
import os
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
import selenium.webdriver
from scrape_linkedin.ProfileScraper import ProfileScraper
from scrape_linkedin.utils import HEADLESS_OPTIONS
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/api', methods=['GET'])
def api_all():
    if 'url' in request.args:
        url = str(request.args['url'])
    else:
        return "Error: No id field provided. Please specify an url."
    driver=selenium.webdriver.Chrome
    driver_type = Firefox if driver == 'Firefox' else Chrome
    driver_options = HEADLESS_OPTIONS
    with ProfileScraper(driver=driver_type, cookie=os.environ['LI_AT'], driver_options=driver_options) as scraper:
        profile = scraper.scrape(url=url)
        output = profile.to_dict()
        return jsonify(output)

app.run()