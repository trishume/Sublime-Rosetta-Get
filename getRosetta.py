import sublime, sublime_plugin, urllib, xml.dom.minidom, re

class GetRosettaCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        self.window = window

    @staticmethod
    def getLang(scope_string):
        scopes = scope_string.split(" ")
        lang = scopes[0].split(".")[1]
        return lang.capitalize()

    
    @staticmethod
    def getCode(lang,task):
        t = task.replace(" ", "_")
        y = urllib.urlopen("http://rosettacode.org/w/index.php?title=%s&action=raw" % t.encode('utf-8'))
        page = y.read()
        result = re.search("<lang %s>([\s\S]*?)</lang>" % lang, page,re.I)
        if not result:
            return None
        else:
            return result.group(1)
    
    @staticmethod
    def getTasksForLang(lang):
        name = "http://rosettacode.org/mw/api.php?action=query&list=categorymembers&cmtitle=Category:%s&cmlimit=500&format=xml" % urllib.quote(lang)
        print name
        cmcontinue, titles = '', []
        while True:
            u = urllib.urlopen(name + cmcontinue)
            xmldata = u.read()
            u.close()
            if xmldata.find("cm") == -1: # language doesn't exist
                return None
            x = xml.dom.minidom.parseString(xmldata)
            titles += [i.getAttribute("title") for i in x.getElementsByTagName("cm")]
            cmcontinue = filter( None,
                                 (urllib.quote(i.getAttribute("cmcontinue"))
                                  for i in x.getElementsByTagName("categorymembers")) )
            if cmcontinue:
                cmcontinue = '&cmcontinue=' + cmcontinue[0]
            else:
                break
        return titles

    def run(self):
        self.view = self.window.active_view()
        self.lang = self.getLang(self.view.scope_name(0).strip())
        print self.lang
        self.task_list = self.getTasksForLang(self.lang)
        if not self.task_list:
            sublime.error_message(__name__ + ': Can\'t find tasks for language ' + self.lang + ' on Rosetta Code.')
            return
        self.window.show_quick_panel(self.task_list, self.on_done)

    def on_done(self, picked):
        if picked == -1:
            return
        task = self.task_list[picked]
        prog = self.getCode(self.lang,task)
        if not prog:
            sublime.error_message(__name__ + ': Can not get task ' + task)
            return

        edit = self.view.begin_edit()
        self.view.insert(edit,self.view.sel()[0].begin(),prog)
        self.view.end_edit(edit)
