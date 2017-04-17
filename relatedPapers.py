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
		self.list_title = []
		self.list_url = []
		self.list_citeByUrl = []
		self.list_relatedArticlesUrl = []
		print("Searching: " + text)
		user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:35.0) Gecko/20100101 Firefox/35.0'
		opener = urllib.request.build_opener()
		
		self.searchGoogleTerm(text)
		self.showtitles()

	def showtitles(self):
		if self.list_title:
			self.view.window().show_quick_panel(self.list_title,self._on_select)
		else:
			sublime.message_dialog("No result!")


	def _on_select(self, idx):
		if idx > -1:
			self.selectedArticle = idx
			self.menuList = ["Open URL", "Go to Citation", "Go to related articles", "Other versions"]
			self.view.window().show_quick_panel(self.menuList,self._on_select_menue)


	def _on_select_menue(self, idx):
		if idx > -1:
			if (idx == 0):
				selected_url = self.list_url[self.selectedArticle]
				webbrowser.open_new(selected_url)
			elif (idx == 1):
				citation_url = self.list_citeByUrl[self.selectedArticle]
				self.list_title = []
				self.list_url = []
				self.list_citeByUrl = []
				self.list_relatedArticlesUrl = []

				self.searchGoogle("https://scholar.google.com" + citation_url)
				self.showtitles()
			elif (idx == 2):
				relatedArticles_url = self.list_relatedArticlesUrl[self.selectedArticle]
				self.list_title = []
				self.list_url = []
				self.list_citeByUrl = []
				self.list_relatedArticlesUrl = []

				self.searchGoogle("https://scholar.google.com" + relatedArticles_url)
				self.showtitles()





	# sparql regex


	
	def searchGoogleTerm(self, search_term):
		query_params = { 'q' : search_term}
		url = "https://scholar.google.com/scholar?hl=en&btnG=&as_sdt=1%2C5&as_sdtp=" + urllib.parse.urlencode(query_params)
		self.searchGoogle(url)

	
	def searchGoogle(self, url):
		fn = os.path.join(os.path.dirname(__file__), 'ScholarExample.html')
		html = codecs.open(fn, 'r', 'utf-8').read()
		# html = self.getHtml(url)
		soup = BeautifulSoup(html, "html.parser")
		div_results = soup.find_all("div", {"class": "gs_ri"})
		if div_results:
			print("div_results: " + str(len(div_results)))
			for articlesDiv in div_results:
				try:
					list_title = articlesDiv.find("h3", {"class" : "gs_rt"}).text.replace("[PDF][PDF]","[PDF]")
					list_url = articlesDiv.find("h3", {"class" : "gs_rt"}).find('a')['href']
					list_citeByUrl = articlesDiv.find("div", {"class" : "gs_fl"}).find_all('a')[0].get('href')
					list_citeByNo = articlesDiv.find("div", {"class" : "gs_fl"}).find_all('a')[0].text
					list_relatedArticlesUrl = articlesDiv.find("div", {"class" : "gs_fl"}).find_all('a')[1].get('href')
					# print("list_title: " + list_title)
					# print("list_url: " + list_url)
					# print("list_citeByUrl: " + list_citeByUrl)
					# print("list_relatedArticlesUrl: " + list_relatedArticlesUrl)
					self.list_title.append("Cited " + re.findall('\d+', list_citeByNo)[0] + ": " + list_title)
					self.list_url.append(list_url)
					self.list_citeByUrl.append(list_citeByUrl)
					self.list_relatedArticlesUrl.append(list_relatedArticlesUrl)
				except:
					pass



	def getHtml(self, url):
		
		self.cjar = MozillaCookieJar()
		self.cjar.load("/Users/user/cookies2.txt",ignore_discard=True)
		opener = urllib.request.build_opener()
		request = urllib.request.Request(url=url, headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Cookie': 'A=sF7U3w:CPTS=1492377836:LM=1492377836:S=60zFToJTBBSlpG5T' })
		handler = opener.open(request)
		html = handler.read()
		return html

	def printTitles(self,url,user_agent, opener):

		request = urllib.request.Request(url="https://scholar.google.com" + url, headers={'User-Agent': 'Mozilla/5.0'})
		handler = opener.open(request)
		htmlPage = handler.read()
		soup = BeautifulSoup(htmlPage, 'html.parser')
		div_results = soup.find_all("div", {"class": "gs_ri"})
		titleList = []
		if div_results != None:
			for articlesDiv in div_results:
				try:
					title = articlesDiv.find("h3", {"class" : "gs_rt"}).find('a').text
					url = articlesDiv.find("h3", {"class" : "gs_rt"}).find('a')['href']
					print(title)
					titleList.append(title)
					self.list_url.append(url)
				except:
					pass
		return titleList


	
	def search(self,search_term, user_agent, opener):

		query_params = { 'q' : search_term}
		url = "https://scholar.google.com/scholar?as_vis=1&hl=en&as_sdt=1,5&" + urllib.parse.urlencode(query_params)
		opener = urllib.request.build_opener()
		request = urllib.request.Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
		handler = opener.open(request)
		html = handler.read()


		# berlin sparql benchmark
		# Create soup for parsing HTML and extracting the relevant information
		soup = BeautifulSoup(html, "html.parser")
		print("Title: " + str(soup.title))
		div_results = soup.find_all("div", {"class": "gs_ri"})
		print("div_results size: " + str(len(div_results)))
		titleList = []
		if div_results:
			print("First Div: " + str(div_results[0]))
			firstArticle = div_results[0].find("div", {"class" : "gs_fl"})
			firstArticleRelatedUrl = firstArticle.find_all('a')[1].get('href')
			print("Related article path: " + str(firstArticleRelatedUrl))
			titleList = self.printTitles(firstArticleRelatedUrl, user_agent, opener)
		else:
			print("Empty!!")
		return titleList



