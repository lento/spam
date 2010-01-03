import getpass, cookielib, urllib, urllib2


class SPAMClient(object):
    def __init__(self, url):
        self.url = url.rstrip('/')
        
    def login(self, username, password=None):
        """Login in SPAM, and save an access cookie for subsequent commands
        @type  username: string
        @type  password: string
        """
        self.username = username
        if not password:
            password = getpass.getpass()
        credentials = urllib.urlencode(dict(login=username,
                                            password=password,
                                           )
                                      )
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        url = '%s/login_handler?__logins=0&came_from=/' % self.url
        self.opener.open(url, credentials)
    
    def open(self, cmd, data=None):
        """Open a spam url using the builtin opener
        
        You should not use "open" directly, use SPAMClient methods instead
        @type  cmd: string
        @param cmd: Command url without prefix (eg: '/project')
        @type  data: string
        @param data: urlencoded POST data
        """
        #print('%s/%s' % (self.url, cmd.lstrip('/')), data)
        return self.opener.open('%s/%s' % (self.url, cmd.lstrip('/')), data)
    
    def project_new(self, proj, name=None, description=None):
        """Create a new project
        @type  proj: string
        @param proj: Project id (eg: 'dummy')
        @type  name: string
        @param name: Project display name (eg: 'Dummy Returns')
        @type  description: string
        @param description: Project description (eg: 'A test project')
        """
        data = urllib.urlencode(dict(proj=proj,
                                     name=name,
                                     description=description,
                                    ))
        return self.open('/project.json', data)
    
    def scene_new(self, proj, sc, description=None):
        """Create a new scene
        @type  proj: string
        @param proj: Project id (eg: 'dummy')
        @type  sc: string
        @param sc: Scene name (eg: 'sc01')
        @type  description: string
        @param description: Scene description (eg: 'dummy saves the day')
        """
        data = urllib.urlencode(dict(proj=proj,
                                     sc=sc,
                                     description=description,
                                    ))
        return self.open('/scene.json', data)
    
    def shot_new(self, proj, sc, sh, description=None, action=None, frames=0,
                                                    handle_in=0, handle_out=0):
        """Create a new shot
        @type  proj: string
        @param proj: Project id (eg: 'dummy')
        @type  sc: string
        @param sc: Scene name (eg: 'sc01')
        @type  sh: string
        @param sh: Shot name (eg: 'sh01')
        @type  description: string
        @param description: Shot description (eg: "close-up on dummy's smile")
        @type  action: string
        @param action: Shot action (eg: "dummy smiles while saving the day")
        @type  frames: int
        @param frames: Shot lenght in frames
        @type  handle_in: int
        @param handle_in: Handle frames at the start of the shot
        @type  handle_out: int
        @param handle_out: Handle frames at the end of the shot
        """
        data = urllib.urlencode(dict(proj=proj,
                                     sc=sc,
                                     sh=sh,
                                     description=description,
                                     action=action,
                                     frames=frames,
                                     handle_in=handle_in,
                                     handle_out=handle_out,
                                    ))
        return self.open('/shot.json', data)
    
    
    
    
