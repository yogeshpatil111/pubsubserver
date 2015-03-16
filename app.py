#!/usr/bin/env/python
import web
import json
import pika

class Topic:
    
    def POST(self):
        response = ""
        topic_id = web.ctx.fullpath.rsplit("/",1)[1]

        data = web.data()
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange=topic_id,durable=True,
                                 type='fanout')

        message = data
        channel.basic_publish(exchange=topic_id,
                      routing_key='',
                      body=message)
        connection.close()
                
        web.ctx.status = "200: Publish succeeded."
        
        return response

class User:

    def POST(self):
        response = ""
        topic_id,username = web.ctx.fullpath.rsplit("/",2)[-2:]

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=topic_id,durable=True,
                         type='fanout')

        qname = topic_id + "_" + username

        channel.queue_declare(queue=qname,durable=True)
        connection.close()
        web.ctx.status = "200: Subscription succeeded."
        return response 

    def GET(self):
        response = {}
        topic_id,username = web.ctx.fullpath.rsplit("/",2)[-2:]
        response = ""

        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
        
            qname = topic_id + "_" + username

            channel.queue_bind(exchange=topic_id,
                               queue=qname)

            response = channel.basic_get(queue=qname,no_ack=True)[2]
            if not response:
                web.ctx.status = '204: There are no messages available for this topic on this user.'
            else:
                web.ctx.status = '200: Retrieval succeeded.'
            
            connection.close()
        except:
            web.ctx.status = '404: The subscription does not exist.'
        
        return response


    def DELETE(self):
        response = ""
        topic_id,username = web.ctx.fullpath.rsplit("/",2)[-2:]
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
        
            qname = topic_id + "_" + username

            result = channel.queue_declare(queue=qname,durable=True,passive=True)
            
            try:
                qname = result.method.queue
                channel.queue_delete(queue=qname)
                web.ctx.status = '200: Unsubscribe succeeded.'
            except:
                web.ctx.status = '404: The subscription does not exist.'
        except:
            web.ctx.status = '404: The subscription does not exist.'
        return response


urls = (
     '/[a-zA-Z0-9_]+','Topic',
     '/[a-zA-Z0-9_]+/[a-zA-Z0-9]+','User',
    )


if __name__ == "__main__": 
    app = web.application(urls, globals())
    app.run()
