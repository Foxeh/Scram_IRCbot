from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log


import ConfigParser
import time, sys, string, os

log.startLogging(sys.stdout)

"""
This protocol class contains the necessary protocol for IRC server/client entities

USAGE: Inherit this class and override the implementations as needed
"""

class ScramBotProtocol:
    
    def __init__(self):
        print "Protocol Instantiated. Module is active."
 #
 # Leave this main handler alone!! This defines the protocol!!!
 #       
    def handler(self, bot, msg, channel, user):
        msgParts = msg.split(':')        
        
        if(msgParts[1] == "start"):            
            self.start(bot, msg,channel,user)
            
        if(msgParts[1] == "stop"):
            self.stop(bot,msg,channel,user)
            
        if(msgParts[1] == "restart"):
            self.restart(bot,msg,channel,user)
            
        if(msgParts[1] == "status"):
            self.status(bot,msg,channel,user)
#
# Override the functions below for your specific implementation
#
    def start(self,bot,msg,channel,user):
        print "Got %s from %s in %s"%(msg,user,channel)
        bot.say(msg,channel,user)
        
    def restart(self,bot,msg,channel,user):
        print "Got %s from %s in %s"%(msg,user,channel)
        bot.say(msg,channel,user)
        
    def stop(self,bot,msg,channel,user):
        print "Got %s from %s in %s"%(msg,user,channel)
        bot.say(msg,channel,user)
    
    def status(self,bot,msg,channel,user):
        print "Got %s from %s in %s"%(msg,user,channel)
        bot.say(msg,channel,user)
        
class ScramBot(irc.IRCClient):  
    def __init__(self,subprotocol):
        self.subprotocol =  subprotocol
        
    def setNick(self, nickname):
        """
        Sets our nick
        """
        config = ConfigParser.ConfigParser()
        #TODO: config??
        config.read("settings.ini")
        nickname = config.get('irc', 'nickname')
        irc.IRCClient.setNick(self, nickname)

    def connectionMade(self):
        """
        Connection has started
        """
        irc.IRCClient.connectionMade(self)
        print "Connection Established."
        
    def connectionLost(self, reason):
        """
        Bot lost connection to server
        """
        irc.IRCClient.connectionLost(self, reason)
        print "Connection Lost"

    def signedOn(self):
        """
        Bot signed onto the server                                                                  
        """
        nick = self.nickname
        self.nickChanged(nick)
        self.join(self.factory.channel)
        
    def joined(self, channel):
        """
        This will get called when the bot joins the channel.
        """
        print("[I have joined %s]" %channel)
        
    def nickChanged(self, nick):
        """
        Called when my nick has been changed.
        """
        irc.IRCClient.nickChanged(self,nick)
        print"[New Nick: %s]"%nick
        
    def action(self, user, channel, msg):
        
        user = user.split('!')[0]
        print("* %s %s" % (user,msg))
        
    def privmsg(self, user, channel, msg):        
        origMsg = msg
        user = user.split('!', 1)[0]
        print ("<%s> %s" %(user, msg))
        
        self.subprotocol.handler(self, msg, channel, user)

    def say(self, m, channel, user):
        """
        Command was used.
        """
        self.msg(channel, "%s:%s" %(user,m))    
        
    def alterCollidedNick(self, nickname):
        """
        Changes Nick if current Nick is taken.
        """
        return nickname + '^'
        
    def kickedFrom(self, channel, kicker, message):
        """
        Detects if Bot was kicked from a channel and attempts to rejoin that channel
        """
        print "kicked from: " + channel + "\nKicked by: " + kicker + "\nReason: " + message
        self.join(channel)
        msg = self.nickname + " is not amused."
        self.msg(channel, msg)
        print("[Attempting to rejoin %s]" %channel)
              
class ScramBotFactory(protocol.ClientFactory):              
    def __init__(self, protocol, channel, reactor):             
        self.protocol = protocol
        self.channel = channel
        self.reactor = reactor
        self.bot = None
              
    def buildProtocol(self, addr):
        self.bot = ScramBot(self.protocol)
        self.bot.factory = self
        self.bot.reactor = self.reactor
        return self.bot
    
    def clientConnectionLost(self, connector, reason):              
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):       
        print "Connection Severed: " + reason

class BotC2:    
    def __init__(self, protocol, reactor):
        #TODO: read channel in from global config
        self.factory = ScramBotFactory(protocol, "scrambot", reactor)
        #TODO: read irc server ip from global config
        reactor.connectTCP("192.168.100.126", 6667, self.factory) 
        
if __name__ == '__main__':       
    p = ScramBotProtocol()    
    c = BotC2(p,reactor)
    reactor.run()
    
    
    
    
