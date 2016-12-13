#!/usr/bin/env python

import os
import re
import sys

#Should remove
KNOWN_TYPES = [
    'id', 'NSObject', 'void', 'char', 'int', 'unsigned', 'double', 'float', 'long', 'bool', 'BOOL', '_Bool',
    'NSAffineTransform','NSAppleEventDescriptor','NSAppleEventManager','NSAppleScript',
    'NSArchiver','NSArray','NSAssertionHandler','NSAttributedString','NSAutoreleasePool',
    'NSBlockOperation','NSBundle','NSCache','NSCachedURLResponse','NSCalendar','NSCharacterSet',
    'NSClassDescription','NSCloneCommand','NSCloseCommand','NSCoder','NSComparisonPredicate',
    'NSCompoundPredicate','NSCondition','NSConditionLock','NSConnection','NSCountCommand',
    'NSCountedSet','NSCreateCommand','NSData','NSDataDetector','NSDate','NSDateComponents',
    'NSDateFormatter','NSDecimalNumber','NSDecimalNumberHandler','NSDeleteCommand','NSDictionary',
    'NSDirectoryEnumerator','NSDistantObject','NSDistantObjectRequest','NSDistributedLock',
    'NSDistributedNotificationCenter','NSEnumerator','NSError','NSException','NSExistsCommand',
    'NSExpression','NSFileCoordinator','NSFileHandle','NSFileManager','NSFileVersion','NSFileWrapper',
    'NSFormatter','NSGarbageCollector','NSGetCommand','NSHashTable','NSHost','NSHTTPCookie',
    'NSHTTPCookieStorage','NSHTTPURLResponse','NSIndexPath','NSIndexSet','NSIndexSpecifier','NSInputStream',
    'NSInvocation','NSInvocationOperation','NSKeyedArchiver','NSKeyedUnarchiver','NSLinguisticTagger',
    'NSLocale','NSLock','NSLogicalTest','NSMachBootstrapServer','NSMachPort','NSMapTable','NSMessagePort',
    'NSMessagePortNameServer','NSMetadataItem','NSMetadataQuery','NSMetadataQueryAttributeValueTuple',
    'NSMetadataQueryResultGroup','NSMethodSignature','NSMiddleSpecifier','NSMoveCommand','NSMutableArray',
    'NSMutableAttributedString','NSMutableCharacterSet','NSMutableData','NSMutableDictionary',
    'NSMutableIndexSet','NSMutableOrderedSet','NSMutableSet','NSMutableString','NSMutableURLRequest',
    'NSNameSpecifier','NSNetService','NSNetServiceBrowser','NSNotification','NSNotificationCenter',
    'NSNotificationQueue','NSNull','NSNumber','NSNumberFormatter','NSObject','NSOperation','NSOperationQueue',
    'NSOrderedSet','NSOrthography','NSOutputStream','NSPipe','NSPointerArray','NSPointerFunctions','NSPort',
    'NSPortCoder','NSPortMessage','NSPortNameServer','NSPositionalSpecifier','NSPredicate','NSProcessInfo',
    'NSPropertyListSerialization','NSPropertySpecifier','NSProtocolChecker','NSProxy','NSQuitCommand',
    'NSRandomSpecifier','NSRangeSpecifier','NSRecursiveLock','NSRegularExpression','NSRelativeSpecifier',
    'NSRunLoop','NSScanner','NSScriptClassDescription','NSScriptCoercionHandler','NSScriptCommand',
    'NSScriptCommandDescription','NSScriptExecutionContext','NSScriptObjectSpecifier','NSScriptSuiteRegistry',
    'NSScriptWhoseTest','NSSet','NSSetCommand','NSSocketPort','NSSocketPortNameServer','NSSortDescriptor',
    'NSSpecifierTest','NSSpellServer','NSStream','NSString','NSTask','NSTextCheckingResult','NSThread',
    'NSTimer','NSTimeZone','NSUbiquitousKeyValueStore','NSUnarchiver','NSUndoManager','NSUniqueIDSpecifier',
    'NSURL','NSURLAuthenticationChallenge','NSURLCache','NSURLConnection','NSURLCredential','NSURLCredentialStorage',
    'NSURLDownload','NSURLHandle','NSURLProtectionSpace','NSURLProtocol','NSURLRequest','NSURLResponse',
    'NSUserAppleScriptTask','NSUserAutomatorTask','NSUserDefaults','NSUserNotification','NSUserNotificationCenter',
    'NSUserScriptTask','NSUserUnixTask','NSUUID','NSValue','NSValueTransformer','NSWhoseSpecifier','NSXMLDocument',
    'NSXMLDTD','NSXMLDTDNode','NSXMLElement','NSXMLNode','NSXMLParser','NSXPCConnection','NSXPCInterface',
    'NSXPCListener','NSXPCListenerEndpoint','NSCoding','NSComparisonMethods','NSConnectionDelegate','NSCopying',
    'NSDecimalNumberBehaviors','NSErrorRecoveryAttempting','NSFastEnumeration','NSFileManagerDelegate',
    'NSFilePresenter','NSKeyedArchiverDelegate','NSKeyedUnarchiverDelegate','NSKeyValueCoding','NSKeyValueObserving',
    'NSLocking','NSMachPortDelegate','NSMetadataQueryDelegate','NSMutableCopying','NSNetServiceBrowserDelegate',
    'NSNetServiceDelegate', 'NSPortDelegate','NSScriptingComparisonMethods','NSScriptKeyValueCoding',
    'NSScriptObjectSpecifiers','NSSecureCoding','NSSpellServerDelegate','NSStreamDelegate',
    'NSURLAuthenticationChallengeSender','NSURLConnectionDataDelegate','NSURLConnectionDelegate',
    'NSURLConnectionDelegate','NSURLHandleClient','NSURLProtocolClient','NSUserNotificationCenterDelegate',
    'NSXMLParserDelegate','NSXPCListenerDelegate','NSXPCProxyCreating',
]

UNKNOWN_TYPE = "CDUnknownBlockType"

def map_format_specifier(type):
    if type == "int":
        return "%d"
    if type in ["BOOL", "_Bool", "bool"]:
        return "%u"
    else:
        return "%@"

class ObjcMethod():
    def __init__(self, line, interface):
        self.line = line.replace(UNKNOWN_TYPE, 'id')
        self.ret_type = self.get_ret_type()
        self.interface = interface
        self.name = self.get_name()
        self.full_name = "[%s %s]" %(interface, self.name)

    def get_name(self):
        splits = self.line.split(')')
        splits = splits[1].split(':')
        splits = splits[0].split(';')
        name = splits[0]
        return name

    def get_ret_type(self):
        splits = self.line[3:].split(')', 1)
        ret_type = splits[0]
        if ret_type is not UNKNOWN_TYPE:
            return ret_type
        return "id"

    def hook(self):
        if self.ret_type == "void":
            print '%s {[logTool logDataFromNSString:@">>>> BEGIN - %s"];%%orig;[logTool logDataFromNSString:@"<<<< END - %s"]; }' %(self.line[:-2], self.full_name, self.full_name)
        else:
            print '%s {[logTool logDataFromNSString:@">>>> BEGIN - %s"];%s ret = %%orig;[logTool logDataFromNSString:[NSString stringWithFormat:@"ret value: %s", ret]];[logTool logDataFromNSString:@"<<<< END - %s"];return ret; }' %(self.line[:-2], self.full_name, self.ret_type, map_format_specifier(self.ret_type), self.full_name)



class HeaderParser():
    def __init__(self, filepath):
        self.file = open(filepath)
        self.lines = self.file.readlines()
        self.interface = self.get_interface_name()
        self.methods = self.get_methods()

    def get_interface_name(self):
        for line in self.lines:
            if "@interface" in line:
                splits = line.split(' ')
                return splits[1]

    def get_methods(self):
        methods = []
        for line in self.lines:
            if "- (" == line[:3] or "+ (" == line[:3]:
                method = ObjcMethod(line, self.interface)
                methods.append(method)
        return methods

def main(args):
    filepath = args[1]
    parser = HeaderParser(filepath)
    print "%hook", parser.interface
    for method in parser.methods:
        method.hook()
    print "%end"


main(sys.argv)
