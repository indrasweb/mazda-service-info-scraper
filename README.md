# Mazda service info scraper

Script to scrape service manuals from http://mazdaserviceinfo.com/

1. Download the script and install dependencies (pip install selenium, brew install chromedriver, pip install PyPDF2)
2. Pay for 24hr access to http://mazdaserviceinfo.com/ [ESI]
3. Replace the `username` and `password` variables with your own credentials
4. Login to the service portal, go to the view-content tab, select the car you want the manual for and click go. This will change your window url. Copy this url set it as `base_url` in the script.
5. `python3 -u scrape.py > out.log &` / `nohup python3 -u scrape.py > out.log &` if running on a server

Downloading a manual takes about 5 hours. The service portal is pretty unreliable, so expect downloads to fail. You should be able to just keep re-running the script and it will keep trying to download any articles it hasn't managed to get yet.

Most manuals will have a few articles that it can’t download at all due to the article being a link to a PDF elsewhere - get these manually (look in articles_to_manually_download.txt after the script terminates).

They rate limit you to one open connection at a time, throwing blank pdf’s in the case that you try to download more than one thing at once, so unfortunately you have to download the articles one by one - no threading :( They also started rate limiting me hard after downloading like 12000 articles during testing, but hopefully no one else encounters this problem.

I think having to pay for the information you need to fix your car from the manufacturer you bought it from is really great so you definitely shouldn’t share any of the manuals you scrape online.
