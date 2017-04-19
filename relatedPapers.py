import sublime, sublime_plugin
import datetime, string
import sys
import urllib.request
import os
import webbrowser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from bs4 import BeautifulSoup
from urllib.request import HTTPCookieProcessor
from http.cookiejar import MozillaCookieJar
import codecs
import re

from selenium import webdriver



# sparql regex
class ProcessTextWithGoogleScholarCommand(sublime_plugin.TextCommand):
	def run(self,edit,entry):
		self.searchGoogleTerm(entry)
		self.showtitles()


	def showtitles(self):
		if self.list_title:
			window = sublime.active_window()
			window.show_quick_panel(self.list_title,self._on_select,sublime.KEEP_OPEN_ON_FOCUS_LOST)
		else:
			sublime.message_dialog("No result!")


	def _on_select(self, idx):
		if idx > -1:
			self.selectedArticle = idx
			selected_url = self.list_url[self.selectedArticle]
			subTitle =  self.list_subtitle[self.selectedArticle]
			self.menuList = ["Open URL: " + selected_url, "Sub-title: " +  subTitle, "Go to Citation", "Go to related articles", "Other versions", "Look up with DBLP", "Back"]
			window = sublime.active_window()
			window.show_quick_panel(self.menuList,self._on_select_menue,sublime.KEEP_OPEN_ON_FOCUS_LOST)

	def emptying(self):
		self.list_title = []
		self.list_url = []
		self.list_citeByUrl = []
		self.list_relatedArticlesUrl = []
		self.list_subtitle = []
		self.list_versionURL = []

	def _on_select_menue(self, idx):
		if idx > -1:
			if (idx == 0):
				selected_url = self.list_url[self.selectedArticle]
				webbrowser.open_new(selected_url)
			elif (idx == 1):
				self.showtitles()
			elif (idx == 2):
				citation_url = self.list_citeByUrl[self.selectedArticle]
				self.emptying()

				self.searchGoogle("https://scholar.google.com" + citation_url)
				self.showtitles()
			elif (idx == 3):
				relatedArticles_url = self.list_relatedArticlesUrl[self.selectedArticle]
				self.emptying()

				self.searchGoogle("https://scholar.google.com" + relatedArticles_url)
				self.showtitles()

			elif (idx == 4):
				versions_url = self.list_versionURL[self.selectedArticle]
				self.emptying()

				self.searchGoogle("https://scholar.google.com" + versions_url)
				self.showtitles()

			elif (idx == 5):
				selected_title = re.sub('Cited [0-9]+: ','',self.list_title[self.selectedArticle])
				selected_title = re.sub(':|-|–',' ',selected_title)
				print("DBLP query: " + selected_title)
				window = sublime.active_window()
				window.active_view().run_command('dblp_insert_citation',{'query':selected_title, 'format': 'bibtex_crossref'})

			elif (idx == 6):
				self.showtitles()

	def searchGoogleTerm(self, search_term):
		self.emptying()
		print("Searching: " + search_term)
		query_params = { 'q' : search_term}
		url = "http://scholar.google.co.uk/scholar?hl=en&" + urllib.parse.urlencode(query_params) + "&btnG=&as_sdt=1%2C5&as_sdtp="
		self.searchGoogle(url)

	
	def searchGoogle(self, url):
		# For debuging with html file
		# fn = os.path.join(os.path.dirname(__file__), 'ScholarExample.html')
		# html = codecs.open(fn, 'r', 'utf-8').read()
		html = self.getHtmlSelPhantomJS(url)
		soup = BeautifulSoup(html, "html.parser")
		div_results = soup.find_all("div", {"class": "gs_ri"})
		if div_results:
			print("div_results: " + str(len(div_results)))
			for articlesDiv in div_results:
				try:
					list_title = articlesDiv.find("h3", {"class" : "gs_rt"}).text.replace("[PDF][PDF]","[PDF]").replace("[HTML][HTML]","[HTML]")
					try:
						list_citeByNo = articlesDiv.find("div", {"class" : "gs_fl"}).find_all('a')[0].text or ["Cited by 0"]
						extractedNumberOfCitation = re.findall('\d+', list_citeByNo)[0] or "0"
					except:
						extractedNumberOfCitation = "0"
					
					
					self.list_title.append("Cited " + extractedNumberOfCitation + ": " + list_title)
					
					try:
						list_url = articlesDiv.find("h3", {"class" : "gs_rt"}).find('a')['href']
						self.list_url.append(list_url)
					except:
						self.list_url.append("#")
					
					try:
						list_citeByUrl = articlesDiv.find("div", {"class" : "gs_fl"}).find_all('a')[0].get('href')
						self.list_citeByUrl.append(list_citeByUrl)
					except:
						self.list_citeByUrl.append("#")
					
					try:
						list_relatedArticlesUrl = articlesDiv.find("div", {"class" : "gs_fl"}).find_all('a')[1].get('href')
						self.list_relatedArticlesUrl.append(list_relatedArticlesUrl)
					except:
						self.list_relatedArticlesUrl.append("#")

					try:
						list_versionURL = articlesDiv.find("div", {"class" : "gs_fl"}).find_all('a')[2].get('href')
						self.list_versionURL.append(list_versionURL)
					except:
						self.list_versionURL.append("#")
					
					try:
						list_subtitle = articlesDiv.find("div", {"class" : "gs_a"}).text
						self.list_subtitle.append(list_subtitle)
					except:
						self.list_subtitle.append("#")


				except:
					pass




	def getHtmlSelPhantomJS(self, url):
	    browser = webdriver.PhantomJS("/usr/local/bin/phantomjs")
	    browser.get(url)
	    html_source = browser.page_source
	    return html_source

	def getHtmlSelFireFox(self, url):
	    browser = webdriver.Firefox()
	    browser.get(url)
	    html_source = browser.page_source
	    return html_source

	def getHtml(self, url):
		
		# self.cjar = MozillaCookieJar()
		# self.cjar.load("/Users/user/cookies2.txt",ignore_discard=True)
		# opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cjar))
		opener = urllib.request.build_opener()
		request = urllib.request.Request(url=url, headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:35.0) Gecko/20100101 Firefox/35.0',
			'Cookie': 'NID=101=Bx9RtLbzsODzLTmDx_iL3WbQobRDGhr794GALapN59pqMSYH0DRVDYHQFH-G6QbGmc3iv2XVqzE6yLfjOu8rck0WTn0Mopf2XTjrxAxhkPe-oc7BUqj69Kjn',
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language':'en-US,en;q=0.5',
			'Accept-Encoding':'gzip, deflate',
			'Referer': 'http://scholar.google.co.uk/',
			'oc7BUqj69KjnlCrsRxDA': 'CONSENT=WP.25f45a; GSP=LM=1492432025:S=JUdcJaFb9V3PdCZ7' })
		handler = opener.open(request)
		html = handler.read()
		return html








class InsertGoogleScholarCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.window = self.view.window()
		prompt = self.window.show_input_panel("Scholar Search:", "", self.on_query, None, None)
	def on_query(self, text):
		if len(text) > 2:
			print("Searching term: " + text)
			window = sublime.active_window()
			window.active_view().run_command('process_text_with_google_scholar',{'entry':text}) 
		else:
			sublime.status_message('DBLP query is too short!')


class GoogleScholarCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for selection in self.view.sel():
			# if the user didn't select anything, search the currently highlighted word
			region = None
			if selection.empty():
				region = self.view.word(selection)
			else:
				region = selection
			text = self.view.substr(region)

		window = sublime.active_window()
		window.active_view().run_command('process_text_with_google_scholar',{'entry':text}) 


		
		




