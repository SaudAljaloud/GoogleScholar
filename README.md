#GoogleScholar
This is a sublime package that provides a facility to interact with Google Scholar without leaving Sublime.

![](https://bytebucket.org/SaudAljaloud/googlescholar/raw/44a003baf428a165cd20daf38b3eff6c7138824d/May-02-2017%2023-11-15.gif)


Install the package from this repo into Sublime, then use the Command Pallette (cmd + shift + P), then search for "GoogleSchoalr". There are two commands: "Search Highlighted" and "Insert your term". Both of them give you a list of the titiles from Google scholar and a list of commands for each paper including: go to, sub-title, number of citation, go to citation, go to related articles, other versions and intergration with [DBLP](https://packagecontrol.io/packages/DBLP).

###Dependencies:
- phantomjs: install by `pip install phantomjs`

- [DBLP](https://packagecontrol.io/packages/DBLP)

I used some other libs which are already included in the lib dir: bs4 and selenium.

This package should be used with Google Scholar access limit in mind. If you got a message with "no results" and you think there should be some, you are most probably have hit the limit!

###TODO:
- [ ] Give a specific message to access limit, different from "No results"
- [ ] Refactor the horrible code of using self.title etc to using a list of dictionary, this will allow to implement a better way of handling "back/forward" feature.
- [ ] Add pagination


###License:

MIT
