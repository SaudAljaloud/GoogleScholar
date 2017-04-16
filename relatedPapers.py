import sublime, sublime_plugin
import datetime, string
import sys
import urllib.request
import os
import webbrowser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from bs4 import BeautifulSoup

class ExampleCommand(sublime_plugin.TextCommand):
	
	
	def run(self, edit):
		for selection in self.view.sel():
			# if the user didn't select anything, search the currently highlighted word
			region = None
			if selection.empty():
				region = self.view.word(selection)
			else:
				region = selection
			text = self.view.substr(region)
		self.list_url = []
		print("Searching: " + text)
		user_agent = 'Mozilla/20.0.1 (compatible; MSIE 5.5; Windows NT)'
		opener = urllib.request.build_opener()
		self.list_title = self.search(text, user_agent, opener)
		print("self.listLegth: " + str(len(self.list_url)))
		if self.list_title:
			self.view.window().show_quick_panel(self.list_title,self._on_select,1,2)

	# sparql regex
	def _on_select(self, idx):
			if idx > -1:
				selected_url = self.list_url[idx]
				# sublime.message_dialog(selected)
				webbrowser.open_new(selected_url)

	
	
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



