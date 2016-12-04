import os
import cherrypy
import requests
import redis


class NiftyFifty(object):

    @cherrypy.expose
    def index(self):
        return open('index.html')

    @cherrypy.expose
    @cherrypy.tools.accept(media='text/plain')
    def get_data(self):
        self.initialize_db()
        try:
            data = cherrypy.thread_data.db.get('top_gainers')
            if len(data):
                return data
            else:
                return []
        except AttributeError as e:
            self.background_fetch()
            return cherrypy.thread_data.db.get('top_gainers')

    def initialize_db(self):
        try:
            # cherrypy.thread_data.db = redis.StrictRedis(host="localhost", port=6379, db=0)
            cherrypy.log("========================================" + str(os.environ.get("REDIS_URL")))
            cherrypy.thread_data.db = redis.from_url(os.environ.get("REDIS_URL"))
        except redis.ConnectionError as e:
            cherrypy.log('Error connecting the db!')

    def background_fetch(self):
        response = requests.get('https://www.nseindia.com/live_market/dynaContent/live_analysis/gainers/niftyGainers1.json')
        top_gainers = response.text.encode('ascii')

        self.initialize_db()
        cherrypy.thread_data.db.set('top_gainers', top_gainers)
        cherrypy.log(str(cherrypy.thread_data.db.get('top_gainers')))

    def initiate_background_job(self):
        self.background_fetch()


if __name__ == '__main__':
    port = os.environ['PORT']
    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(port),
    })
    cherrypy.process.plugins.Monitor(cherrypy.engine, NiftyFifty().initiate_background_job, frequency=300).subscribe()
    cherrypy.quickstart(NiftyFifty(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
