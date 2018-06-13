# Mazda service info scraper

Script to scrape service manuals from http://mazdaserviceinfo.com/

1. Pay for 24hr access to http://mazdaserviceinfo.com/
2. Download the script and install dependencies (pip install selenium, brew install chromedriver, pip install PyPDF2)
3. Replace the username and password variables with your own credentials
4. Login to the service portal, go to the view-content tab, select the car you want the manual for and click go. This will change your window url. Copy this url set it as `base_url` in the script.
5. python3 -u scrape.py > out.log &

Downloading a manual takes about 5 hours. You have to keep the chrome window visible (focused) for the first 2 mins otherwise it wont expand the menu - this window will then close itself.
After this you can run it in headless mode (uncomment the `options.add_argument('-headless’)` line) on a server if you want, or just leave it running as is.

The service portal is pretty temperamental, so expect downloads to fail. You should be able to just keep re-running the script and it will keep trying to download any articles it hasn't managed to get yet.
Some manuals will have a few articles that it can’t download at all due to the article being a link to a PDF elsewhere - get these manually (look in articles_to_manually_download.txt after the script terminates).

They rate limit you to one open connection at a time, throwing blank pdf’s in the case that you try to download more than one thing at once, so unfortunately you have to download the articles one by one - no threading :(

I think having to pay for the information you need to fix your car from the manufacturer you bought it from is really great and is definitely not a shitbag move at all so you definitely shouldn’t share any of the manuals you scrape online.
