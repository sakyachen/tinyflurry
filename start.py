import tornado.httpserver   
import tornado.ioloop   
import tornado.options   
import tornado.web   
from tornado.options import define, options
import sys
import operator
import os 

define("port", default=8000, help="run on the given port", type=int)
execfile(sys.path[0]+ '/'+ 'flurry_event_daily.py')
execfile(sys.path[0]+ '/'+ 'flurry_event_summary.py')
execfile(sys.path[0]+ '/'+ 'flurry_metric.py')

# class IndexHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.render("flurry_metric.html",s0='')

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
                                            (r"/", Metric_Handler),
                                            (r"/flurry_event_daily.py", Event_Daily_Handler),
                                            (r"/flurry_event_summary.py", Flurry_Show_Handler),
                                            (r"/flurry_metric.py", Metric_Handler),
                                        ], 
                                        debug=True  
                            )   
    http_server = tornado.httpserver.HTTPServer(app)   
    http_server.listen(options.port)   
    tornado.ioloop.IOLoop.instance().start()